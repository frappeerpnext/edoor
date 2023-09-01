from datetime import datetime
import json
from edoor.edoor.doctype.reservation_stay.reservation_stay import change_room_occupy, generate_room_rate
from py_linq import Enumerable
import re
from edoor.api.frontdesk import get_working_day
from edoor.api.utils import get_date_range, update_reservation_folio, update_reservation_stay,update_reservation,add_room_charge_to_folio,get_master_folio,create_folio
import frappe
from frappe.utils.data import add_to_date, getdate
from frappe import _

@frappe.whitelist()
def test():
    data = frappe.db.get_all("Account Code", filters={"parent_account_code":"1000"}, order_by='lft')
    return data 

@frappe.whitelist()
def get_reservation_detail(name):
    reservation= frappe.get_doc("Reservation",name)
    reservation_stays = frappe.get_list("Reservation Stay",filters={'reservation': name},fields=['name','rooms_data','require_drop_off','require_pickup','room_type_alias','is_active_reservation','rate_type','guest','total_credit','balance','total_debit','total_room_rate','reservation_status','status_color','guest_name','pax','child','adult','adr', 'reference_number','arrival_date','arrival_time','departure_date','departure_time','room_types','rooms',"is_master","paid_by_master_room","allow_post_to_city_ledger"])
    master_guest = frappe.get_doc("Customer",reservation.guest)
    return {
        "reservation":reservation,
        "reservation_stays":reservation_stays,
        "master_guest": master_guest
    }


@frappe.whitelist()
def get_reservation_stay_detail(name):
    reservation_stay= frappe.get_doc("Reservation Stay",name)
    
    reservation = frappe.get_doc("Reservation",reservation_stay.reservation)
    total_reservation_stay = frappe.db.count("Reservation Stay", {'reservation': reservation.name})
    guest=frappe.get_doc("Customer",reservation_stay.guest)

    reservation_stay_names =frappe.get_all("Reservation Stay",filters={"reservation":reservation_stay.reservation},order_by="name", page_length=10000,pluck='name')
    

    master_guest = guest
    if reservation.guest != reservation_stay.guest:
        master_guest = frappe.get_doc("Customer",reservation.guest)

    
    return {
        "reservation":reservation,
        "total_reservation_stay": total_reservation_stay,
        "reservation_stay":reservation_stay,
        "guest":guest,
        "master_guest":master_guest,
        "reservation_stay_names":reservation_stay_names
    }


@frappe.whitelist()
def get_folio_summary_by_transaction_type(transaction_type, transaction_number):
     

    sql = """
        select 
            account_category,
            account_category_sort_order, 
            sum(amount * if(type='Debit',1,-1)) as amount 
        from `tabFolio Transaction` 
        where 
            transaction_type = '{}' and 
            transaction_number = '{}'
        group by 
            account_category 
        order by account_category_sort_order
     """.format(
        transaction_type,
        transaction_number
    )
   

    return frappe.db.sql(sql, as_dict=1)


@frappe.whitelist()
def get_reservation_charge_summary(reservation = None, reservation_stay = None,folio_number = None):
    search_field = "reservation"
    search_value = reservation
    if reservation_stay:
        search_field = "reservation_stay"
        search_value = reservation_stay
    elif folio_number:
        search_field = "folio_number"
        search_value = folio_number


    sql = """
        select 
            account_category,
            account_category_sort_order, 
            sum(amount * if(type='Debit',1,-1)) as amount 
        from `tabFolio Transaction` 
        where 
            {} = '{}' and 
            transaction_type='Reservation Folio'
        group by 
            account_category 
        order by account_category_sort_order 
     """.format(
        search_field,
        search_value
    )
  

    return frappe.db.sql(sql, as_dict=1)

@frappe.whitelist()
def get_folio_detail(name):
    
    doc = frappe.get_doc("Folio Transaction",name)
    account_code = frappe.get_doc("Account Code", doc.account_code)
    return {"doc":doc, "account_code": account_code}

@frappe.whitelist()
def check_room_availability(property,room_type_id=None,start_date=None,end_date=None,exception=None):
    working_day = get_working_day(property)
    end_date = add_to_date(end_date,days=-1)
    sql_except = ''
    if not room_type_id:
        room_type_id = ''
    if exception:
        exception = json.loads(exception)
        sql_except = "and {0} != '{1}'".format(exception['field'], exception['value'])

    sql = """
        select 
            distinct
            room_type_id,
            room_type,
            name,
            room_number
        from `tabRoom` 
        where 
            property = '{0}' and 
            room_type_id = if('{1}'='', room_type_id, '{1}') and
            name not in (
                select 
                    distinct
                    coalesce(room_id,'') 
                from `tabTemp Room Occupy` 
                where
                    date between '{2}' and '{3}' {4}
            )   
    """
    #check if arrival date is equal to current system date then check room availabityy is check with house keeping status
    # concat where condition with show_in_room_availability = 1
    if str(start_date) == str(working_day["date_working_day"]):
        sql = "{} and coalesce(show_in_room_availability,0)  = 1".format(sql)

    sql = sql.format(property,room_type_id,start_date, end_date,sql_except)
    data = frappe.db.sql(sql,as_dict=1)
    return data

@frappe.whitelist()
def check_room_type_availability(property,start_date=None,end_date=None,rate_type=None, business_source=None, room_type_id=None):
    end_date = add_to_date(end_date,days=-1)
    #get all room type and total room 
    sql_room_type = "select room_type_id as name, room_type, count(name) as total_room, 0 as occupy from `tabRoom` where disabled = 0 and property='{}'  group by room_type_id,room_type".format(property)
    if room_type_id:
        sql_room_type = "select room_type_id as name, room_type, count(name) as total_room, 0 as occupy from `tabRoom` where disabled = 0 and property='{}' and room_type_id = '{}'  group by room_type_id,room_type".format(property,room_type_id)
    
    room_type = frappe.db.sql(sql_room_type,as_dict=1)

    for t in room_type:
        #get total room occupy from temp room occupy 
        #we count stay_room_id because some reervation stay is not yet assign room
        sql = "select count(room_type_id) as total_room from `tabTemp Room Occupy` where room_type_id = '{}' and date between '{}' and '{}' group by date order by count(room_type_id) desc limit 1".format(t["name"],start_date,end_date)
        room_type_occupy = frappe.db.sql(sql,as_dict=1)
  
        if room_type_occupy:
            t["occupy"] = room_type_occupy[0]["total_room"]
        else:
            t["occupy"] = 0

        t["total_vacant_room"] = (t["total_room"] or 0) - ( t["occupy"] or 0)
    
        t["rate"] = get_room_rate(property, rate_type, t["name"], business_source, start_date)
        t["new_rate"] = t["rate"]

    #return  [d for d in room_type if ((d['total_room'] or 0) - (d["occupy"] or 0) > 0)]

    return  room_type


@frappe.whitelist()
def check_room_occupy(property,room_type_id, room_id, start_date=None, end_date=None, reservation_stay=None):
    end_date = add_to_date(end_date,days=-1)
    except_stay = ""
    if reservation_stay:
        except_stay = " AND coalesce(reservation_stay,'') <> '{}'".format(reservation_stay)
    sql = "SELECT COUNT(name) AS total FROM `tabTemp Room Occupy` WHERE property='{4}' AND room_id = '{0}' AND room_type_id = '{5}' AND DATE BETWEEN '{1}' AND '{2}'{3}".format(room_id,start_date,end_date,except_stay,property,room_type_id)
    room_occupy = frappe.db.sql(sql)
    return room_occupy[0][0]


@frappe.whitelist(methods="POST")
def add_new_reservation(doc):
    #for group booking stay can be 0 
    if len(doc["reservation_stay"]) == 0:
        frappe.throw("Please select room to add reservation")


    arrival_date = doc["reservation"]["arrival_date"]
    working_day = get_working_day(doc["reservation"]["property"])
    
    if not working_day["cashier_shift"]:
        frappe.throw("Please start cashier shift first") 

 
    if frappe.utils.getdate(arrival_date) < working_day["date_working_day"]:
        
        if str(frappe.db.get_default("allow_user_to_add_back_date_transaction")) =="1":
           
            backdate_role = frappe.db.get_default("role_for_back_date_transaction")
            
            if backdate_role:
                
                if not backdate_role in frappe.get_roles(frappe.session.user):
                    frappe.throw("You don't have permission to add back date reservation")
            else:
                frappe.throw("You can not add reservation to past date")
        else:
            frappe.throw("You can not add reservation to past date")


    
    #validate stay with room number duplicate 
    room_ids = [d["room_id"] for d in doc["reservation_stay"] if (d["room_id"] or '')!=""]
    if len(room_ids) != len(set(room_ids)):
        frappe.throw("You cannot select duplicate room number")

    #check room avaliability
    validate_room_type_availability(doc )
    

    
    #check if not have guest selected then create new guest
    if not check_field(doc["reservation"],"guest"):
        
        guest = frappe.get_doc(doc["guest_info"]).insert()
      
        doc["reservation"]["guest"] = guest.name
    else:
        guest = frappe.get_doc(doc["guest_info"]).save()
    
    #prevent code call on_pdate to reservation stay
    reservation = frappe.get_doc(doc["reservation"]).insert()
    
    #start insert insert reservation stay
    i = 0
    stay_names = []
    # set first stay as master room 
    doc["reservation_stay"][0]["is_master"] = 1
    #check if reservation is automatically assign room
    available_rooms = []
    if 'auto_assign_room' in doc.keys():
        if doc["auto_assign_room"]:
            #get room available list then assign to each stay
            available_rooms = check_room_availability(
                property=reservation.property, 
                    start_date=reservation.arrival_date,
                    end_date=reservation.departure_date,
            )


    for   d in doc["reservation_stay"]:
        room = None

        if   'room_id' in d.keys():
            room = d["room_id"]
            #checi if room is not available
            if d["room_id"]:
                check_room_not_available = frappe.db.sql("select name from `tabTemp Room Occupy` where room_id='{}' and date between '{}' and '{}'".format(room, reservation.arrival_date, add_to_date(getdate(reservation.departure_date), days=-1)),as_dict=1)
                if check_room_not_available:
                    frappe.throw("Room {} is not available".format(frappe.db.get_value("Room",room,"room_number")))
        
        if not room and len(available_rooms)>0:
            
            if len(available_rooms)> 0:
                room_by_room_types = list(filter(lambda x: x['room_type_id'] == d["room_type_id"], available_rooms))
                if len(room_by_room_types)>0:
                    room = room_by_room_types[0]["name"]
                    available_rooms.remove(room_by_room_types[0])

                            
   
        stay = {
            "doctype":"Reservation Stay",
            "update_reservation":False,
            "reservation":reservation.name,
            "reservation_status":"Reserved" if (room or '') !='' else "Confirmed",
            "arrival_time":reservation.arrival_time,
            "departure_time":reservation.departure_time,
            "note":reservation.note,
            "tax_rule":reservation.tax_rule,
            "rate_include_tax":reservation.rate_include_tax or "No",
            "tax_1_rate":reservation.tax_1_rate or 0,
            "tax_2_rate":reservation.tax_2_rate or 0,
            "tax_3_rate":reservation.tax_3_rate or 0,
            "paid_by_master_room":doc["reservation"]["paid_by_master_room"],
            "allow_post_to_city_ledger":doc["reservation"]["allow_post_to_city_ledger"],
            "is_master":d["is_master"],
            "group_code":reservation.group_code,
            "group_name":reservation.group_name,
            "adult":d["adult"],
            "child":d["child"],
            "stays":[
                {
                    "doctype":"Reservation Stay Room",
                    "room_type_id": d["room_type_id"],
                    "room_id":room,
                    "input_rate":d["rate"] or 0,
                    "guest":reservation.guest,
                    "reservation_status":"Reserved" if (room or '') !='' else "Confirmed",
                    
                    "start_date":reservation.arrival_date,
                    "end_date":reservation.departure_date,
                    "start_time":reservation.arrival_time,
                    "end_time":reservation.departure_time,

                    "is_manual_rate":d["is_manual_rate"]
                }
            ]
        }
        
        stay_doc = frappe.get_doc(stay).insert()
        stay_names.append(stay_doc.name)

        

    #update summary to reservation stay
    for s in stay_names:
        update_reservation_stay(s, run_commit=False)

    #udpate summary to reservation 
    update_reservation(name=reservation.name, run_commit= False)
 
    frappe.db.commit()
    frappe.msgprint("Add new reservation successfully")
    return reservation

def validate_room_type_availability(doc):
    room_type_ids = set([d["room_type_id"] for d in doc["reservation_stay"]])
    for rt in room_type_ids:
       
        total_rooms = len( [d["room_type_id"] for d in doc["reservation_stay"] if d["room_type_id"] == rt])
        available_room = check_room_type_availability(
                    property=doc["reservation"]["property"],
                    room_type_id=rt,
                    start_date=doc["reservation"]["arrival_date"],
                    end_date=doc["reservation"]["departure_date"],
                )
         
        vacant_room = available_room[0]["total_vacant_room"]

        if total_rooms>vacant_room:
            frappe.throw("You don't have enought room for room type {}. Room available {}, but you book {}".format(available_room[0]["room_type"], 0 if vacant_room< 0 else vacant_room, total_rooms))
        
        

@frappe.whitelist(methods="POST")
def stay_add_more_rooms(reservation=None, data=None):
    reservation = frappe.get_doc("Reservation", reservation)
    
    for d in data:
         
        if d['departure_date'] <= d['arrival_date']:
            frappe.throw("Departure date cannot less than or equal to arrival date")
        stay = {
            "doctype":"Reservation Stay",
            "reservation":reservation.name,
            "reservation_status":"Reserved" if ((d["room_id"] or None) if 'room_id' in d else None)  else "Confirmed",

            "arrival_time":reservation.arrival_time,
            "departure_time":reservation.departure_time,
            "note":reservation.note,
            "child":d["child"],
            "adult":d["adult"],
            "stays": [{
                "room_type_id": d["room_type_id"],
                "room_id": d["room_id"] or None if 'room_id' in d else None,
                "input_rate":d["rate"] or 0,
                "guest":reservation.guest,
                "reservation_status":"Reserved",
                "start_date":d["arrival_date"],
                "end_date":d["departure_date"],
                "child":d["child"],
                "adult":d["adult"],
                "start_time":reservation.arrival_time,
                "end_time":reservation.departure_time,
                "is_manual_rate":d["is_manual_rate"]
            }]
        }
        frappe.get_doc(stay).insert()
        frappe.enqueue("edoor.api.utils.update_reservation", queue='short', name=reservation.name, doc=None, run_commit=True)

    frappe.db.commit()
    return reservation
@frappe.whitelist(methods="POST")
def check_in(reservation,reservation_stays=None,is_undo = False):
    #reservation_stays is array
    #reservation_stays is apply then we skip check reservation 
    #validate user permission check if user have role in check in role in edoor setting
    #validate with working day and cashier shift
    #validate room if still have guest inhouse
    #validate with room is already assign room 
    #after check in check if no folio then create 1 and mark as master
    #add room charge to folio transaction
    #check master room is already check in
    #update check date and check in by in to reservation stay


    check_in_role = frappe.db.get_default("check_in_role")
 
    if not check_in_role in frappe.get_roles(frappe.session.user):
        frappe.throw(frappe._("You don't have permission to perform this action"))
    
    
    doc = frappe.get_doc("Reservation",reservation)
    working_day = get_working_day(doc.property)
   
    if not working_day["cashier_shift"]:
        frappe.throw("There is no cashier shift open. Please open cashier shift first")   

    if not reservation:
        frappe.throw("There is no reservation to check in")

    if reservation_stays:
        stays = reservation_stays
    else:
        stays = frappe.get_list("Reservation Stay",filters={"reservation":reservation},limit=100) # limit 100 to prevent reservation that have more than 20 stay

    #check if master room is already check in
    if not is_master_room_check_in(doc.name,reservation_stays):
        frappe.throw("Please check in master room first")

    housekeeping_status =  frappe.db.get_default("housekeeping_status_after_check_in")

    for s in stays:
        stay = frappe.get_doc("Reservation Stay", s)
        #check if stay is not assign room then alert to user to asign room first
        if Enumerable(stay.stays).where(lambda x: (x.room_id or "") =="").count()>=1:
            frappe.throw("Please asign room to reservation stay #{}.".format(s))

        if stay.reservation_status in("In-house","Void","Cancelled","Checked In","Checked Out") and not is_undo:
            frappe.throw("Stay # {}. Room {}. This room is already {}.".format(stay.name, stay.rooms,stay.reservation_status.lower()))
        if is_undo and not stay.reservation_status in("In-house","Checked In"):
            frappe.throw("Stay # {}. Room {}. This room is {}.".format(stay.name, stay.rooms,stay.reservation_status.lower()))
      
        if frappe.utils.getdate(stay.arrival_date) > working_day["date_working_day"]:
            frappe.throw("Stay # {}. Room {}. Arrival date must be equal to current date.".format(stay.name, stay.rooms))
        
        if stay.reservation_status =="No Show":
            if stay.is_active_reservation == 1:
                frappe.throw("You cannot Check In  No Show reservation # {}. Because this reservation don't have a reserve room.".format(stay.name))
                

        #validate check if current room is still have guest in house

        room_id = stay.stays[0].room_id
        check_room_in_house = frappe.db.sql("select name from `tabReservation Stay Room` where parent!='{}' and room_id='{}' and end_date='{}' and reservation_status='In-house'".format(stay.name,room_id, stay.arrival_date),as_dict=1)
        if check_room_in_house:
             frappe.throw("Stay # {}, Room {} still have guest In-house.".format(stay.name, stay.stays[0].room_number))

 

        stay.reservation_status = "In-house" if not is_undo else "Confirmed"
        stay.checked_in_by = frappe.session.user
        stay.checked_in_date = frappe.utils.now()
        stay.save()

        

        #update room housekeeing status to occupy clean
        room_id = stay.stays[0].room_id
        room = frappe.get_doc("Room",room_id)
        room.housekeeping_status = housekeeping_status
        room.reservation_stay = stay.name
        room.save()
        
        #create folio 
        master_folio = {}
        if stay.is_master:
            
            #check if folio is not create yet
            master_folios = frappe.db.get_list("Reservation Folio",{"reservation_stay":stay.name,"is_master":1})
            folio = None
            if len(master_folios) == 0:
                folio =create_folio(stay)
            else:
                folio = frappe.get_doc("Reservation Folio",master_folios[0].name)
                folio.status="Open"
                folio.save()
                
            if folio:
                #get first rate from reservation room rate
                
                room_rates = frappe.db.get_list("Reservation Room Rate",fields=["*"], filters={"reservation_stay":stay.name,"date":["<=",working_day["date_working_day"]]},order_by="date desc",page_length=1)
                if (room_rates):
                    for r  in room_rates:
                        add_room_charge_to_folio(folio,r )
                else:
                    frappe.throw("Stay # {}, Room {} does not have room rate".format(stay.name, stay.rooms))
                
            #Fine all other stay that that mark as paid_by_master_room then enter folio transaction master folio
            other_stays = frappe.db.sql("select name  from `tabReservation Stay` where name !='{}' and reservation='{}' and paid_by_master_room=1 and reservation_status = 'In-house'".format(stay.name, stay.reservation),as_dict=1)
            if other_stays:
                for os in other_stays:
                    #get first rate from reservation room rate
                    room_rates = frappe.db.get_list("Reservation Room Rate",fields=["*"], filters={"reservation_stay":os['name'],"date":["<=",working_day["date_working_day"]]},order_by="date",page_length=1)
                    if (room_rates):
                        for r  in room_rates:
                            add_room_charge_to_folio(folio,r )
                    else:
                        frappe.throw("Stay # {} does not have room rate".format(os['name']))

        else:

            if not stay.paid_by_master_room:
                # if stay have master folio
                master_folios = frappe.db.get_list("Reservation Folio",{"reservation_stay":stay.name,"is_master":1})
                folio = None
                if len(master_folios)==0:
                    folio = create_folio(stay)
                else:
                    folio = frappe.get_doc("Reservation Folio",master_folios[0].name)
                    
                if folio:
                    #get first rate from reservation room rate
                    room_rates = frappe.db.get_list("Reservation Room Rate",fields=["*"], filters={"reservation_stay":stay.name,"date":["<=",working_day["date_working_day"]]},order_by="date",page_length=1000)
                    if (room_rates):
                        for r in room_rates:
                            add_room_charge_to_folio(folio,r )
                    else:
                        frappe.throw("Stay # {}, Room {} does not have room rate".format(stay.name, stay.rooms))
            else:
                #add room rate to folio of master room
                master_folio = get_master_folio(reservation)
                if master_folio:
                    room_rates = frappe.db.get_list("Reservation Room Rate",fields=["*"], filters={"reservation_stay":stay.name,"date":["<=",working_day["date_working_day"]]},order_by="date",page_length=1000)
                    if (room_rates):
                        for r in room_rates:
                            add_room_charge_to_folio(master_folio,r )
                    else:
                        frappe.throw("Stay # {}, Room {} does not have room rate".format(stay.name, stay.rooms))


 
    frappe.db.commit()
    return {
        "reservation":doc
    }

@frappe.whitelist(methods="POST")
def undo_check_in(reservation_stay):
    #validate status and date
    #validate working day in doc method
    #validate user role from edoor setting role
    #delete all auto post under current stay folio

    role = frappe.db.get_default("undo_check_in_role")
 
    if not role in frappe.get_roles(frappe.session.user):
        frappe.throw(frappe._("You don't have permission to perform this action"))

    doc = frappe.get_doc("Reservation Stay", reservation_stay)
    working_day = get_working_day(doc.property)
   
    if not working_day["cashier_shift"]:
        frappe.throw("There is no cashier shift open. Please open cashier shift first")   

    
    doc.reservation_status = 'Reserved'
    doc.checked_in_by = None
    doc.checked_in_date = None
    doc.save()
 
    #update housekeeping status to room
    room_id = doc.stays[0].room_id
    room = frappe.get_doc("Room",room_id)
    room.housekeeping_status = frappe.db.get_default("housekeeping_status_after_undo_check_in")
    room.reservation_stay = None
    room.save()
    

    #delete auto post transaction
    folio_numbers = frappe.db.sql("select distinct transaction_number from `tabFolio Transaction` where reservation_stay = '{}' and is_auto_post=1 and transaction_type='Reservation Folio'".format(reservation_stay),as_dict=1)
    frappe.db.delete("Folio Transaction", {"reservation_stay":doc.name, "is_auto_post":1})

    if folio_numbers:
        for f in folio_numbers:           
            update_reservation_folio(f["transaction_number"], None, run_commit=False)

    frappe.enqueue("edoor.api.utils.update_reservation_stay", queue='short', name=reservation_stay, doc=None, run_commit=True)
    frappe.enqueue("edoor.api.utils.update_reservation", queue='short', name=doc.reservation, doc=None, run_commit=True)



    return doc








def is_master_room_check_in(reservation,reservation_stays):

    for s in reservation_stays:
        if frappe.db.get_value("Reservation Stay",s,"is_master")==1:
            return True
        else:
            if frappe.db.get_value("Reservation Stay",s,"paid_by_master_room") ==1:
                return frappe.db.exists("Reservation Stay", {"reservation":reservation, "is_master":1,"reservation_status":"In-house"})
    
    return True 


@frappe.whitelist(methods="POST")
def mark_as_master_folio(reservation,reservation_stay):
    doc = frappe.get_doc("Reservation Stay",reservation_stay)
    working_day = get_working_day(doc.property)
    if not working_day["cashier_shift"]:
        frappe.throw("Please start cashier shift first")   

    frappe.db.set_value("Reservation Stay",{"reservation":reservation,"is_master":1},"is_master",0)
    
    doc.is_master = 1
    doc.save()
    #check if this reservation stay is already check in then and folio not exists
    #create new folio and mark it as master folio
    if doc.reservation_status =='In-house':
        if not frappe.db.exists("Reservation Folio", {"reservation_stay":reservation_stay}):
            frappe.get_doc(
                {
                    "doctype":"Reservation Folio",
                    "guest":doc.guest,
                    "reservation_stay":doc.name,
                    "is_master":1
                }
            ).insert()
    
    frappe.db.commit()
    return doc

@frappe.whitelist(methods="POST")
def check_out(reservation,reservation_stays=None):
    #reservation stay is array
    #validate user role
    #validate cashier shift 
    #remove guest and stay number from room
    
    doc = frappe.get_doc("Reservation",reservation)
    if not reservation:
        frappe.throw("There is no reservation to check out")

    working_day = get_working_day(doc.property)
   
    if not working_day["cashier_shift"]:
        frappe.throw("There is no cashier shift open. Please open cashier shift first")   

    room_status = frappe.db.get_default("housekeeping_status_after_check_out")
    for s in reservation_stays:
        stay = frappe.get_doc("Reservation Stay", s)
        if stay.reservation_status=="Checked Out":
            frappe.throw("Stay # {}. Room {}. This room is already check out.".format(stay.name, stay.rooms))

        if not (stay.departure_date <= working_day["date_working_day"] or stay.departure_date ==add_to_date (working_day["date_working_day"] ,days=-1)):
            frappe.throw("Reservation Stay {}, room {} cannot check out because the departure date is in the future.".format(stay.name,stay.rooms))
        if stay.balance> 0:
            frappe.throw("Reservation Stay {}, room {} cannot check out because the balance is greater than zero".format(stay.name,stay.rooms))


        stay.reservation_status = "Checked Out"
        stay.save()

        #update room status
        #get last stay room form temp occupy
        last_stay_room = frappe.db.sql("select room_id from `tabReservation Stay Room` where parent='{}' order by departure_date desc limit 1".format(stay.name), as_dict=1)
        for r in last_stay_room:
            room_doc = frappe.get_doc("Room", r["room_id"])
            room_doc.housekeeping_status = room_status
            room_doc.guest = None
            room_doc.reservation_stay = None 
            room_doc.save()
        
        #close all open folio
        frappe.db.sql("update `tabReservation Folio` set status = 'Closed' where reservation_stay='{}' and status='Open'".format(s))


    doc = update_reservation(name=reservation,run_commit=False)

    
    #close all open folio 
    
    
    frappe.db.commit()

    #enqueu remove record from temp room occupy
    frappe.enqueue("edoor.api.utils.remove_temp_room_occupy", queue='short', reservation=reservation)

    return {
        "reservation":doc
    }

@frappe.whitelist(methods="POST")
def undo_check_out(property=None, reservation = None, reservation_stays=None):
    stay_doc = {}
    working_day = get_working_day(property)
    room_status = frappe.db.get_default("housekeeping_status_after_undo_check_out")
    for s in reservation_stays:
        stay_doc = frappe.get_doc("Reservation Stay", s)
        if stay_doc.reservation_status =="Checked Out" and stay_doc.departure_date == working_day["date_working_day"]:
            stay_doc.reservation_status = "In-house"
            stay_doc.is_undo_check_out = True
            stay_doc.save()
            
            #get stay date to temp room occupy
            room_occupy_list = frappe.db.sql("select date,room_type_id, room_id,stay_room_id from `tabRoom Occupy` where reservation_stay='{}'".format(s),as_dict=1)
            
            for r in room_occupy_list:
                
                frappe.get_doc({
                    "doctype":"Temp Room Occupy",
                    "reservation":stay_doc.reservation,
                    "reservation_stay":s,
                    "room_type_id":r["room_type_id"],
                    "room_id":r["room_id"],
                    "date":r["date"],
                    "type":"Reservation",
                    "property":stay_doc.property,
                    "stay_room_id":r["stay_room_id"],
                    "adult":stay_doc.adult,
                    "child":stay_doc.child,
                    "pax":stay_doc.pax
                }).insert()

            #update room status
            last_stay_room = frappe.db.sql("select room_id from `tabReservation Stay Room` where parent='{}' order by departure_date desc limit 1".format(stay_doc.name), as_dict=1)
            if last_stay_room:
                room_doc = frappe.get_doc("Room",last_stay_room[0]["room_id"])
                room_doc.housekeeping_status = room_status
                room_doc.guest = stay_doc.guest
                room_doc.reservation_stay = s
                room_doc.save()

        else:
            frappe.throw("This reservation stay {}, room {} is not allow to undo check out".format(stay_doc.name, stay_doc.rooms))
    
        #reopen master folio
        frappe.db.sql("update `tabReservation Folio` set status = 'Open' where reservation_stay='{}' and status='Closed' and is_master=1".format(s))

    if reservation:
        update_reservation(name=reservation,run_commit=False)
    else:
         update_reservation(name=stay_doc.reservation ,run_commit=False)

    frappe.msgprint("Undo check out successfully")
    if not reservation:
        return stay_doc
    #frappe.throw("undo check out ")

@frappe.whitelist()
def change_reservation_guest( guest, reservation='',reservation_stay='', is_apply_all_stays='false', is_apply_master_guest='false', is_only_master_guest='false'):
    doc_guest = json.loads(guest)
    #check if not have guest selected then create new guest
    if doc_guest.get("name") is None:
        guest_info = frappe.get_doc(doc_guest).insert()
    else:
        guest_info = frappe.get_doc(doc_guest).save()
    
    # update master guest
    if(is_apply_master_guest == 'true' or is_only_master_guest == 'true'):
        reservation_doc = frappe.get_doc('Reservation', reservation)
        reservation_doc.guest = guest_info.name
        reservation_doc.save()

    # update only stay
    # if(is_only_master_guest == 'false'):
    if(is_apply_all_stays == 'false'):
        reservation_stay_doc = frappe.get_doc('Reservation Stay', reservation_stay)
        reservation_stay_doc.guest = guest_info.name
        reservation_stay_doc.save()
    else:
        reservation_stays = frappe.get_list('Reservation Stay',filters={"reservation":reservation})
        for s in reservation_stays:
            reservation_stay_doc = frappe.get_doc('Reservation Stay', s)
            reservation_stay_doc.guest = guest_info.name
            reservation_stay_doc.save()
    frappe.db.commit()
    return {
        'guest': guest_info
    }
    
@frappe.whitelist()
def change_reservation_additional_guest(guest,reservation_stay):
 
    doc_guest = json.loads(guest)
    guest_name = ''
    if doc_guest.get("name") is None:
        doc_guest = json.loads(guest)
        doc_guest = frappe.get_doc(doc_guest).insert()
        guest_name = doc_guest.name
    else:
        guest_info = frappe.get_doc(doc_guest).save()
        guest_name = guest_info.name
    doc_stay = frappe.get_doc('Reservation Stay', reservation_stay)
    if doc_stay.guest == guest_name:
        frappe.throw('This guest is already selected.')
    for i in doc_stay.additional_guests:
        if i.guest ==guest_name or i.guest == doc_stay.guest:
            frappe.throw('This guest is already selected.')
    
    doc_stay.append('additional_guests',{'guest':guest_name})
    doc_stay = doc_stay.save()
    frappe.db.commit()
    return {
        'result': doc_stay
    }


def check_field(doc, key):
    if key in doc.keys():
        if  doc[key].strip():
            return True
    return False 



@frappe.whitelist()
def get_reservation_guest(reservation=None, reservation_stay=None):
    sql = """
            select guest as name, guest_name from `tabReservation` where name='{0}'
            union 
            select guest as name, guest_name from `tabReservation Stay` where name='{1}' 
            union 
            select guest as name, guest_name from `tabAdditional Stay Guest` where parent='{1}' 
        """
    sql = sql.format((reservation or ''), (reservation_stay or ''))
    return frappe.db.sql(sql, as_dict=1)

@frappe.whitelist()
def get_reservation_folio(reservation=None, reservation_stay=None):
    if reservation:
        sql = """
                #select 'all' as name , 'All Folio' as folio
                #union
                select name, name as folio from `tabReservation Folio` where reservation='{}'
            """.format(reservation)
        return frappe.db.sql(sql, as_dict=1)
    else:
        sql = """
                #select 'all' as name , 'All Folio' as folio
                #union
                select name, name as folio from `tabReservation Folio` where reservation_stay='{}'
            """.format(reservation_stay)
        return frappe.db.sql(sql, as_dict=1)



@frappe.whitelist(methods="POST")
def get_room_rate(property, rate_type, room_type, business_source, date):
    sql = "select name from `tabSeason` where '{}' between start_date and end_date limit 1".format(date)
    season = frappe.db.sql (sql, as_dict=1)

    room_type_rate  = frappe.get_value("Room Type", room_type,"rate")
    
    rate = 0
   
    if season and rate_type:
        season_id = season[0]["name"]
       
        sql = """select 
                    max(rate) as rate 
                from `tabRate Plan` 
                where 
                    property='{}' and
                    season = '{}' and 
                    rate_type = '{}' 
                """.format(property, season_id, rate_type)
 
        if business_source:
            sql_with_business_source = "{} and business_source = '{}'".format(sql, business_source)
            data = frappe.db.sql(sql_with_business_source, as_dict=1)
            rate = data[0]["rate"] or 0
            
            
        if rate ==0:
            #check rate from rate that dont have business source
            sql = "{} and ifnull(business_source,'') = '' ".format(sql) 
           
            data = frappe.db.sql(sql, as_dict=1)
            rate = data[0]["rate"] or 0

  
    if rate == 0:
        #if still rate = 0 the  get rate from room type
        
        if (frappe.db.get_value("Rate Type",rate_type,"disable_get_rate_room_room_type") or 0)==0:
            rate = room_type_rate

    return rate


#@frappe.whitelist(methods="POST")
@frappe.whitelist()
def change_rate_type(property=None,reservation=None, reservation_stay=None, rate_type = None, apply_to_all_stay = None,regenerate_new_rate=None):
    working_day = get_working_day(property)
    #get reservation room rate
    #udpate to reservation room rate
    room_rates = []
    active_stays = []
    stay = {}
    if reservation_stay:
        stay = frappe.get_doc("Reservation Stay", reservation_stay)
        if not stay.is_active_reservation:
            frappe.throw("Reservation stay # {} is not an active reservation".format(reservation_stay))
        
        if   stay.reservation_status=='Checked Out':
            frappe.throw("Reservation stay # {} is already checked out".format(reservation_stay))
        
        active_stays.append(reservation_stay)
    else:
        apply_to_all_stay = True
    if apply_to_all_stay:
        active_stays = frappe.get_all("Reservation Stay",filters={"is_active_reservation":1,"reservation":reservation}, page_length=10000,pluck='name')
        
        
    room_rates = frappe.get_all("Reservation Room Rate",
                                filters={
                                            "reservation_stay":['in',active_stays],
                                            "date":['>=',working_day["date_working_day"]]
                                }, page_length=10000)
   
    for r in room_rates:
        doc = frappe.get_doc("Reservation Room Rate",r.name)
        doc.rate_type = rate_type
        doc.regenerate_rate = regenerate_new_rate
        doc.save()

    #update rate type to reservation stay
    for s in active_stays:
        doc = frappe.get_doc("Reservation Stay",s)
        doc.rate_type = rate_type
        doc.update_reservation = False
        update_reservation_stay(doc=doc, run_commit = False)
    #disable update to reservation when update stay
    frappe.db.commit()
    if reservation or apply_to_all_stay:
        reservation_doc = frappe.get_doc("Reservation", reservation)
        reservation_doc.rate_type = rate_type
        reservation_doc.update_reservation = True
        reservation_doc.save()
        reservation_doc = update_reservation(name=reservation,run_commit=False)
    return True

@frappe.whitelist()
def get_current_room_reservation(room_id):

    sql = "select parent from `tabReservation Stay Room` where room_id='{}' and '{}' between start_date and end_date and is_active_reservation=1"
    sql = sql.format(room_id,frappe.utils.today() )
    data = frappe.db.sql(sql, as_dict=1)

@frappe.whitelist()
def get_reservation_comment_note(doctype, docname):
    sql = """
        SELECT `name`, creation,note_date, reference_doctype, reference_name,`owner`, content, 'Notice' AS note_type FROM `tabFrontdesk Note` WHERE reference_doctype ='{0}' AND reference_name = '{1}'
        UNION
        SELECT `name`, creation ,NULL as note_date, reference_doctype, reference_name,comment_by AS owner, content, 'Comment' AS note_type FROM `tabComment` WHERE comment_type = 'Comment' AND reference_doctype ='{0}' AND reference_name = '{1}'
    """
    sql = sql.format(doctype, docname)
    data = frappe.db.sql(sql, as_dict=1)
    return data

@frappe.whitelist(methods="POST")
def change_stay(data):
    room_id = ""
    if 'room_id' in data and data["room_id"]:
        room_id = data["room_id"]
    # when we change stay date from drap and drop in room chart calendar we allow to overlap
    if 'ignore_check_room_occupy' in data and not data["ignore_check_room_occupy"]==1: 
        room_occupy = check_room_occupy(property=data['property'],room_type_id=data["room_type_id"],room_id=room_id,start_date=data['start_date'],end_date=data['end_date'],reservation_stay=data['parent'])
        if room_occupy:
            frappe.throw("Room not avaible")
    
    doc = frappe.get_doc("Reservation Stay",data['parent'])
    doc.is_override_rate = 'is_override_rate' in data and data['is_override_rate']
    stays = Enumerable(doc.stays).order_by(lambda x:datetime.strptime(str(x.start_date), '%Y-%m-%d').date()).to_list()
    
    for s in stays:
        if s.name == data['name']:
            s.start_date = data['start_date']
            s.end_date = data['end_date']
        # change last stay room for start date
        index = stays.index(s) + 1
        if len(stays) > index and stays[index]:
            stays[index].start_date = s.end_date
            if datetime.strptime(str(stays[index].start_date), '%Y-%m-%d').date() >= datetime.strptime(str(stays[index].end_date), '%Y-%m-%d').date():
                frappe.throw("Start date cannot greater than end date.{}".format(str(index)))
    doc.save()
    frappe.db.commit()
    if doc: 
        change_room_occupy(doc)
        generate_room_rate(self=doc, is_update_reservation_stay=True)
        update_reservation(name=doc.reservation)
    return doc
    


@frappe.whitelist(methods="POST")
def change_reservation_stay_min_max_date(reservation_stay, arrival_date=None, departure_date=None, arrival_time=None, departure_time=None):
    doc = frappe.get_doc("Reservation Stay",reservation_stay)
    # multiple says
    if len(doc.stays) > 1:
        frappe.throw("This reservation stay has multiple rooms. Please change in room stay.")
    else:
        doc.stays[0].start_date = arrival_date
        doc.stays[0].end_date = departure_date
        doc.stays[0].start_time = arrival_time or "12:00:00"
        doc.stays[0].end_time = departure_time or "12:00:00"
        
        doc.arrival_time = arrival_time or "12:00:00"
        doc.departure_time = departure_time or "12:00:00"
        

    doc.save()
    if getdate(doc.arrival_date)!=getdate(arrival_date) or  getdate(doc.departure_date)!=getdate(departure_date):
        update_reservation(name=doc.reservation, run_commit=False)
        change_room_occupy(doc)
        generate_room_rate(doc)
    frappe.db.commit()
    return doc

@frappe.whitelist(methods="DELETE")
def delete_stay_room(parent,name, note):
    stay = frappe.get_doc('Reservation Stay', parent)
    deleted_row = None
    for p in stay.stays:
        if p.name == name:
            p.deleted_note = note or ""
            deleted_row = p
    stay.save()
    stay.remove(deleted_row)
    stay.save()
    frappe.db.commit()
    if stay:
        update_reservation(name=stay.reservation)
        change_room_occupy(stay)
        generate_room_rate(stay)
    
    return stay

@frappe.whitelist(methods="POST")
def update_note(data):

    note = '' if data.get("note") is None else data['note']
    housekeeping_note = '' if data.get("housekeeping_note") is None else data['housekeeping_note']
    doc = frappe.get_doc(data['doctype'], data['name'])
    doc.note = note
    doc.housekeeping_note = housekeeping_note
    doc.save()

    # apply reservation
 
    if(data['is_apply_reseration']):
        reseration = frappe.get_doc('Reservation', data['reservation'])
        reseration.note = note
        reseration.housekeeping_note = housekeeping_note
        reseration.save() 
        
    # apply all stays
    if(data['is_apply_all_stays']):
        reservation_stays = frappe.get_list('Reservation Stay',filters={"reservation":data['reservation']})
        for s in reservation_stays:
            reservation_stay_doc = frappe.get_doc('Reservation Stay', s)
            reservation_stay_doc.note = note
            reservation_stay_doc.housekeeping_note = housekeeping_note
            reservation_stay_doc.save()

    frappe.db.commit()
    return doc

@frappe.whitelist(methods="POST")
def update_reservation_status(reservation, stays, status, note,reserved_room=True):
    doc_reservation = frappe.get_doc("Reservation", reservation)

    working_day =get_working_day(doc_reservation.property)
    if not working_day["cashier_shift"]:
        frappe.throw("Please start cashier shift first") 
    
    for s in stays:
        if not  s["reservation_status"] in ["Reserved" , "Confirmed"]:
            frappe.throw("You can {} on Confirmed and Reserved reservation only".format(status))
        stay = frappe.get_doc('Reservation Stay', s['name'])
        #check if currentr working day is not equal to arrival date
 
        if getdate( stay.arrival_date) != getdate(working_day["date_working_day"]) and status=="No Show":
            frappe.throw("Reservation stay {}, room {}, Arrival date of date of No Show reservation must be equal to current working date".format(stay.name,stay.rooms ))
        
        #validate folio balance
        if stay.balance> 0:
            frappe.throw("You have folio balance in reservation stay {}. To {} a reservation, balace must be 0".format(stay.name, status))


        stay.reservation_status = status
        stay.reservation_status_note = note
        stay.is_active_reservation = False

        if status=="No Show":
            stay.is_reserved_room = (1 if reserved_room ==True else 0)
        
        stay.save()
        #update is active reservation to room rate 
        frappe.db.sql("update `tabReservation Room Rate` set is_active_reservation = 0 where reservation_stay='{}'".format(s['name']))
        if status!="No Show":
            change_room_occupy(stay)
        else:
            if not reserved_room:
                change_room_occupy(stay)

        #close all folio
        if status in ["Cancelled","No Show","Voided"]:
            frappe.db.sql("update `tabReservation Folio` set status = 'Closed' where reservation_stay='{}' and status='Open'".format(stay.name))
        
    update_reservation(reservation, run_commit=False)
    frappe.db.commit()
    frappe.msgprint("{} reservation successfully".format(status))
    return stays



@frappe.whitelist()
def get_audit_trail(doctype, docname,is_last_modified=False):
    doc_meta = []
    room_rate = ""
    filter_name = ""
    def get_other_doc(doctype=None, field=None, field_name=None):
        separator = "', '"
        data = frappe.db.get_list(doctype, filters={field: field_name})
        sql_filters =  "'" + separator.join([r.name for r in data ]) + "'"
        meta = frappe.get_meta(doctype=doctype)
        doc_meta.append(meta)
        return sql_filters
    filters = ""
    filter_folio_transactions = ""
    filter_reservation_stay = ""
    sql=""
    if is_last_modified:
        sql = "SELECT `name`,docname AS `docname`, ref_doctype AS `doctype`, 'Version' AS `type`, '' AS comment_type, creation,`owner`,`data` AS `content`   FROM `tabVersion` WHERE docname = '{}' AND ref_doctype = '{}' ORDER BY creation DESC LIMIT 1".format(docname,doctype)
    else:
        if doctype == 'Reservation':
            filter_name = 'reservation'
            filter_reservation_stay = get_other_doc('Reservation Stay',filter_name, docname)
            
        elif doctype == 'Reservation Stay':
            filter_name = 'reservation_stay'
            filter_reservation_stay = "'{}'".format(docname)
        
        if filter_name:
            filter_folio_transactions = get_other_doc('Folio Transaction',filter_name,docname)
            room_rate = get_other_doc('Reservation Room Rate',filter_name,docname)
        filters = (','.join(filter(None,[("'{}'".format(docname)),room_rate,filter_folio_transactions,filter_reservation_stay])))

        sql = """
            SELECT `name`,docname AS `docname`, ref_doctype AS `doctype`, 'Version' AS `type`, '' AS comment_type, creation,`owner`,`data` AS `content`   FROM `tabVersion` WHERE docname IN({0})
            UNION
            SELECT `name`,reference_name AS `docname`,reference_doctype AS `doctype`, 'Frontdesk Note' AS `type`, '' AS comment_type, creation,`owner`, `content` AS `content` FROM `tabFrontdesk Note` WHERE reference_name IN({0})
            UNION
            SELECT `name`,reference_name AS `docname`, reference_doctype AS `doctype`, 'Comment' AS `type`, comment_type, creation, COALESCE(comment_by,modified_by) AS `owner`, `content` AS `content` FROM `tabComment` WHERE reference_name IN({0})
            UNION
            SELECT `name`,reservation_stay AS `docname`, '' AS `doctype`, 'Folio Transaction' AS `type`, '' AS comment_type, creation, `owner`, CONCAT('Add ', account_name) AS `content` FROM `tabFolio Transaction` WHERE `name` IN({2})
            UNION
            SELECT `name`,reference_name AS `docname`, reference_doctype AS `doctype`, 'Comment' AS `type`, 'Deleted Folio' AS comment_type, creation,COALESCE(comment_by,modified_by) AS `owner`, CONCAT(reservation,'|',reservation_stay,'|',reservation_folio,'|',folio_number,'|',deleted_document,'|',reason) AS `content` FROM `tabComment` WHERE comment_type = 'Deleted' AND reservation_stay IN({1})
            UNION
            SELECT `name`,reference_name AS `docname`, reference_doctype AS `doctype`, 'Comment' AS `type`, comment_type, creation,COALESCE(comment_by,modified_by) AS `owner`,`content` FROM `tabComment` WHERE comment_type = 'Created' AND reservation_stay IN({1})
        """ 
        sql = sql.format(filters or "''",filter_reservation_stay or "''",filter_folio_transactions or "''")

    data = frappe.db.sql(sql, as_dict=1)
    meta = frappe.get_meta(doctype)
    def get_label(key):
        if(meta.fields and len(meta.fields) > 0):
            field = Enumerable(meta.fields).single_or_default(lambda r:r.fieldname == key)
            if field:
                return field.label
            return ''
    def get_text(t):
        tag = re.compile(r'<[^>]+>')
        text = tag.sub('',str(t))
        text = text if len(text) <= 20 else text.rstrip(text[-20]) + '...'
        return "<b>{}</b>".format(text)
    def get_option(key):
        if(meta.fields and len(meta.fields) > 0):
            field = Enumerable(meta.fields).single_or_default(lambda r:r.fieldname == key)
            if field:
                return field.options
            return ''
    

    result = []
    for record in data:
        prefix = 'You' if record.owner == frappe.session.user else record.owner
        if(record.type == 'Version'):
            content = json.loads(record.content)
            if(len(content['added']) > 0):
                addeds = []
                description = ''
                for add in content['added']:
                    pro_list = []
                    for key, value in add[1].items():
                        pro_list.append({'property': key, 'value': value})
                    property = get_label(add[0])
                    description = description + property + ', '
                    addeds.append({'property':property, 'value': pro_list})
                record['added'] = addeds
                record['description'] = "{0} added rows for {1}".format(prefix, description)
            elif len(content['changed']) > 0:
                pro_list = []
                description = ''
                count_result = 0
                changed_other_doc = ''
                meta_fields = []
                if not record['doctype'] == doctype:
                    changed_other_doc = " in <b>#{}</b>".format(record['doctype'])
                    meta_fields = Enumerable(doc_meta).single_or_default(lambda r:r.name == record['doctype']).fields
                else:
                    meta_fields = meta.fields
                for c in content['changed']:
                    meta_key = Enumerable(meta_fields).single_or_default(lambda r:r.fieldname == c[0])
                    if hasattr(meta_key,'fieldtype') and (meta_key.fieldtype != 'JSON' and meta_key.fieldtype != 'Code' and meta_key.fieldtype != 'HTML') and not meta_key.hidden:
                        count_result = count_result + 1
                        pro_list.append({
                            'property': meta_key.label,
                            'original_value': c[1],
                            'new_value': c[2],
                        })
                        if count_result <= 3:
                            description = description + "{0} from {1} to {2}, ".format(meta_key.label, get_text(c[1]), get_text(c[2]))

                record['changed'] = pro_list 
                record['description'] = "{0} changed the value of {1}{2}".format(prefix, description[:-2],changed_other_doc)
            elif len(content['row_changed']) > 0:
                pro_list = []
                for r in content['row_changed']:
                    pro_list.append({
                        'property': r[0],
                        'index': r[1],
                        'name': r[2],
                        'feilds': r[3]
                    })
                
                groups = Enumerable(pro_list).distinct(lambda x: x['property'])
                group_list = [] 
                for g in groups: 
                    group_list.append({
                        'property': g['property'],
                        'rows': Enumerable(pro_list).where(lambda x: x['property'] == g['property'])
                    })
                description = "{} changed the values for ".format(prefix)
                for g in group_list:
                    description = description + "{} in row ".format(get_label(g['property']))
                    for r in g['rows']:
                        description = description + "#{}, ".format(r['index'])
                record['row_changed'] = group_list
                record['description'] = description[:-2]
            elif len(content['removed']) > 0:
                description = prefix + " removed rows for "
                
                for r in content['removed']:
                    pro_list = []
                    description = description + "{}, ".format(get_label(r[0]))
                    objs = []
                    for key, value in r[1].items():
                        objs.append({'property': key, 'value': value})
                    pro_list.append({
                        'property': get_label(r[0]),
                        'options': get_option(r[0]),
                        'value': objs
                    })
                record['removed'] = pro_list
                record['description'] = description.rstrip(description[-2]) if len(description) > 2 else description
            result.append(record)
        elif record.type == 'Comment' and record.comment_type == 'Created':
            content = json.loads(record.content) 
            list_data = [{'property':k, 'value':v} for k,v in content.items()]
            record['content'] = list_data
            record['description'] = "{} created {} #<b>{}</b>".format(prefix, record.doctype.lower(), content['name'] or '')
            result.append(record)
        else:
            result.append(record)
    if is_last_modified:
        return result[0] if len(result) > 0 else {}
    
    return result


@frappe.whitelist()
def get_folio_transaction(transaction_type, transaction_number):
    show_account_code = frappe.db.get_default("show_account_code_in_folio_transaction")==1
    sql = "select * from `tabFolio Transaction` where ifnull(parent_reference,'') = '' and  transaction_type='{}' and transaction_number='{}'"
    sql = sql.format(transaction_type, transaction_number)
    
       
  
    data = frappe.db.sql(sql,as_dict=1)

    balance = 0
    folio_transactions = []
    for d in data:
        if  d.bank_fee_amount > 0:
            balance = balance + d.bank_fee_amount
          
            folio_transactions.append({ 
                "name":d["name"],
                "room_number":d.room_number,
                "account_name": "{}-{}".format(d.bank_fee_account, d.bank_fee_description)  if show_account_code else d.bank_fee_description,
                "quantity": d["quantity"],
                "note":d["note"],
                "posting_date": d["posting_date"],
                "debit": d.bank_fee_amount,
                "credit": 0,
                "balance":balance,
                "owner":d["owner"],
                "modified_by":d["modified_by"],
                "creation":d.creation,
                "show_print_preview":d.show_print_preview,
                "print_format":d.print_format,
                "is_auto_post":d["is_auto_post"]

            })


      
        #this is main transaction
        amount = d.amount
         
        # if d.rate_include_tax=="Yes":
        #     amount =( amount - d.total_tax ) + d.discount_amount
        
        balance = balance + (amount * (1 if d.type=="Debit" else -1))        

        folio_transactions.append({ 
            "name":d["name"],
            "room_number":d.room_number,
            "account_name": "{}-{}".format(d.account_code, d.account_name)  if show_account_code else d.account_name,
            "quantity": d["quantity"],
            "note":d["note"],
            "posting_date": d["posting_date"],
            "debit": amount  if d["type"] == 'Debit' else 0,
            "credit": amount  if d["type"] == 'Credit' else 0,
            "balance":balance,
            "owner":d["owner"],
            "modified_by":d["modified_by"],
            "creation":d.creation,
            "show_print_preview":d.show_print_preview,
            "print_format":d.print_format,
             "is_auto_post":d["is_auto_post"]
        })

        if  d.discount_amount > 0:
            balance = balance - d.discount_amount
            folio_transactions.append({
                "account_name": "{}-{}".format(d.discount_account, d.discount_description)  if show_account_code else d.discount_description,
                "credit":d.discount_amount,
                "debit":0,
                "balance":balance
            })
        
        if  d.tax_1_amount > 0:
            balance = balance + d.tax_1_amount
            folio_transactions.append({
                "account_name": "{}-{}".format(d.tax_1_account, d.tax_1_description)  if show_account_code else d.tax_1_description,
                "debit":d.tax_1_amount,
                "credit":0,
                "balance":balance
            })

        if  d.tax_2_amount > 0:
            balance = balance + d.tax_2_amount
            folio_transactions.append({
                "account_name": " {}-{}".format(d.tax_2_account, d.tax_2_description)  if show_account_code else d.tax_2_description,
                "debit":d.tax_2_amount,
                "credit":0,
                "balance":balance
            })

        if  d.tax_3_amount > 0:
            balance = balance + d.tax_3_amount
            folio_transactions.append({
                "account_name": "{}-{}".format(d.tax_3_account, d.tax_3_description)  if show_account_code else d.tax_3_description,
                "debit":d.tax_3_amount,
                "credit":0,
                "balance":balance
            })
        
        
    return folio_transactions

@frappe.whitelist()
def get_folio_transaction_summary(folio_number):
    data = frappe.db.sql("""
                    select 
                        room_number,
                        account_name,
                        type,
                        account_category_sort_order, 
                        sum(amount) as amount
                    from `tabFolio Transaction` 
                    where 
                        folio_number = '{}' 
                        group by 
                            account_name ,
                            room_number,
                            type
                        order by 
                            account_category_sort_order
                """.format(folio_number),as_dict=1)
    summary_data = []
    balance = 0
    for d in data:
        balance = balance + d["amount"]  * (1 if d["type"] =="Debit" else -1)
        summary_data.append({
            "room_number":d["room_number"],
            "description":d["account_name"],
            "debit": d["amount"] if d["type"] == "Debit" else 0,
            "credit": d["amount"] if d["type"] == "Credit" else 0,
            "balance":balance
        })

    
    return summary_data


@frappe.whitelist()
def get_reservation_housekeeping_charge_summary(reservation_stay):
    data  = frappe.db.sql("""
                    select 
                        sum(if(type='Credit',amount,0)) as credit,
                        sum(if(type='Debit',amount,0)) as debit
                    from `tabFolio Transaction` 
                    where 
                        reservation_stay = '{}' 
                    """.format(reservation_stay),as_dict=1)
 
    if data:
        return  {"credit":data[0]["credit"] or 0, "debit":data[0]["debit"] or 0}
        
    return {"credit":0, "debit":0}


@frappe.whitelist(methods="POST")
def update_room_rate(room_rate_names= None,data=None,reservation_stays=None):
    
    #validate reservation status 
    #reservation_stays is array string

    if reservation_stays:
        for s in reservation_stays:
          
            status = frappe.db.get_value("Reservation Stay",s,"reservation_status")
            if frappe.db.get_value("Reservation Status",status, "allow_user_to_edit_information")==0:
                frappe.throw("Reservation Stay: {0} is {1}. {1} reservation is not allow to change information".format(s, status) )
 
    if  len(room_rate_names) ==0:
        room_rate_names.append(data["name"])
    for d in room_rate_names:
        doc = frappe.get_doc("Reservation Room Rate",d)
        doc.is_manual_rate = data["is_manual_rate"]
        doc.rate_type = data["rate_type"]
        doc.input_rate = data["input_rate"]
        doc.discount_type = data["discount_type"] 
        doc.discount = data["discount"] 
        doc.tax_rule = data["tax_rule"]
        doc.tax_1_rate = data["tax_1_rate"]
        doc.tax_2_rate = data["tax_2_rate"]
        doc.tax_3_rate = data["tax_3_rate"]
        doc.rate_include_tax = data["rate_include_tax"]
        doc.save()

    #update to reservation stay
    #using enqure process 
    #loop from stays list to update room charge summary to reservation stay
    if reservation_stays:
        for s in reservation_stays:
            update_reservation_stay(name=s, run_commit=False)
    else:
        update_reservation_stay(name=data["reservation_stay"], run_commit=False)

    update_reservation(name=data["reservation"], run_commit=False)
    #frappe.enqueue("edoor.api.utils.update_reservation_stay", queue='short', name=data["reservation_stay"], doc=None, run_commit=False)

    frappe.db.commit()
    #update to reservation
    # #using enqure process  
    return frappe.get_list("Reservation Room Rate",fields=["*"], filters={"reservation_stay":data["reservation_stay"]},limit_page_length=1000,order_by="date")
    
@frappe.whitelist(methods="POST")
def update_business_source(reservation, business_source, regenerate_rate,reservation_stay):
    reservation_doc = frappe.get_doc("Reservation", reservation)
    #check reservation status if allow to edit information
    doc_reservation_stay = None
    if reservation_stay:
        doc_reservation_stay = frappe.get_doc("Reservation Stay", reservation_stay)
        if (frappe.db.get_value("Reservation Status",doc_reservation_stay.reservation_status,"allow_user_to_edit_information") or 0 )==0:
            frappe.throw("Reservation stay # {}, status {} is not allow to edit information".format(reservation_stay, doc_reservation_stay.reservation_status))
    else:
        #if user edit from reservation not have stay name
        #find all stay that not allow to edit information then throw error
        sql = """
                select name from `tabReservation Status` where name in (
                    select distinct reservation_status  from `tabReservation Stay` s where s.reservation = '{}' and s.is_active_reservation=1  
                ) and   allow_user_to_edit_information = 0 limit 1

            """.format(reservation)
 
        data = frappe.db.sql(sql,as_dict=1)
        if data:
            frappe.throw("You cannot change business source in this reservation. Because it has reservation stays that not allow to change information")




    reservation_doc.business_source = business_source
    reservation_doc.save()
 
     
    working_day = get_working_day(reservation_doc.property)

    if regenerate_rate:
        active_stays = frappe.get_all("Reservation Stay",filters={"is_active_reservation":1,"reservation":reservation}, page_length=10000,pluck='name')
        
        room_rates = frappe.get_all("Reservation Room Rate",
                                    filters={
                                                "is_manual_rate":['=',0],
                                                "reservation_stay":['in',active_stays],
                                                "date":['>=',working_day["date_working_day"],
                                                ]
                                    }, page_length=10000)
      
        for r in room_rates:
            doc = frappe.get_doc("Reservation Room Rate",r.name)
            doc.regenerate_rate = regenerate_rate
            doc.save()

        for s in active_stays:
            update_reservation_stay(name=s, run_commit = False)
         
        update_reservation(name=reservation, run_commit = False)
    
    frappe.db.commit()
    if reservation_stay:
        return frappe.get_doc("Reservation Stay", reservation_stay)
    else:
        return reservation_doc
    
@frappe.whitelist()
def get_folio_transaction_detail(name):
    folio_transaction = frappe.get_doc("Folio Transaction", name)
    account_code = frappe.get_doc("Account Code", folio_transaction.account_code)
    return {
        "folio_transaction":folio_transaction,
        "account_code":account_code
    }

@frappe.whitelist(methods="POST")
def auto_update_reservation_stay(docname, data, update_doc):
    data = json.loads(json.dumps(data))
    doc = frappe.get_doc("Reservation Stay",docname)
    for i in data:
        setattr(doc, i['fieldname'], i['value'])

    doc = doc.save()
    for f in update_doc:
        if f == 'update_reservation':
            update_reservation(name=doc.reservation)
        if f == 'update_room_occupy':
            change_room_occupy(doc)
        if f == 'update_room_rate':
            generate_room_rate(doc)
        if f == 'update_reservation_stay':
            update_reservation_stay(doc=doc)
    frappe.db.commit()
    return doc

@frappe.whitelist(methods="POST")
def upgrade_room(doc):
    data = frappe.get_doc('Reservation Stay',doc['name'])
    for dc in doc['stays']:
        if 'name' in dc and dc['name']:
            indices = [i for i, d in enumerate(data.stays) if dc['name'] in d.name]
            data.stays[indices[0]].end_date = dc['end_date']
        else:
            data.append('stays', dc) 
    data.save()
    frappe.db.commit()
    if data:
        change_room_occupy(data)
        update_reservation(name=data.reservation)
        generate_room_rate(self=data,is_update_reservation_stay=True)
    return data

@frappe.whitelist(methods="POST")
def unassign_room(reservation_stay, room_stay):
    doc = frappe.get_doc('Reservation Stay', reservation_stay)
    doc.reservation_status = 'Confirmed'
    for s in doc.stays:
        if s.name == room_stay:
            s.room_id = None
            s.room_number = None
    doc.save()
    
    if doc:
        change_room_occupy(doc)
        generate_room_rate(self=doc, is_update_reservation_stay=True)
        update_reservation(name=doc.reservation, run_commit=False)
    
    frappe.db.commit()

    frappe.msgprint(frappe._("Unassign room successfully"))
    return doc

@frappe.whitelist(methods="POST")
def assign_room(data):
    doc = frappe.get_doc('Reservation Stay', data['reservation_stay'])
    doc.reservation_status = 'Reserved'
    if 'room_id' in data:
        if not data['room_id']:
            frappe.throw(_("Please assign room."))
    else:
        frappe.throw(_("Please assign room."))
    for s in doc.stays:
        if s.name == data['stay_room']:
            s.room_id = data['room_id'] or None
            s.room_type_id = data['room_type_id']
            if data['is_override_rate'] or data['is_manual_rate']:
                s.is_manual_rate = data['is_manual_rate']
                s.input_rate = data['rate']
    doc.save()
    
    if doc:
        change_room_occupy(doc)
        generate_room_rate(self=doc,is_update_reservation_stay=True)
        update_reservation(name=doc.reservation, run_commit=False)
    
    frappe.db.commit()
    frappe.msgprint(_("Assign room successfully"))
    return doc
@frappe.whitelist()
def get_room_rate_by_name_to_edit(name):
    doc = frappe.get_doc("Reservation Room Rate", name)
    stay = frappe.get_doc("Reservation Stay", doc.reservation_stay)
    future_rate = frappe.db.sql("select name,reservation_stay from `tabReservation Room Rate` where reservation_stay='{}' and date>'{}'".format(doc.reservation_stay,doc.date),as_dict=1)

    return {
        "room_rate":doc,
        "reservation_stay":stay,
        "future_room_rate":future_rate
    }

@frappe.whitelist(methods="POST")
def update_reservation_information(doc, apply_all_active_stay=False,update_to_reservation = False):
  
    if doc["doctype"]=="Reservation Stay":
        if (doc["allow_user_to_edit_information"] or 0)==0:
            frappe.throw("{} reservation is not allow to edit information".format(doc["reservation_status"]))
    
        if not apply_all_active_stay:
            frappe.get_doc(doc).save()

    if apply_all_active_stay:
        active_stay = frappe.db.sql("select name from `tabReservation Stay` where allow_user_to_edit_information = 1 and reservation='{}'".format(doc["reservation"] if doc["doctype"]=="Reservation Stay" else doc["name"]),as_dict=1)
        for s in active_stay:
            stay = frappe.get_doc("Reservation Stay",s["name"])
            stay.reference_number = doc["reference_number"]
            stay.internal_reference_number = doc["internal_reference_number"]
            stay.reservation_date = doc["reservation_date"]
            stay.save()

    
 
    #update reservation 
    reservation = frappe.get_doc("Reservation",doc["reservation"] if doc["doctype"]=="Reservation Stay" else doc["name"])
    reservation.group_code = doc["group_code"] 
    reservation.group_name = doc["group_name"]
    if update_to_reservation or  doc["doctype"]=="Reservation":
        reservation.reference_number = doc["reference_number"]
        reservation.internal_reference_number = doc["internal_reference_number"]
        reservation.reservation_date = doc["reservation_date"]
    reservation.save()


    if doc["doctype"]=="Reservation Stay":
        return frappe.get_doc("Reservation Stay",doc["name"])
    else:
        return reservation
    
@frappe.whitelist(methods="POST")
def update_reservation_color(data):
    
    reservation = data['name']
    if data['doctype'] == 'Reservation Stay':
        reservation = data['reservation']

    frappe.db.set_value('Reservation', reservation, 'reservation_color', data['reservation_color'])
 
    stays = frappe.db.get_list('Reservation Stay', filters={'reservation':reservation, 'is_active_reservation': 1})
    for t in stays:
        doc = frappe.get_doc('Reservation Stay', t.name)
        doc.reservation_color = data['reservation_color']
        doc.save()
    return frappe.get_doc(data['doctype'], data['name'])


@frappe.whitelist(methods="POST")
def unreserved_room(property, reservation_stay):
    working_day = get_working_day (property)
    if not working_day["cashier_shift"]:
        frappe.throw("Please start cashier shift first")   
    
    stay = frappe.get_doc("Reservation Stay", reservation_stay)
    if stay.reservation_status !="No Show":
        frappe.throw("You cannot unserved room for {} reservation".format(stay.reservation_status))
    
    if getdate(stay.departure_date)<= getdate(working_day["date_working_day"]):
        frappe.throw("Departure date must be greater than current working date")
    
    stay.is_reserved_room=0
    stay.save()

    frappe.db.sql("update `tabReservation Stay Room` set show_in_room_chart = 0 where parent='{}'".format(stay.name))
    frappe.db.sql("delete from `tabTemp Room Occupy`  where reservation_stay='{}'".format(stay.name))
    frappe.db.sql("delete from `tabRoom Occupy`  where reservation_stay='{}'".format(stay.name))

    frappe.db.commit()
    frappe.msgprint("Unreserved room successfully")

@frappe.whitelist(methods="POST")
def reserved_room(property, reservation_stay):
    working_day = get_working_day (property)
    if not working_day["cashier_shift"]:
        frappe.throw("Please start cashier shift first")   
    
    stay = frappe.get_doc("Reservation Stay", reservation_stay)

    if stay.reservation_status !="No Show":
        frappe.throw("You cannot reserved room for {} reservation".format(stay.reservation_status))
    
    if getdate(stay.departure_date)<= getdate(working_day["date_working_day"]):
        frappe.throw("Departure date must be greater than current working date")


    #validate room availability
    #check room type first
    for s in stay.stays:
        available_room = check_room_type_availability(
            property=stay.property,
            room_type_id=s.room_type_id,
            start_date=s.start_date,
            end_date=s.end_date
        )
        for d in available_room:
            if d.total_vacant_room == 0:
                frappe.throw("Room type {} is not available".format(s.room_type))

        #check if current room is already assign room 
        if s.room_id:
            
            data = frappe.db.sql("select name from `tabTemp Room Occupy` where room_id='{}' and date between '{}' and '{}'".format(s.room_id, s.start_date, add_to_date(getdate(s.end_date), days=-1)),as_dict=1)
            if data:
                frappe.throw("Room {} is not available now".format(s.room_number))
    
    stay.is_reserved_room=1
    stay.save()

    frappe.db.sql("delete from `tabTemp Room Occupy` where reservation_stay='{}'".format(stay.name))
    frappe.db.sql("delete from `tabRoom Occupy` where reservation_stay='{}'".format(stay.name))

    


    dates = get_date_range(working_day["date_working_day"], stay.departure_date)
    for s in stay.stays: 
        for d in dates:
            #generate room to temp room occupy
            frappe.get_doc({
                "doctype":"Temp Room Occupy",
                "reservation":stay.reservation,
                "reservation_stay":stay.name,
                "room_type_id":s.room_type_id,
                "room_id":s.room_id,
                "date":d,
                "type":"Reservation",
                "property":stay.property,
                "stay_room_id":s.name,
                "adult":stay.adult,
                "child":stay.child,
                "pax":stay.pax

            }).insert()


            #generate room to room occupy
            frappe.get_doc({
                "doctype":"Room Occupy",
                "room_type_id":s.room_type_id,
                "room_id":s.room_id,
                "date":d,
                "type":"Reservation",
                "property":stay.property,
                "stay_room_id":s.name,
                "reservation":stay.reservation,
                "reservation_stay":stay.name,
                "adult":stay.adult,
                "child":stay.child,
                "pax":stay.pax
            }).insert()
    
    #show no show reservation to room chart
    frappe.db.sql("update `tabReservation Stay Room` set show_in_room_chart = 1 where parent='{}'".format(stay.name))

    frappe.db.commit()
    frappe.msgprint("Reserved room successfully")

@frappe.whitelist()
def get_reservation_stay_for_assign_room(reservation):
    doc_reservation = frappe.get_doc("Reservation", reservation)
    data = frappe.db.sql("""
                            select 
                                name, 
                                parent as reservation_stay,
                                start_date, 
                                end_date, 
                                room_type_id, 
                                room_type_id as new_room_type_id,
                                room_type, '' as room_id,
                                rate_type,
                                rate,
                                room_nights,
                                guest,
                                guest_name ,
                                0 as is_generate_rate
                            from `tabReservation Stay Room` 
                            where 
                                reservation='{}' and 
                                is_active_reservation=1 and 
                                ifnull(room_id,'')=''""".format(reservation),as_dict=1)
    dates = []
    for d in data:
        dates.append({"start_date":d["start_date"],"end_date":d["end_date"]})
    
    room_available = [dict(t) for t in {tuple(d.items()) for d in dates}]

    for d in room_available:
        d["room_types"] = check_room_type_availability(
                property=doc_reservation.property, 
                start_date=d["start_date"],
                end_date=d["end_date"],
                business_source= doc_reservation.business_source,
                )
        d["rooms"] = check_room_availability(
            property=doc_reservation.property, 
                start_date=d["start_date"],
                end_date=d["end_date"],
        )

    

    return {"data":data, "rooms":room_available}


@frappe.whitelist(methods="POST")
def bulk_assign_room(reservation, reservation_stays):
    #check if user select room
    if len(reservation_stays)==0:
        frappe.throw("Please select at lease 1 room to assign room")
    

    for stay in reservation_stays:
        doc = frappe.get_doc('Reservation Stay', stay['reservation_stay'])
        doc.reservation_status = 'Reserved'
        for s in doc.stays:
            if s.name == stay["name"]:
                s.room_id = stay["room_id"]
                s.room_type_id = stay['new_room_type_id']
                if stay["room_type_id"] !=stay['new_room_type_id']:
                    if stay["is_generate_rate"] == 1:
                        doc.is_override_rate = 1
                #update room id and room_name to temp room occupy and room occupy
                room_number = frappe.db.get_value("Room", s.room_id, "room_number")
                room_type,room_type_alias = frappe.db.get_value("Room Type", s.room_type_id, ["room_type","alias"])
 
                sql = """update `{0}` 
                                set room_id='{1}' ,
                                room_number='{2}' ,
                                room_type_id = '{3}',
                                room_type = '{4}'
                                where stay_room_id= '{5}'
                                """
                
                frappe.db.sql(sql.format(
                                    "tabTemp Room Occupy",
                                    s.room_id, 
                                    room_number,
                                    s.room_type_id,
                                    room_type,
                                    s.name
                                    )
                )
                
                frappe.db.sql(sql.format(
                                    "tabRoom Occupy",
                                    s.room_id, 
                                    room_number,
                                    s.room_type_id,
                                    room_type,
                                    s.name
                                    )
                )

                doc.save()

                if stay["is_generate_rate"] == 1:
                    generate_room_rate(self=doc,is_update_reservation_stay=True, run_commit=False)
                else:
                    #update room to room rate
                    
                    sql = """update `tabReservation Room Rate` 
                            set room_id='{0}' ,
                            room_number='{1}' ,
                            room_type_id = '{2}',
                            room_type = '{3}',
                            room_type_alias='{4}'
                            where stay_room_id= '{5}'
                            """.format(
                                s.room_id,
                                room_number,
                                s.room_type_id,
                                room_type,
                                room_type_alias,
                                s.name
                            )
                    
                    frappe.db.sql(sql)

        
    update_reservation(name=reservation, run_commit=False)
    frappe.db.commit()
    
    frappe.msgprint(_("Assign room successfully"))
        
    
@frappe.whitelist()
def get_reservation_room_rate(reservation):
    sql="select * from `tabReservation Room Rate` where reservation = '{}' and is_active_reservation = 1 order by date, room_number "
    data = frappe.db.sql(sql.format(reservation),as_dict=1)
    return data
    
    
@frappe.whitelist(methods="POST")
def update_mark_as_paid_by_master_room(stays, paid_by_master_room):
    for s in stays:
        frappe.db.set_value("Reservation Stay", s,"paid_by_master_room",paid_by_master_room)
    if paid_by_master_room==1:
        frappe.msgprint("Update mark as paid by master room successfully")
    else:
        frappe.msgprint("Update unmark as paid by master room successfully")
    
@frappe.whitelist(methods="POST")
def update_allow_post_to_city_ledger(stays, allow_post_to_city_ledger):
    for s in stays:
        frappe.db.set_value("Reservation Stay", s,"allow_post_to_city_ledger",allow_post_to_city_ledger)
    if allow_post_to_city_ledger==1:
        frappe.msgprint("Allow post to city ledger successfully")
    else:
        frappe.msgprint("Unallow post to city ledger successfully")
