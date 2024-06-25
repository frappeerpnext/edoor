from datetime import datetime
from decimal import Decimal
import json
from edoor.api.folio_transaction import get_master_folio, post_charge_to_folio_afer_check_in, update_reservation_folio
from edoor.api.tax_calculation import get_tax_breakdown
from edoor.api.cache_functions import get_account_category_doc, get_account_code_doc, get_account_code_sub_account_information, get_base_rate_cache, get_rate_type_doc, get_rate_type_info_with_cache
from edoor.edoor.doctype.reservation_stay.reservation_stay import    update_reservation_stay_room_rate, update_reservation_stay_room_rate_after_move, update_reservation_stay_room_rate_after_resize
from py_linq import Enumerable
import re
from edoor.api.frontdesk import get_working_day
from edoor.api.utils import check_user_permission, get_date_range, get_rate_type_info, update_is_arrival_date_in_room_rate, update_reservation_stay,update_reservation,add_room_charge_to_folio, update_reservation_stay_and_reservation, validate_backdate_permission, validate_role,update_keyword,add_package_inclusion_charge_to_folio,get_breakdown_package_charge_code
import frappe
import time
import uuid  
from frappe.model.document import bulk_insert
from frappe.model.naming import make_autoname
from frappe.utils.data import add_to_date, getdate,now
from frappe import _
from frappe.utils import (
	cint
)
from functools import lru_cache
from edoor.api.generate_occupy_record import generate_room_occupies
from edoor.api.generate_room_rate import generate_forecast_revenue, generate_new_room_rate, generate_new_room_rate_by_stay_room_id, get_charge_breakdown_by_account_code_breakdown, get_package_charge_data, get_room_rate_account_code_breakdown, get_room_rate_breakdown, package_base_account_code_charge_breakdown

@frappe.whitelist()
def test():
    data = frappe.db.get_all("Account Code", filters={"parent_account_code":"1000"}, order_by='lft')
    return data 
@frappe.whitelist()
def get_reservation_folio_list(reservation):
    sql="""
        select 
            name,
            guest_name,
            guest,
            rooms,
            reservation_status,
            status_color,
            total_credit,
            total_debit,
            balance,
            allow_post_to_city_ledger

        from `tabReservation Stay` 
        where 
            name in (select reservation_stay from `tabReservation Folio` where reservation='{}') 
        """.format(reservation)
    
    data = frappe.db.sql(sql,as_dict=1)
    sql = "select name, reservation_stay,reservation, posting_date, guest,guest_name, total_credit,total_debit,balance ,status,is_master,note,business_source,folio_type,folio_type_color from `tabReservation Folio` where reservation='{}'".format(reservation)
    folios = frappe.db.sql(sql,as_dict=1)
    
    if folios:
        for d in data:
            d["folios"]=[f.update({"allow_post_to_city_ledger":d["allow_post_to_city_ledger"]}) or f for f in folios if f["reservation_stay"]==d["name"]]
 
    
    return data

@frappe.whitelist()
def get_reservation_detail(name):


    #start get information
    reservation= frappe.get_doc("Reservation",name)
    reservation_stays = frappe.get_list("Reservation Stay",filters={'reservation': name},fields=['name','rooms_data','require_drop_off','require_pickup','room_type_alias','is_active_reservation','rate_type','guest','total_credit','balance','total_debit','total_room_rate','reservation_status','status_color','guest_name','pax','child','adult','adr', 'reference_number','arrival_date','arrival_time','departure_date','departure_time','room_types','rooms',"is_master","paid_by_master_room","allow_post_to_city_ledger","allow_user_to_edit_information","room_nights","is_package"])
    master_guest = frappe.get_doc("Customer",reservation.guest)
    total_folio = frappe.db.count('Reservation Folio', {'reservation': name})

    return {
        "reservation":reservation,
        "reservation_stays":reservation_stays,
        "master_guest": master_guest,
        "total_folio":total_folio or 0,
    }



@frappe.whitelist()
def get_reservation_stay_detail(name):
    reservation_stay= frappe.get_doc("Reservation Stay",name)
    if reservation_stay.reservation_status in ["Reserved","In-house","Confirmed","No Show"]:
        #verify reservation stay this function will fix some problem that occure in room occupy generation , temp room occupy and room rate
        frappe.enqueue("edoor.api.reservation.verify_reservation_stay",queue='long', stay_name = name )
       

    reservation = frappe.get_doc("Reservation",reservation_stay.reservation)
    total_reservation_stay = frappe.db.count("Reservation Stay", {'reservation': reservation.name})
    guest=frappe.get_doc("Customer",reservation_stay.guest)

    reservation_stay_names =frappe.get_all("Reservation Stay",filters={"reservation":reservation_stay.reservation},order_by="name", page_length=10000,pluck='name')
    

    master_guest = guest
    if reservation.guest != reservation_stay.guest:
        master_guest = frappe.get_doc("Customer",reservation.guest)

    total_folio = frappe.db.count('Reservation Folio', {'reservation_stay': name})
  


    
    return {
        "reservation":reservation,
        "total_reservation_stay": total_reservation_stay,
        "reservation_stay":reservation_stay,
        "guest":guest,
        "master_guest":master_guest,
        "reservation_stay_names":reservation_stay_names,
        "total_folio":total_folio or 0,
 
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

    data = frappe.db.sql(sql, as_dict=1)
    #validate to reservation filio 
    balance = frappe.db.get_value(transaction_type,transaction_number,"balance")
    

    if balance != sum([d["amount"] for d in data]):
        
        sql="update `tab{0}` set total_debit={1},total_credit={2}, balance={1}-{2} where name='{3}'".format(
            transaction_type,
            sum(d["amount"] for d in data if d["amount"]> 0), 
            abs(sum(d["amount"] for d in data if d["amount"]< 0)),
            transaction_number
        )
        frappe.db.sql(sql)
         
        frappe.db.commit()

    
    

    return data


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
            property = %(property)s and 
            room_type_id = if(%(room_type_id)s='', room_type_id, %(room_type_id)s) and
            name not in (
                select 
                    distinct
                    coalesce(room_id,'') 
                from `tabTemp Room Occupy` 
                where
                    is_departure = 0 and
                    date between '{0}' and '{1}' {2}
            )   
    """
    #check if arrival date is equal to current system date then check room availabityy is check with house keeping status
    # concat where condition with show_in_room_availability = 1
    if str(start_date) == str(working_day["date_working_day"]):
        sql = "{} and coalesce(show_in_room_availability,0)  = 1".format(sql)
   
    sql = sql.format(start_date, end_date,sql_except)
 
    data = frappe.db.sql(sql,{"property":property,"room_type_id":room_type_id},as_dict=1)
    return data

@frappe.whitelist()
def check_room_type_availability(property,start_date=None,end_date=None,rate_type=None, business_source=None, room_type_id=None,exclude_stay_room_id=None):
    end_date = add_to_date(end_date,days=-1)
    #check if start date < current working date then set start date to crrent working date because we check date only for future date
    working_day = get_working_day(property=property)
    if getdate(start_date)< getdate(working_day["date_working_day"]):
        start_date = working_day["date_working_day"]

    #get all room type and total room 
    sql_room_type = "select a.room_type_id as name, a.room_type, count(a.name) as total_room, 0 as occupy from `tabRoom` a inner join `tabRoom Type` rt on rt.name = a.room_type_id where a.disabled = 0 and a.property=%(property)s  group by a.room_type_id,a.room_type order by rt.sort_order"
    if room_type_id:
        sql_room_type = "select room_type_id as name, room_type, count(name) as total_room, 0 as occupy from `tabRoom` where disabled = 0 and property=%(property)s and room_type_id = %(room_type_id)s  group by room_type_id,room_type order by sort_order"
    
    room_type = frappe.db.sql(sql_room_type,{"property":property,"room_type_id":room_type_id},as_dict=1)
    
    for t in room_type:
        #get total room occupy from temp room occupy 
        #we count stay_room_id because some reervation stay is not yet assign room
        sql = "select count(room_type_id) as total_room from `tabTemp Room Occupy` where is_departure = 0 and  room_type_id = '{}' and date between '{}' and '{}'".format(t["name"],start_date,end_date)
        if exclude_stay_room_id:
            sql = sql + " and stay_room_id<>'{}'".format(exclude_stay_room_id) 
            
        sql= sql + " group by date order by count(room_type_id) desc limit 1"
       
        room_type_occupy = frappe.db.sql(sql,as_dict=1)
  
        if room_type_occupy:
            t["occupy"] = room_type_occupy[0]["total_room"]
        else:
            t["occupy"] = 0

        t["total_vacant_room"] = (t["total_room"] or 0) - ( t["occupy"] or 0)
        
        t["rate"] = 0 if not rate_type else  get_room_rate(property, rate_type, t["name"], business_source, start_date)
        # return get_room_rate(property, rate_type, t["name"], business_source, start_date)
        t["new_rate"] = t["rate"]

    #return  [d for d in room_type if ((d['total_room'] or 0) - (d["occupy"] or 0) > 0)]

    return  room_type


@frappe.whitelist()
def check_room_occupy(property,room_type_id, room_id, start_date=None, end_date=None, reservation_stay=None):
    end_date = add_to_date(end_date,days=-1)
    except_stay = ""
    if reservation_stay:
        except_stay = " AND coalesce(reservation_stay,'') <> '{}'".format(reservation_stay)
    sql = "SELECT COUNT(name) AS total FROM `tabTemp Room Occupy` WHERE is_departure = 0 and property='{4}' AND room_id = '{0}' AND room_type_id = '{5}' AND DATE BETWEEN '{1}' AND '{2}'{3}".format(room_id,start_date,end_date,except_stay,property,room_type_id)
    room_occupy = frappe.db.sql(sql)
    return room_occupy[0][0]


@frappe.whitelist(methods="POST")
def add_new_reservation(doc):
    get_rate_type_doc.cache_clear()
    get_account_code_doc.cache_clear()
    
    if not  "rate_type"  in doc["reservation"]:
        frappe.throw("Please select rate type")

    #for group booking stay can be 0 
    if len(doc["reservation_stay"]) == 0:
        frappe.throw("Please select room to add reservation")


    arrival_date = doc["reservation"]["arrival_date"]
    working_day = get_working_day(doc["reservation"]["property"])
    
    if not working_day["cashier_shift"]:
        frappe.throw("Please start cashier shift first") 

 
    if frappe.utils.getdate(arrival_date) < working_day["date_working_day"]:
        
        if str(frappe.db.get_single_value("eDoor Setting","allow_user_to_add_back_date_transaction")) =="1":
           
            backdate_role = frappe.db.get_single_value("eDoor Setting","role_for_back_date_transaction")
            
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
        
        guest = frappe.get_doc(doc["guest_info"]).insert(ignore_permissions=True)
      
        doc["reservation"]["guest"] = guest.name
    else:
        guest = frappe.get_doc(doc["guest_info"]).save(ignore_permissions=True)
    

    #assign is_complementary or is house use o reservation
    is_complementary, is_house_use = frappe.db.get_value("Rate Type", doc["reservation"]["rate_type"],["is_complimentary","is_house_use"])

    doc["reservation"]["is_complimentary"] = is_complementary
    doc["reservation"]["is_house_use"] = is_house_use

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
    # check if item is package item then get package item from account code attach to reservation stay
     
    package_items = get_package_item_for_reservation_stay(reservation.rate_type)
    
    for   d in doc["reservation_stay"]:
        room = None

        if  'room_id' in d.keys():
            room = d["room_id"]
            #checi if room is not available
            if d["room_id"]:
                check_room_not_available = frappe.db.sql("select name from `tabTemp Room Occupy` where is_departure=0 and room_id='{}' and date between '{}' and '{}'".format(room, reservation.arrival_date, add_to_date(getdate(reservation.departure_date), days=-1)),as_dict=1)
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
            "rate":reservation.rate_type,
            "is_complimentary":is_complementary,
            "is_house_use":is_house_use,
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
            "group_color":reservation.group_color,
            "reservation_color_code":reservation.reservation_color_code,
            "adult":d["adult"],
            "child":d["child"],
            "is_walk_in":0 if not "is_walk_in"  in doc["reservation"] else doc["reservation"]["is_walk_in"],
            "stays":[
                {
                    "doctype":"Reservation Stay Room",
                    "room_type_id": d["room_type_id"],
                    "room_id":room,
                    "input_rate":d["rate"] or 0,
                    "guest":reservation.guest,
                    "reservation_status":"Reserved" if (room or '') !='' else "Confirmed",
                    "business_source":reservation.business_source,
                    "start_date":reservation.arrival_date,
                    "end_date":reservation.departure_date,
                    "start_time":reservation.arrival_time,
                    "end_time":reservation.departure_time,
                    "is_master":d["is_master"] ,
                    "is_manual_rate":d["is_manual_rate"]
                }
            ],
            "inclusion_items":package_items
        }
       
        stay_doc = frappe.get_doc(stay).insert()
        stay_names.append(stay_doc.name)


    #update summary to reservation stay
    from edoor.api.generate_room_rate import generate_new_room_rate
    generate_new_room_rate(stay_names=stay_names,run_commit=False)
    generate_room_occupies(stay_names,run_commit=False)
    # frappe.enqueue("edoor.api.generate_room_rate.generate_forecast_revenue",queue='short', stay_names=stay_names, run_commit = False )
    generate_forecast_revenue(stay_names=stay_names,run_commit=False)
    
    update_reservation_stay_and_reservation(reservation = reservation.name, reservation_stay=stay_names,run_commit=False)
    
    frappe.db.commit()

    
    frappe.msgprint("Add new reservation successfully")
    return reservation

 
def get_package_item_for_reservation_stay(rate_type):
    rate_type_doc = get_rate_type_doc(rate_type)
    package_items = []
    if rate_type_doc.is_package:
        account_code = get_account_code_doc(rate_type_doc.account_code)
        if account_code.packages:
            for p in account_code.packages:
                package_items.append( {
                    "account_code": p.account_code ,
                    "posting_rule": p.posting_rule,
                    "charge_rule": p.charge_rule,
                    "rate":p.rate,
                    "adult_rate":p.adult_rate,
                    "child_rate":p.child_rate,
                    "allow_user_to_edit_information":rate_type_doc.allow_user_to_edit_rate,
                    "is_rate_type_package":1,
                    "breakdown_account_code": p.breakdown_account_code or "",
                    "discount_breakdown_account_code": p.discount_breakdown_account_code or "",
                    "tax_1_breakdown_account_code": p.tax_1_breakdown_account_code or "",
                    "tax_2_breakdown_account_code": p.tax_2_breakdown_account_code or "",
                    "tax_3_breakdown_account_code": p.tax_3_breakdown_account_code or "",
                     
                })
                
    return package_items

@frappe.whitelist()
def test_generate_room_occupy():
    
    import time


    start_time = time.time()


    data = frappe.db.sql("select name from `tabReservation Stay` where reservation='RS2024-0749'",as_dict=1)
    # new method
    generate_room_occupies([d["name"] for d in data ])
    
    

    end_time = time.time()


    duration = end_time - start_time
    return ("Execution duration:", duration, "seconds")
    
    

def validate_room_type_availability(doc):
    if not frappe.db.get_single_value("eDoor Setting","enable_over_booking")==1:
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
    #CHECK ROOM OVER BOOKING
    if not frappe.db.get_single_value("eDoor Setting","enable_over_booking")==1:
        room_type_ids = set([d["room_type_id"] for d in data["reservation_stays"]])
        for rt in room_type_ids:
        
            total_rooms = len( [d["room_type_id"] for d in data["reservation_stays"] if d["room_type_id"] == rt])
            available_room = check_room_type_availability(
                        property=reservation.property,
                        room_type_id=rt,
                        start_date=data["arrival_date"],
                        end_date=data["departure_date"],
                    )
            
            vacant_room = available_room[0]["total_vacant_room"]

            if total_rooms>vacant_room:
                frappe.throw("You don't have enought room for room type {}. Room available {}, but you book {}".format(available_room[0]["room_type"], 0 if vacant_room< 0 else vacant_room, total_rooms))
 
    #END VALIDATE ROOM OVER BOOKING
    stay_doc_names = []
    for d in data["reservation_stays"]:
         
        if data['departure_date'] <= data['arrival_date']:
            frappe.throw("Departure date cannot less than or equal to arrival date")

        stay = {
            "doctype":"Reservation Stay",
            "reservation":reservation.name,
            "reservation_status":"Reserved" if ((d["room_id"] or None) if 'room_id' in d else None)  else "Confirmed",
            "reservation_color": reservation.reservation_color,
            "arrival_time":reservation.arrival_time,
            "departure_time":reservation.departure_time,
            "tax_rule":data["tax_rule"],
            "rate_include_tax":data["rate_include_tax"] or "No",
            "tax_1_rate":data["tax_1_rate"] or 0,
            "tax_2_rate":data["tax_2_rate"] or 0,
            "tax_3_rate":data["tax_3_rate"] or 0,
            "note":reservation.note,
            "child":d["child"],
            "adult":d["adult"],
            "stays": [{
                "room_type_id": d["room_type_id"],
                "room_id": d["room_id"] or None if 'room_id' in d else None,
                "input_rate":d["rate"] or 0,
                "guest":reservation.guest,
                "reservation_status":"Reserved" if ((d["room_id"] or None) if 'room_id' in d else None)  else "Confirmed",
                "start_date":data["arrival_date"],
                "end_date":data["departure_date"],
                "business_source":reservation.business_source,
                "child":d["child"],
                "adult":d["adult"],
                "start_time":reservation.arrival_time,
                "end_time":reservation.departure_time,
                "is_manual_rate":d["is_manual_rate"]
            }],
            "inclusion_items":get_package_item_for_reservation_stay(reservation.rate_type)
        }
        stay_doc =  frappe.get_doc(stay).insert()
        stay_doc_names.append(stay_doc.name)


    #update master
    if not frappe.db.exists("Reservation Stay", {"reservation": reservation.name,"is_master":1,"is_active_reservation":1}):
        stay_name   = frappe.db.sql("select name from `tabReservation Stay` where reservation='{}' limit 1".format(reservation.name),as_dict=1)
        if len(stay_name)>0:
            stay_doc = frappe.get_doc("Reservation Stay", stay_name[0]["name"])
            stay_doc.is_master = 1
            if len(stay_doc.stays)>0:
                stay_doc.stays[0].is_master = 1
            stay_doc.flags.ingnore_validate = True
            stay_doc.flags.ingnore_on_update = True
            stay_doc.save(ignore_permissions=True)
            
        





    # frappe.enqueue("edoor.api.generate_occupy_record.generate_room_occupies",queue='default', stay_names=stay_doc_names)
    generate_room_occupies(stay_names = stay_doc_names,run_commit=False)
    generate_new_room_rate(stay_names = stay_doc_names,run_commit=False)
    generate_forecast_revenue(stay_names = stay_doc_names,run_commit=False)
    
    update_reservation_stay_and_reservation( reservation = reservation.name, reservation_stay=stay_doc_names,run_commit=False)
    frappe.db.commit()
    return reservation


@frappe.whitelist()
def dome():
    start_time = time.time() 
    get_account_code_doc.cache_clear()
    data =  post_charge_to_folio_afer_check_in(
        reservation="RS2024-0979",
        stays=[{"stay_name":"ST2024-5504"}],
        working_day={'date_working_day': "2024-05-28", 'name': 'WD2024-0013', 'cashier_shift': {'creation': "2024-05-28", 'shift_name': 'Morning Shift', 'name': 'CS2024-0023'}, 'stock_location': 'Main Warehouse'},
        master_folio=get_master_folio(reservation="RS2024-0979",create_if_not_exists=True, reopen_folio_if_closed=True)
    )
    
    end_time = time.time()
    duration = end_time - start_time
    return (duration, data)

@frappe.whitelist(methods="POST")
def check_in(reservation,reservation_stays=None,is_undo = False,note="",arrival_time=None):
    
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
    
    get_account_code_doc.cache_clear()
    get_account_code_sub_account_information.cache_clear()

    check_user_permission("check_in_role")
    
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
    if frappe.db.count('Reservation Stay', {'is_master': 1,"reservation":reservation})>0:
        if not is_master_room_check_in(doc.name,reservation_stays):
            frappe.throw("Please check in master room first")
  

    comment_doc = [] 
    checked_in_stays = []
    noshow_check_in_stays = []
    for s in stays:
        stay = frappe.get_doc("Reservation Stay", s)
        is_no_show =( stay.reservation_status == 'No Show')
        if stay.reservation_status in ["Reserved","Confirmed","No Show"]:
            comment = {
                "subject":"Checked In",
                "reference_doctype":"Reservation Stay",
                "reference_name":stay.name,
                "custom_audit_trail_type":"Check In",
                "custom_icon":"pi pi-sign-in",
                "content": f"Reservation stay #: {stay.name}, Ref. #: {stay.reference_number}, Room #: {stay.rooms}, Guest: {stay.guest}-{stay.guest_name}"}
            if note:
                comment["content"] = comment["content"] + f"<br/> Note: {note}"
            comment_doc.append(comment)



            if frappe.db.count('Reservation Stay', {'is_master': 1,"reservation":reservation})==0:
                if s == stays[0]:
                    stay.is_master = 1


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
                #chekc if user check in a no show reservtion on departure date
                if getdate(working_day["date_working_day"]) == getdate(stay.departure_date):
                    frappe.throw("You cannot Check In No Show reservation on Departure Date")


            #validate check if current room is still have guest in house
            room_id = stay.stays[0].room_id
            check_room_in_house = frappe.db.sql("select name from `tabRoom Occupy` where  room_id='{}' and date between '{}' and '{}' and reservation_status='In-house' and reservation_stay !='{}' limit 1".format(room_id,  stay.arrival_date,add_to_date( stay.departure_date,days=-1),stay.name),as_dict=1)    
            if check_room_in_house:
                frappe.throw("Stay # {}, Room {} still have guest In-house.".format(stay.name, stay.stays[0].room_number))

            
            stay.checked_in_by = frappe.session.user
            stay.checked_in_date = frappe.utils.now()
            if stay.reservation_status == 'No Show':
                stay.checked_in_system_date = working_day["date_working_day"]
                if not stay.arrival_date == stay.checked_in_system_date:
                    # we store this for run enquere job
                    noshow_check_in_stays.append(stay.name)

            else:
                stay.checked_in_system_date = stay.arrival_date

            stay.reservation_status = "In-house"
            if arrival_time:
                stay.arrival_time =  arrival_time
            stay.save()




            #update room housekeeing status to occupy clean
            room_id = stay.stays[0].room_id
            room = frappe.get_doc("Room",room_id)
            room.room_status = "Occupy"
            room.reservation_stay = stay.name
            room.save()
            
            checked_in_stays.append({"stay_name":stay.name,"paid_by_master_room": stay.paid_by_master_room})
            
            if is_no_show:
                generate_forecast_revenue(stay_names=[stay.name],run_commit=False)
                


    if len(checked_in_stays)> 0:
        # create master folio and post master post change to master folio first   
        master_folio = get_master_folio(reservation=reservation,create_if_not_exists=True, reopen_folio_if_closed=True)  
        post_charge_to_folio_afer_check_in(working_day=working_day, 
                                                  reservation=reservation,
                                                  stays=checked_in_stays,
                                                  master_folio=master_folio,
                                                  run_commit=False)
        
    
       
            
        
        frappe.enqueue("edoor.api.utils.update_reservation_stay_and_reservation", queue='short', reservation=reservation,reservation_stay=[d["stay_name"] for d in checked_in_stays])
    
    if len(noshow_check_in_stays)> 0:
        update_room_occupy_information_after_no_show_check_in(noshow_check_in_stays)



    frappe.msgprint(_("Check in successfully"))
    
    frappe.db.commit()
    #enqueue add comment
    frappe.enqueue("edoor.api.utils.add_audit_trail", data =comment_doc,  queue='long')


 
    
    return {
        "reservation":doc
    }

 

@frappe.whitelist()
def update_sub_package_charge_to_folio_transaction(folio_transaction_name=None, folio_transaction_names=None, reservation_stay=None, reservation=None,reservation_folio=None,reservation_folios=None):
    if folio_transaction_name:
        data =frappe.db.sql("select sum(total_amount) as amount from `tabFolio Transaction` where  reference_folio_transaction='{}'".format(folio_transaction_name) ,as_dict=1)
        if data:
            frappe.db.sql("update `tabFolio Transaction` set total_sub_package_charge={} where name='{}'", data[0]["amount"],folio_transaction_name)
    elif reservation_folio:
        data =frappe.db.sql("select reference_folio_transaction, sum(total_amount) as amount from `tabFolio Transaction` where  coalesce(reference_folio_transaction,'')!='' and transaction_number='{}' and transaction_type='Reservation Folio' group by reference_folio_transaction".format(reservation_folio) ,as_dict=1)
        for d in data:
            frappe.db.sql("update `tabFolio Transaction` set total_sub_package_charge={} where name='{}'", d["amount"],d["reference_folio_transaction"])
    elif reservation_folios:
        data =frappe.db.sql("select reference_folio_transaction, sum(total_amount) as amount from `tabFolio Transaction` where coalesce(reference_folio_transaction,'')!='' and transaction_number in %(reservation_folio)s and transaction_type='Reservation Folio' group by reference_folio_transaction",{"reservation_folio":reservation_folios} ,as_dict=1)
        for d in data:
            frappe.db.sql("update `tabFolio Transaction` set total_sub_package_charge={} where name='{}'".format( d["amount"],d["reference_folio_transaction"]))
        

    frappe.db.commit()


            

@frappe.whitelist(methods="POST")
def undo_check_in(reservation_stay, reservation, property,note=""):
    #validate status and date
    #validate working day in doc method
    #validate user role from edoor setting role
    #delete all auto post under current stay folio
    
    stays = []
    if isinstance(reservation_stay, list):
        stays=reservation_stay
    else:
        stays.append(reservation_stay)

    check_user_permission("undo_check_in_role")
    
    working_day = get_working_day(property)
    if not working_day["cashier_shift"]:
        frappe.throw("There is no cashier shift open. Please open cashier shift first")   
    comment_doc = []

    for s in stays:
        doc = frappe.get_doc("Reservation Stay", s)
        comment = {
                "subject":"Undo Checked In",
                "reference_doctype":"Reservation Stay",
                "reference_name":s, 
                "custom_audit_trail_type":"Undo",
			    "custom_icon":"pi pi-replay",
                "content": f"Reservation stay #: {doc.name}, Ref. #: {doc.reference_number}, Room #: {doc.rooms}, Guest: {doc.guest}-{doc.guest_name}"}

        if note:
            comment["content"] = comment["content"] + f"<br/> Note: {note}"

        comment_doc.append(comment)
        #validate status
        if doc.reservation_status !="In-house":
            frappe.throw("Reservation status of stay # {} must be In-house".format(s))

        #validate arrival date

        if getdate(doc.arrival_date)!=getdate(working_day["date_working_day"]):
            if frappe.db.get_single_value("eDoor Setting","allow_user_to_add_back_date_transaction")==1:
                check_user_permission("role_for_back_date_transaction","Sorry you don't have permission to perform back date transaction")
            else:
                frappe.throw("Arrival date of reservation stay # {} must be equal to current working date".format(s))
        
  

        doc.checked_in_by = None
        doc.checked_in_date = None
        doc.checked_in_system_date = None
        
        
        doc.reservation_status = 'Reserved'
        
        doc.save()
    
        #update housekeeping status to room
        room_id = doc.stays[0].room_id
        room = frappe.get_doc("Room",room_id)
        room.room_status = "Vacant"
        room.reservation_stay = None
        room.save()
        

        #delete auto post transaction
        folio_numbers = frappe.db.sql("""select distinct transaction_number from `tabFolio Transaction` where reservation_stay = '{0}' and is_auto_post=1 and transaction_type='Reservation Folio' 
                                      and 
                                      reservation_room_rate in (select name from `tabReservation Room Rate` where reservation_stay='{0}')
                                      """.format(s),as_dict=1)
        
        frappe.db.sql("delete from `tabFolio Transaction` where is_auto_post=1 and reservation_room_rate in (select name from `tabReservation Room Rate` where reservation_stay='{}')".format(s))

        folio_numbers = frappe.db.sql("select name from `tabReservation Folio` where reservation_stay='{}'".format(s), as_dict = 1)
        if folio_numbers:
            for f in folio_numbers:
                frappe.enqueue("edoor.api.folio_transaction.update_reservation_folio", queue='default', name=f["name"], doc=None, run_commit=True )
                

        #end loop stay
        

    frappe.enqueue("edoor.api.utils.update_reservation_stay_and_reservation", queue='short', reservation = reservation, reservation_stay=stays)
    
    frappe.enqueue("edoor.api.utils.add_audit_trail", queue='long', data=comment_doc)
    
    return doc

@frappe.whitelist()
def update_room_occupy_information_after_no_show_check_in(stay_names):
    for stay_name in stay_names:
        arrival_date, checked_in_date = frappe.db.get_value("Reservation Stay",stay_name,["arrival_date","checked_in_system_date"])
        if not  arrival_date== checked_in_date:
            frappe.db.sql("Update `tabRoom Occupy` set is_arrival=if(date='{0}',1,0),is_active=if(date>='{0}',1,0) where date<='{0}' and reservation_stay='{1}' and is_active=1".format(checked_in_date, stay_name))
    frappe.db.commit()

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

    # reservation stay is array
    # validate user role
    # validate cashier shift 
    # remove guest and stay number from room


    check_user_permission("check_out_role")
 
     
    doc = frappe.get_doc("Reservation",reservation)
    if not reservation:
        frappe.throw("There is no reservation to check out")

    working_day = get_working_day(doc.property)
   
    if not working_day["cashier_shift"]:
        frappe.throw("There is no cashier shift open. Please open cashier shift first")   

    #validate if user check out master room first
    # check if stay list is have master room include
    master_stay_data = frappe.db.sql("select name from `tabReservation Stay` where name in %(reservation_stays)s and is_master=1",{"reservation_stays":reservation_stays},as_dict=1)
    if len(master_stay_data)>0:
        data = frappe.db.sql("select name from `tabReservation Stay` where reservation_status in ('In-house','Reserved', 'Confirmed') and  reservation=%(reservation)s and name not in %(reservation_stays)s and paid_by_master_room=1 ",{
            "reservation":reservation,
            "reservation_stays":reservation_stays
        },as_dict=1)
        if len(data)> 0:
            frappe.throw("You cannot check out master room, because there's reservation stay that mark as paid by master room is still remaining.")
    
    currency_precision = frappe.db.get_single_value("System Settings","currency_precision")
    comment_doc = []

    for s in reservation_stays:
        stay = frappe.get_doc("Reservation Stay", s)
        if stay.reservation_status=="Checked Out":
            frappe.throw("Stay # {}. Room {}. This room is already check out.".format(stay.name, stay.rooms))
        if not (stay.departure_date <= working_day["date_working_day"] or stay.departure_date ==add_to_date (working_day["date_working_day"] ,days=1)):
            frappe.throw("Reservation Stay {}, room {} cannot check out because the departure date is in the future.".format(stay.name,stay.rooms))
        #validate folio balance
        data_balance = frappe.db.sql("select max(balance) as balance from `tabReservation Folio` where reservation_stay='{}'".format(stay.name),as_dict = 1)
        
        if data_balance:
            balance = data_balance[0]["balance"] or 0
            if abs(balance)> 0 and  abs(round(balance, int(currency_precision)))> (Decimal('0.1') ** int(currency_precision)):
                frappe.throw("Reservation Stay {}, room {} cannot check out because the folio balance of this reservation stay is greater than zero".format(stay.name,stay.rooms))

        stay.checked_out_by = frappe.db.get_value("User", frappe.session.user,"full_name")
        stay.checked_out_date = now()
        stay.checked_out_system_date = working_day["date_working_day"]
        stay.is_early_checked_out = 0 if getdate(working_day["date_working_day"]) == getdate(stay.departure_date) else 1
        stay.reservation_status = "Checked Out"
        
        stay.save()

        #update room status
        #get last stay room form temp occupy
        last_stay_room = frappe.db.sql("select room_id from `tabReservation Stay Room` where parent='{}' order by departure_date desc limit 1".format(stay.name), as_dict=1)
        for r in last_stay_room:
            room_doc = frappe.get_doc("Room", r["room_id"])
            room_doc.housekeeping_status_code = "Dirty"
            room_doc.room_status= "Vacant"

            room_doc.guest = None
            room_doc.reservation_stay = None 
            room_doc.save()
        
        #close all open folio

        frappe.db.sql("update `tabReservation Folio` set status = 'Closed',reservation_status='Checked Out',reservation_status_color='{}' where reservation_stay='{}'".format(stay.status_color,s))

        #check if early check out then remvoe last row
        if stay.is_early_checked_out == 1:
            #delete last stay date from room occupy
            frappe.db.sql("delete from `tabRoom Occupy` where reservation_stay='{}' and date='{}'".format(stay.name, stay.departure_date))

            #update last stay date is departure = 1 and is_active = 1
            

            # frappe.throw("update `tabRoom Occupy` set is_departure=1,is_active=1,drop_off={} where reservation_stay='{}' and date='{}'".format(stay.require_drop_off, stay.name, stay.checked_out_system_date))
            frappe.db.sql("""
                            update `tabRoom Occupy` set 
                                is_departure=1,
                                is_active=1,
                                drop_off={}
                            where 
                                reservation_stay='{}' and 
                                date='{}'"""
                    .format(stay.require_drop_off, stay.name, stay.checked_out_system_date))

        #update reservation status
        frappe.db.sql("update  `tabRoom Occupy` set reservation_status='{}' where reservation_stay='{}'".format(stay.reservation_status, stay.name))

        #add to audit trail
        comment = {
            "subject":"Checked Out",
            "reference_doctype":"Reservation Stay",
            "reference_name":s,
            "custom_audit_trail_type":"Checked Out",
			"custom_icon":"pi pi-sign-out",
            "content": f"Reservation stay #:<a data-action='view_reservation_stay_detail' data-name='{stay.name}'> {stay.name}</a>, Reservation #:<a data-action='view_reservation_detail' data-name='{stay.reservation}'> {stay.reservation}</a>, Ref. #: {stay.reference_number}, Room #: {stay.rooms}, Guest:<a data-action='view_guest_detail' data-name='{stay.guest}'> {stay.guest}-{stay.guest_name}</a>"
        }

        comment_doc.append(comment)

        
    frappe.enqueue("edoor.api.utils.update_reservation", queue='short', name=reservation)

    
    
    


    frappe.db.commit()


    #enqueu remove record from temp room occupy
    frappe.enqueue("edoor.api.utils.remove_temp_room_occupy", queue='long', reservation=reservation)
    frappe.enqueue("edoor.api.utils.add_audit_trail", queue='long', data=comment_doc)
    return {
        "reservation":doc
    }


@frappe.whitelist(methods="POST")
def undo_check_out(property=None, reservation = None, reservation_stays=None,note=""):
    stay_doc = {}
    working_day = get_working_day(property)
    #validate backdate 
    #validate role

    check_user_permission("undo_check_out_role")
    allow_back_date = frappe.db.get_single_value("eDoor Setting","allow_user_to_add_back_date_transaction")
    comment_doc = []
    
    # validate room occupy
    if int(frappe.db.get_single_value("eDoor Setting","enable_over_booking"))!=1:
        for s in reservation_stays:
            room_stay_data = frappe.db.sql("select room_id,room_number,start_date,end_date from `tabReservation Stay Room` where parent='{}'".format(s),as_dict=1)
            if (len(room_stay_data)>0):
                for r in room_stay_data:
                    occupied  =frappe.db.sql("select room_id, date from `tabTemp Room Occupy` where room_id=%(room_id)s and date between %(start_date)s and %(end_date)s order by date desc limit 1",
                                            {
                                                "room_id":r["room_id"],
                                                "start_date":r["start_date"],
                                                "end_date":add_to_date(r["end_date"], days=-1)
                                            },
                                            as_dict = 1)
                    if len(occupied):
                        frappe.throw("Room number {} is not available on {}".format( r["room_number"],frappe.format_value(occupied[0]["date"], "Date")))

    for s in reservation_stays:
        stay_doc = frappe.get_doc("Reservation Stay", s)
        is_early_checked_out_reservation = stay_doc.is_early_checked_out
        #validate backdate
        if getdate(stay_doc.departure_date)<getdate(working_day["date_working_day"]):
            validate_backdate_permission()

        if (stay_doc.reservation_status =="Checked Out" and stay_doc.departure_date >= working_day["date_working_day"] ) or (stay_doc.reservation_status =="Checked Out" and int(allow_back_date)==1):
            stay_doc.reservation_status = "In-house"
            stay_doc.flags.is_undo_check_out = True
            stay_doc.is_early_checked_out =0
            stay_doc.checked_out_system_date = None

            stay_doc.save()
            frappe.enqueue("edoor.api.generate_occupy_record.generate_room_occupies", queue='short', stay_names = [stay_doc.name])
            
                   
            #update room status
            last_stay_room = frappe.db.sql("select room_id from `tabReservation Stay Room` where parent='{}' order by departure_date desc limit 1".format(stay_doc.name), as_dict=1)
            if last_stay_room:
                room_doc = frappe.get_doc("Room",last_stay_room[0]["room_id"])
                room_doc.room_status = "Occupy"
                room_doc.guest = stay_doc.guest
                room_doc.reservation_stay = s
                room_doc.save()

        else:
            frappe.throw("This reservation stay {}, room {} is not allow to undo check out".format(stay_doc.name, stay_doc.rooms))
    
        #reopen master folio
        frappe.db.sql("update `tabReservation Folio` set status = 'Open' where reservation_stay='{}' and status='Closed' and is_master=1".format(s))
        
        #add to audit trail
        comment = {
            "subject":"Undo Checked Out",
            "reference_doctype":"Reservation Stay",
            "reference_name":s,
            "custom_audit_trail_type":"Undo",
			"custom_icon":"pi pi-replay",
            "content": f"Reservation stay #:<a data-action='view_reservation_stay_detail' data-name='{stay_doc.name}'> {stay_doc.name}</a>, Reservation #:<a data-action='view_reservation_detail' data-name='{stay_doc.reservation}'> {stay_doc.reservation}</a>, Ref. #: {stay_doc.reference_number}, Room #: {stay_doc.rooms}, Guest:<a data-action='view_guest_detail' data-name='{stay_doc.guest}'> {stay_doc.guest}-{stay_doc.guest_name}</a>"
        }
        if note:
            comment["content"] =  comment["content"] + " <br/> Note: " + note
        comment_doc.append(comment)
        #end add to audit trail

    if reservation:
        
        frappe.enqueue("edoor.api.utils.update_reservation", queue='short', name=reservation,run_commit=True)
    else:
        frappe.enqueue("edoor.api.utils.update_reservation", queue='short', name=stay_doc.reservation ,run_commit=True)
          
    frappe.msgprint("Undo check out successfully")

    frappe.enqueue("edoor.api.utils.add_audit_trail", queue='long', data=comment_doc)



    if not reservation:
        return stay_doc

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

def get_room_rate(property, rate_type, room_type, business_source, date,include_tax_rule=False):
    rate_type_doc = None
    if rate_type:
        rate_type_doc = get_rate_type_doc(rate_type)
    
    sql = "select name from `tabSeason` where '{}' between start_date and end_date limit 1".format(date)
    season = frappe.db.sql (sql, as_dict=1)
    room_type_rate  = frappe.get_value("Room Type", room_type,"rate")
    rate = 0
    filter_data = {
        "property":property, 
       
        "room_type":room_type,
        "rate_type":rate_type,
        "business_source":business_source
    }
    
    if season and rate_type:
        season_id = season[0]["name"]
        filter_data["season_id"] = season_id
        
        sql = """select 
                    max(rate) as rate 
                from `tabRate Plan` 
                where 
                    property=%(property)s and
                    season = %(season_id)s and 
                    room_type_id = %(room_type)s and 
                    rate_type = %(rate_type)s 
                """
 
        if business_source:
            sql_with_business_source = "{} and business_source = %(business_source)s".format(sql)
            data = frappe.db.sql(sql_with_business_source,filter_data, as_dict=1)
            rate = data[0]["rate"] or 0
            
            
        if rate ==0:
            #check rate from rate that dont have business source
            sql = "{} and ifnull(business_source,'') = '' ".format(sql) 
           
            data = frappe.db.sql(sql,filter_data, as_dict=1)
           
            rate = data[0]["rate"] or 0

  
    if rate == 0:
        #if still rate = 0 the  get rate from room type
        if rate_type_doc:
            if rate_type_doc.disable_get_rate_room_room_type ==0:
                rate = room_type_rate
            
    tax_rule = None

    rate_type_info = None
    if include_tax_rule==True:
        rate_type_info= get_rate_type_info(rate_type)
        tax_rule = rate_type_info["tax_rule"]
    
     
    #if have rate type check if rate is allow to discount or note
    allow_discount = 0
    is_house_use = 0
    is_complimentary =0
    if rate_type:
        account_code = rate_type_doc.account_code
        is_house_use = rate_type_doc.is_house_use
        is_complimentary = rate_type_doc.is_complimentary
        if  account_code:
            allow_discount = frappe.db.get_value("Account Code",account_code, "allow_discount")

        if is_house_use == 1 or is_complimentary ==1:
            rate = 0
            tax_rule = None
            allow_discount = 0

    return {"rate":rate,"tax_rule":tax_rule,
            "allow_discount":allow_discount,
            "allow_user_to_change_tax":0 if not rate_type_info else rate_type_info["allow_user_to_change_tax"],
            "is_house_use":is_house_use or 0,
            "allow_user_to_edit_rate":0 if not rate_type_info else rate_type_info["allow_user_to_edit_rate"],
            "is_complimentary":is_complimentary or 0,
            "is_package":0 if not rate_type_info else rate_type_info["is_package"],
            "package_charge_data": '[]'  if not rate_type_info else rate_type_info["package_charge_data"],
        }


#@frappe.whitelist(methods="POST")
@frappe.whitelist()
def change_rate_type(property=None,reservation=None, reservation_stay=None, rate_type = None, apply_to_all_stay = None,regenerate_new_rate=None,rate_include_tax='Yes',tax_rule=None,tax_1_rate=0,tax_2_rate=0,tax_3_rate=0):
    get_package_charge_data.cache_clear()
    get_room_rate_breakdown.cache_clear()
    get_room_rate_account_code_breakdown.cache_clear()
    get_tax_breakdown.cache_clear()
    
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

    is_complimentary, is_house_use = frappe.db.get_value("Rate Type", rate_type,["is_complimentary","is_house_use"])
    
    package_data = []
    rate_type_doc = get_rate_type_doc(rate_type)
    if rate_type_doc.is_package==1:
        package_data = get_package_charge_data(rate_type)
        
    for r in room_rates:
        doc = frappe.get_doc("Reservation Room Rate",r.name)
        doc.rate_type = rate_type
        
        
         
        
        doc.tax_rule = tax_rule
        doc.tax_1_rate = tax_1_rate
        doc.tax_2_rate = tax_2_rate
        doc.tax_3_rate = tax_3_rate
        doc.rate_include_tax = rate_include_tax
        doc.regenerate_rate = regenerate_new_rate
        doc.flags.regenerate_rate = regenerate_new_rate
        
        if is_complimentary ==1 or is_house_use==1:
            doc.input_rate = 0
            doc.package_charge_data = "[]"
            
        if package_data:
            if doc.is_arrival:
                doc.package_charge_data = json.dumps([d for d in package_data if d["posting_rule"] in ["Everyday","Checked In Date"]])
            else:
                doc.package_charge_data = json.dumps([d for d in package_data if d["posting_rule"] in ["Everyday"]])
                    
        doc.flags.ignore_on_update = True
        doc.save(ignore_permissions=True)

    #update rate type to reservation stay
    for s in active_stays:
        doc = frappe.get_doc("Reservation Stay",s)
        doc.rate_type = rate_type
        doc.tax_rule = tax_rule
        doc.tax_1_rate = tax_1_rate
        doc.tax_2_rate = tax_2_rate
        doc.tax_3_rate = tax_3_rate
        doc.rate_include_tax = rate_include_tax
        
        
        doc.update_reservation = False
        doc.flags.ignore_validate =True
        doc.save()
    if active_stays:
        frappe.enqueue("edoor.api.utils.update_reservation_stay", queue='short', stay_names=active_stays, run_commit = True)
        
        
    #disable update to reservation when update stay
    if reservation or apply_to_all_stay:
        reservation_doc = frappe.get_doc("Reservation", reservation)
        reservation_doc.rate_type = rate_type
        reservation_doc.update_reservation = True
        reservation_doc.save()
        frappe.enqueue("edoor.api.utils.update_reservation", queue='short',name=reservation,run_commit=True)
    generate_forecast_revenue(stay_names=active_stays, run_commit=False)
    frappe.db.commit()
    return True

@frappe.whitelist()
def get_current_room_reservation(room_id):

    sql = "select parent from `tabReservation Stay Room` where room_id='{}' and '{}' between start_date and end_date and is_active_reservation=1"
    sql = sql.format(room_id,frappe.utils.today() )
    data = frappe.db.sql(sql, as_dict=1)

@frappe.whitelist()
def get_reservation_comment_note(doctype, docname,):
    data = []
    
    data =  frappe.db.sql("SELECT `name`, creation ,custom_note_date, reference_doctype, reference_name,owner, comment_by as user_full_name,subject, content, comment_type, custom_icon,custom_is_note FROM `tabComment` WHERE comment_type in ('Comment','Info','Deleted','Attachment','Attachment Removed') AND reference_doctype ='{0}' AND reference_name = '{1}' and custom_is_audit_trail=1 order by modified desc limit 20".format(doctype, docname),as_dict=1)
    return data

@frappe.whitelist(methods="POST")
def change_stay(data):
    working_day  =get_working_day(data["property"])
    if not working_day["cashier_shift"]:
        frappe.throw("There is no cashier open. Please open your cashier shift")

    doc = frappe.get_doc("Reservation Stay",data['parent'])
    if doc.reservation_status not in ["Reserved",'In-house',"Confirmed"]:
        frappe.throw( "{} is not allow to change stay".format(doc.reservation_status))

    allow_back_date = frappe.db.get_single_value("eDoor Setting","allow_user_to_add_back_date_transaction")

    room_id = ""
    
    if 'room_id' in data and data["room_id"]:
        room_id = data["room_id"]
    if getdate(data["start_date"]) == getdate(data["end_date"]):
        frappe.throw("Arrival date cannot equal to departure date")
        
    # when we change stay date from drap and drop in room chart calendar we allow to overlap

    if frappe.db.get_single_value("eDoor Setting","enable_over_booking")==0: 
        if room_id:        
            check_room_occupy = frappe.db.sql("select stay_room_id, date from `tabTemp Room Occupy` where is_departure = 0 and date between %(start_date)s and %(end_date)s and stay_room_id<>%(stay_room_id)s and room_id=%(room_id)s limit 1",
                {"start_date":data["start_date"],"end_date":add_to_date(data["end_date"],days=-1),"stay_room_id":data["name"],"room_id":data["room_id"]},
                as_dict = 1
                )
            
            if check_room_occupy:
                frappe.throw(_("You cannot change stay of this reservation. Because this room is not available or block on {}".format(frappe.format(check_room_occupy[0]["date"]),{"fieldtype":"Date"}) ))

        #check room type occupy
        available_room = check_room_type_availability(
            property=data["property"],
            room_type_id=data["room_type_id"],
            start_date=data["start_date"],
            end_date=data["end_date"],
            exclude_stay_room_id=data["name"]
        )

         
        if available_room[0]["total_vacant_room"]<=0:
            frappe.throw("You cannot change stay of this reservation. Because you don't have enough room for room type {}".format(available_room[0]["room_type"]))
    else:
        #check if the room is block
        if room_id:        
            check_room_occupy = frappe.db.sql("select stay_room_id, date from `tabTemp Room Occupy` where type='Block' and date between %(start_date)s and %(end_date)s and stay_room_id<>%(stay_room_id)s and room_id=%(room_id)s limit 1",
                {"start_date":data["start_date"],"end_date":add_to_date(data["end_date"],days=-1),"stay_room_id":data["name"],"room_id":data["room_id"]},
                as_dict = 1
                )
            
            if check_room_occupy:
                frappe.throw(_("You cannot change stay of this reservation. Because this room is not available or block on {}".format(frappe.format(check_room_occupy[0]["date"]),{"fieldtype":"Date"}) ))
            
    
    

    

    #delete all invalid room rate record that stay out site of stay date
    frappe.db.sql("delete from `tabReservation Room Rate` where reservation_stay='{}' and date<'{}'".format(doc.name, doc.arrival_date))
    frappe.db.sql("delete from `tabReservation Room Rate` where reservation_stay='{}' and date>='{}'".format(doc.name, doc.departure_date))
    

    
    #validate move room that have mulltiple stay is not allow to change stay date
    stay_room = [d for d in  doc.stays if d.name ==data["name"]][0]

    if data["is_move"]==1 and len(doc.stays)>1:
            if getdate(stay_room.start_date) != getdate(data["start_date"]) and  getdate(stay_room.end_date) != getdate(data["end_date"]):
                frappe.throw(_("Multiple stay rooms are not allowed to change stay dates during movement"))


        

    #validate if reservation is check in and they and they already stay so we cannot 


    if doc.stays.index(stay_room)==0:
        if getdate( stay_room.start_date) != getdate(data["start_date"]) and  getdate(  working_day["date_working_day"])>= getdate( stay_room.start_date) and doc.reservation_status =='In-house':
            frappe.throw(_("Checked-In reservation is not allow to change arrival date"))
        
        if  getdate(working_day["date_working_day"])>=getdate( stay_room.start_date) and doc.reservation_status =='In-house' and getdate(stay_room.start_date) !=getdate(data["start_date"]) :
            frappe.throw(_("Checked-In reservation is not allow to change arrival date"))


    #check if user move from departure date and move behind current working date 
    if getdate(data["end_date"])< getdate(working_day["date_working_day"]):
        if allow_back_date==1:
                validate_role("role_for_back_date_transaction","You don't have permission to add back date reservation")
        else:
            frappe.throw(_("Depature date must be greater then or equal to current working date"))

        

   
    #check if current dsate date range have room block
    if hasattr(data,"room_id") and data["room_id"]: 
        block_data =frappe.db.sql("select name from `tabTemp Room Occupy` Where  type='Block' and room_id=%(room_id)s and date between %(start_date)s and %(end_date)s",
                                {
                                    "room_id":data["room_id"],
                                    "start_date":data["start_date"],
                                    "end_date":add_to_date(getdate(  data["end_date"]),days=-1)
                                },as_dict=1)
        if block_data:
            frappe.throw("You cannot change stay or extend stay on a block room")

    # validate back date role
    if getdate(data["start_date"])<getdate(working_day["date_working_day"]):
        if doc.reservation_status in ["Reserved","Confirm"]:
            if frappe.db.get_single_value("eDoor Setting","allow_user_to_add_back_date_transaction")==1:
                validate_role("role_for_back_date_transaction","You don't have permission to add back date reservation")
            else:
                frappe.throw("You cannot change arrival date to the back date")
        else:
            if data["name"] == doc.stays[0].name:
                if doc.stays[0].start_date != getdate(data["start_date"]):
                    frappe.throw("{} is not allow to change arrival date".format(doc.reservation_status))
    doc.is_override_rate = 'is_override_rate' in data and data['is_override_rate']
    stays = Enumerable(doc.stays).order_by(lambda x:datetime.strptime(str(x.start_date), '%Y-%m-%d').date()).to_list()
    
    #validate if user change room after checkin and runnight audit
    if data["name"] == stays[0].name:
        if allow_back_date==0 and room_id:
            
            if (doc.reservation_status=='In-house' and room_id != stays[0].room_id) or (doc.reservation_status=='In-house' and getdate(stays[0].start_date)!=getdate(data["start_date"])):
                frappe.throw("In-house reservation is not allow to change date or room number")
    
    for s in stays:
        if s.name == data['name']:
            s.room_type_id=data["room_type_id"]
            if room_id: 
                s.room_id=room_id 

            s.start_date = data['start_date']
            s.end_date = data['end_date']
           
        # change last stay room for start date
        index = stays.index(s) + 1
        if len(stays) > index and stays[index]:
            stays[index].start_date = s.end_date
            if datetime.strptime(str(stays[index].start_date), '%Y-%m-%d').date() >= datetime.strptime(str(stays[index].end_date), '%Y-%m-%d').date():
                frappe.throw("Start date cannot greater than end date.{}".format(str(index)))

    if hasattr(data,"note"):
        doc.change_stay_note = data["note"]  

    doc.save()

    if doc: 
        if data["is_move"]==0:
            update_reservation_stay_room_rate_after_resize(data=data,stay_doc= doc)
        else:
            update_reservation_stay_room_rate_after_move(data=data,stay_doc= doc)
            
 
        # post_room_charge_to_folio_after_extend_stay(stays=[doc.name])
        generate_room_occupies(stay_names = [doc.name],run_commit=False)
        generate_forecast_revenue (stay_names = [doc.name],run_commit=False)
        frappe.db.commit()

        frappe.enqueue("edoor.api.utils.update_reservation_stay_and_reservation", queue='short', reservation = doc.reservation, reservation_stay=doc.name)
        
        
       
    

    frappe.msgprint(_("Change stay successully"))


    return doc
    

def post_room_charge_to_folio_after_extend_stay(stays):
    if frappe.db.get_single_value("eDoor Setting","auto_post_room_charge_folio_on_current_audit_date")==0:
        for s in stays:
            stay_doc = frappe.get_doc("Reservation Stay", s)
            if stay_doc.reservation_status =="In-house":
                working_day = get_working_day(stay_doc.property)
                if getdate( stay_doc.departure_date) > getdate(working_day["date_working_day"]):
                    
                    sql_rate = "select name from `tabReservation Room Rate` where reservation_stay='{}' and date='{}'".format(stay_doc.name, working_day["date_working_day"])
                    room_rates = frappe.db.sql(sql_rate,as_dict=1)
                    
                    if room_rates:
                        room_rate_doc = frappe.get_doc("Reservation Room Rate", room_rates[0]["name"])

                        # check if room chage already post to folio
                        sql="select name,stay_room_id,room_id from `tabFolio Transaction` where coalesce(reservation_room_rate,'')!= '' and source_reservation_stay='{}' and posting_date='{}' and is_auto_post=1".format(stay_doc.name, working_day["date_working_day"])
                        folio_transactions = frappe.db.sql(sql,as_dict=1)
                        if len(folio_transactions)>0:
                            for f in folio_transactions:
                                
                                if f["stay_room_id"] != room_rate_doc.stay_room_id or f["room_id"] != room_rate_doc.room_id:                            
                                    frappe.db.sql("update `tabFolio Transaction` set stay_room_id='{0}',room_id='{1}', room_number={2}, room_type_id='{3}', room_type='{4}' where name='{5}'".format(
                                        room_rate_doc.stay_room_id,
                                        room_rate_doc.room_id,
                                        room_rate_doc.room_number,
                                        room_rate_doc.room_type_id,
                                        room_rate_doc.room_type,
                                        f["name"]
                                        
                                    ))


                        else:
                            # start add charge to filio
                            # get folio post to master or post to self folio
                            folio = get_stay_posting_folio(stay_doc)
                            
                            if folio:
                                add_room_charge_to_folio( folio, room_rate_doc,0,"Room Extended")
                            else:
                                frappe.throw("Please create folio for reservation stay #{}".format(stay_doc.name))

                else:
                    # delete extended room 
                    room_rates= frappe.db.sql("select name from `tabReservation Room Rate` where reservation_stay='{}'".format(stay_doc.name),as_dict=1)
                


                    # get folio data before delete 
                    sql = """
                            select name,transaction_number,posting_date,account_code, account_name, total_amount from `tabFolio Transaction` 
                            where
                                coalesce(parent_reference,'') = '' and  
                                reservation_room_rate not in %(reservation_room_rate)s and 
                                source_reservation_stay = %(source_reservation_stay)s
                            """
                    
                    delete_folios = frappe.db.sql(sql,
                                        {
                                            "source_reservation_stay":stay_doc.name,
                                            "reservation_room_rate": set([d["name"] for d in room_rates])
                                        }
                                        ,as_dict=1)
                    
                    if delete_folios:

                        folio_names = set([d["name"] for d in delete_folios])
                        frappe.db.sql("delete from `tabFolio Transaction` where  name in %(names)s or parent_reference in %(names)s",{
                            "names": folio_names
                        })
                        
                        
                        #update folio balance
                        for d in set([x["transaction_number"] for x in delete_folios]):
                            update_reservation_folio(doc=frappe.get_doc("Reservation Folio",d), run_commit=False)

                        #post to audit trail
                        for f in delete_folios:
                            content = f"""Folio Transaction Deleted when change departure date to the back date. Folio #: {f["transaction_number"] }, Folio Tran. #: {f["name"]}, Date: {frappe.format_value(f["posting_date"],{"fieldtype":"Date"} )}, Account Code: {f["account_code"]} - {f["account_name"]}, Amount: {frappe.format_value(f["total_amount"],{"fieldtype":"Currency"} )}"""

                            frappe.enqueue("edoor.api.utils.add_audit_trail",queue='long', data =[{
                                    "comment_type":"Deleted",
                                    "subject":"Delete Folio Transaction",
                                    "reference_doctype":"Reservation Stay",
                                    "reference_name":stay_doc.name,
                                    "custom_audit_trail_type":"Deleted",
                                    "content":content.strip()
                                }])

                    
                




                    


    
def get_stay_posting_folio(stay_doc):
    data=[]
    if stay_doc.paid_by_master_room==0:
        data = frappe.db.sql("select name from `tabReservation Folio` where reservation_stay='{}' and is_master=1 and status='Open'".format(stay_doc.name),as_dict=1)
    else:
        master_stay_names = frappe.db.sql("select name from `tabReservation Stay` where reservation='{}' and is_master=1 ".format(stay_doc.reservation),as_dict=1)
        if master_stay_names:
            data = frappe.db.sql("select name from `tabReservation Folio` where reservation_stay='{}' and is_master=1 and status='Open'".format(master_stay_names[0]["name"]),as_dict=1)

    if data:
        return frappe.get_doc("Reservation Folio", data[0]["name"])
    return None
        


        
@frappe.whitelist(methods="POST")
def change_reservation_stay_min_max_date(reservation_stay, arrival_date=None, departure_date=None, arrival_time=None, departure_time=None):
    get_rate_type_doc.cache_clear()
    get_package_charge_data.cache_clear()
    get_charge_breakdown_by_account_code_breakdown.cache_clear()
    doc = frappe.get_doc("Reservation Stay",reservation_stay)
    # multiple stays
    if len(doc.stays) > 1:
        frappe.throw("This reservation stay has multiple rooms. Please change in room stay.")
    else:
        #validate if room is not available 
        if frappe.db.get_single_value("eDoor Setting","enable_over_booking")==0:
            if doc.stays[0].room_id:
                data = frappe.db.sql("select stay_room_id, date from `tabTemp Room Occupy`  where is_departure = 0 and date between %(start_date)s and %(end_date)s and stay_room_id<>%(stay_room_id)s and room_id=%(room_id)s limit 1",
                    {"start_date":arrival_date,"end_date":add_to_date(departure_date,days=-1),"stay_room_id":doc.stays[0].name,"room_id":doc.stays[0].room_id},
                    as_dict = 1
                )
        
                if data:
                    frappe.throw(_("You cannot change stay of this reservation. Because this room is not available on {}".format(frappe.format(data[0]["date"]),{"fieldtype":"Date"}) ))

                #check if room type available
                available_room = check_room_type_availability(
                    property=doc.property,
                    room_type_id=doc.stays[0].room_type_id,
                    start_date=arrival_date,
                    end_date=add_to_date(departure_date,days=-1),
                    exclude_stay_room_id=doc.stays[0].name
                )

                if available_room[0]["total_vacant_room"]<=0:
                    frappe.throw("You cannot change stay of this reservation. Because you don't have enough room for room type {}".format(available_room[0]["room_type"]))
            

            else:
                #check if room type available
                available_room = check_room_type_availability(
                    property=doc.property,
                    room_type_id=doc.stays[0].room_type_id,
                    start_date=arrival_date,
                    end_date=add_to_date(departure_date,days=-1)
                )

                if available_room[0]["total_vacant_room"]<=0:
                    frappe.throw("You cannot change stay of this reservation. Because you don't have enough room for room type {}".format(available_room[0]["room_type"]))
        
        default_check_in_date = frappe.db.get_single_value("eDoor Setting","default_check_in_time")
        default_check_out_date = frappe.db.get_single_value("eDoor Setting","default_check_out_time")


        doc.stays[0].start_date = arrival_date
        doc.stays[0].end_date = departure_date
        doc.stays[0].start_time = arrival_time or default_check_in_date
        doc.stays[0].end_time = departure_time or default_check_out_date
        doc.arrival_time = arrival_time or default_check_in_date
        doc.departure_time = departure_time or default_check_out_date
        doc.save()


       

        #generate room rate
        update_reservation_stay_room_rate_after_resize(data= {
            "room_id": doc.stays[0].room_id,
            "property": doc.property,
            "room_type_id": doc.stays[0].room_type_id,
            "start_date": arrival_date,
            "end_date": departure_date,
            "parent": reservation_stay,
            "generate_rate_type": "stay_rate",
            "name": doc.stays[0].name
        },stay_doc= doc)

        generate_room_occupies( stay_names=[doc.name] , run_commit=False )
        
        frappe.enqueue("edoor.api.utils.update_reservation_stay_and_reservation", queue='short', reservation = doc.reservation, reservation_stay=doc.name)
        generate_forecast_revenue(stay_names=[doc.name] , run_commit = False )
        
        frappe.db.commit()
        return doc

@frappe.whitelist(methods="DELETE")
def delete_stay_room(parent,name, note):
    stay = frappe.get_doc('Reservation Stay', parent)
    if stay.allow_user_to_edit_information==0:
        frappe.throw("This reservation stay is not allow user to edit information")

    if len(stay.stays)==1:
        frappe.throw("You cannot delete this stay room record")
    
    if stay.stays[len(stay.stays)-1].name !=name:
        frappe.throw("Please delete last stay room record first")
    stay_room = [d for d in stay.stays if d.name==name][0]
    
    if stay.reservation_status=="In-house":
        
        working_day = get_working_day(stay.property)

        if getdate(stay_room.start_date ) < getdate(working_day["date_working_day"]):
            frappe.throw("You cannot delete this room stay because stay date is less then current working date.")



    for p in stay.stays:
        if p.name == name:
            p.deleted_note = note or ""
            stay.remove(p)
    
    
    if stay.reservation_status in ["Reserved","Confirmed"]:
        if len([d for d in stay.stays if d.room_id])>0:
            stay.reservation_status ="Reserved"
        else:
            stay.reservation_status ="Confirmed"

    stay.save()


    # check if reservation have room charge posting to folio transaction then delete it
    sql = """
            select name,transaction_number,posting_date,account_code, account_name, total_amount from `tabFolio Transaction` 
            where
                coalesce(parent_reference,'') = '' and  
                reservation_room_rate in (
                    select name from `tabReservation Room Rate` where stay_room_id = '{}' 
                )  

            """.format(name)
    data = frappe.db.sql(sql,as_dict=1)
    content =""
    if data:
        # delete from folio transaction
        frappe.db.sql("delete from `tabFolio Transaction` where name in %(names)s or parent_reference in %(names)s",{"names":set([d["name"] for d in data])})
        # post to audit trail
        content = f"""Delete room stay from Res. Stay#: {stay.name},Date: {frappe.format_value(stay_room.start_date,{"fieldtype":"Date"} )} to {frappe.format_value(stay_room.end_date,{"fieldtype":"Date"} )}, Reason: {note}, Folio Transaction Deleted: {data[0]["name"]}, Date: {frappe.format_value(data[0]["posting_date"],{"fieldtype":"Date"} )}, Account Code: {data[0]["account_code"]} - {data[0]["account_name"]}, Amount: {frappe.format_value(data[0]["total_amount"],{"fieldtype":"Currency"} )}"""

        for d in set([x["transaction_number"] for x in data]):
            update_reservation_folio(doc=frappe.get_doc("Reservation Folio",d), run_commit=False)
                    
    else:
        content = f"""Delete room stay from Res. Stay#: {stay.name}, Date: {frappe.format_value(stay_room.start_date,{"fieldtype":"Date"} )} to {frappe.format_value(stay_room.end_date,{"fieldtype":"Date"} )}  Reason: {note}"""

    frappe.enqueue("edoor.api.utils.add_audit_trail",queue='long', data =[{
            "comment_type":"Deleted",
            "subject":"Delete Stay Room",
            "reference_doctype":"Reservation Stay",
            "reference_name":stay.name,
            "custom_audit_trail_type":"Deleted",
            "content":content.strip()
        }])





    if stay:
        frappe.db.sql("delete from `tabReservation Room Rate` where stay_room_id='{}'".format(name))
        frappe.enqueue("edoor.api.utils.update_reservation_stay_and_reservation", queue='short', reservation = stay.reservation, reservation_stay=stay.name)
        generate_room_occupies(stay_names=[stay.name],run_commit=False)
        generate_forecast_revenue(stay_names=[stay.name], run_commit=False)
        
    update_is_arrival_date_in_room_rate(stay.name, run_commit=False)

    frappe.db.commit()
    return stay

@frappe.whitelist(methods="POST")
def update_note(data):

    note = '' if data.get("note") is None else data['note']
    housekeeping_note = '' if data.get("housekeeping_note") is None else data['housekeeping_note']
    doc = frappe.get_doc(data['doctype'], data['name'])
    doc.note = note
    doc.housekeeping_note = housekeeping_note
    doc.flags.ingore_validate = True
    doc.save()

    # apply reservation
 
    if(data['is_apply_reseration']):
        reseration = frappe.get_doc('Reservation', data['reservation'])
        reseration.note = note
        reseration.housekeeping_note = housekeeping_note
        reseration.save() 
        
    # apply all stays
    if(data['is_apply_all_stays']):
        reservation_stays = frappe.get_list('Reservation Stay',filters={"reservation":data['reservation'],"is_active_reservation":True})
        for s in reservation_stays:
            reservation_stay_doc = frappe.get_doc('Reservation Stay', s)
            reservation_stay_doc.note = note
            reservation_stay_doc.housekeeping_note = housekeeping_note
            reservation_stay_doc.save()

    frappe.db.commit()
    return doc

@frappe.whitelist(methods="POST")
def update_reservation_status(reservation, stays, status, note,reserved_room=True):
    if status=="Cancelled":
        check_user_permission("cancel_reservation_role")
    elif status=="No Show":
        check_user_permission("no_show_reservation_role")    
    elif status=="Void":
        check_user_permission("void_reservation_role")


    doc_reservation = frappe.get_doc("Reservation", reservation)
    currency_precision = frappe.db.get_single_value("System Settings","currency_precision")

    working_day =get_working_day(doc_reservation.property)
    if not working_day["cashier_shift"]:
        frappe.throw("Please start cashier shift first") 
    comment_doc = []
    for s in stays:
        if not  s["reservation_status"] in ["Reserved" , "Confirmed"]:
            frappe.throw("You can {} on Confirmed and Reserved reservation only".format(status))
        stay = frappe.get_doc('Reservation Stay', s['name'])
        #check if currentr working day is not equal to arrival date
 
        if getdate( stay.arrival_date) != getdate(working_day["date_working_day"]) and status=="No Show":
            frappe.throw("Reservation stay {}, room {}, Arrival date of date of No Show reservation must be equal to current working date".format(stay.name,stay.rooms ))
        
        #validate folio balance
        data_balance = frappe.db.sql("select max(balance) as balance from `tabReservation Folio` where reservation_stay='{}'".format(stay.name),as_dict = 1)
        balance = 0
        if data_balance:
            balance = data_balance[0]["balance"] or 0

        
        

        if balance !=0 and abs(round(balance, int(currency_precision)))> (Decimal('0.1') ** int(currency_precision)):
            frappe.throw("You have folio balance in reservation stay {}. To {} a reservation, balace must be 0".format(stay.name, status))

        
        stay.reservation_status = status
        stay.reservation_status_note = note
        stay.is_active_reservation = False

        if status=="No Show":
            stay.is_reserved_room = (1 if reserved_room ==True else 0)

        stay.cancelled_note = note
        stay.cancelled_by = frappe.db.get_value("User", frappe.session.user,"full_name")
        
        stay.cancelled_date = working_day["date_working_day"]
        stay.save()
        #update is active reservation to room rate 
        frappe.db.sql("update `tabReservation Room Rate` set is_active_reservation = 0 where reservation_stay='{}'".format(s['name']))
        
        if status!="No Show":
            #void and cancel
            frappe.db.sql("delete from `tabTemp Room Occupy` where reservation_stay=%(reservation_stay)s",
                          {"reservation_stay":stay.name})
            
            frappe.db.sql("delete from `tabRoom Occupy` where reservation_stay=%(reservation_stay)s",
                          {"reservation_stay":stay.name})
            
        else:
            if not reserved_room:
                #No Show but not reserve room
                frappe.db.sql("delete from `tabTemp Room Occupy` where reservation_stay=%(reservation_stay)s",
                          {"reservation_stay":stay.name})
            
                frappe.db.sql("delete from `tabRoom Occupy` where reservation_stay=%(reservation_stay)s",
                            {"reservation_stay":stay.name})

        #close all folio
        if status in ["Cancelled","No Show","Void"]:
            # delete revenue from revenue forecast breakdown
            frappe.db.sql("delete from `tabRevenue Forecast Breakdown` where reservation_stay=%(reservation_stay)s",
                          {"reservation_stay":stay.name}) 
            color = frappe.db.get_value("Reservation Status",status,"color")
            
            frappe.db.sql("update `tabReservation Folio` set status = 'Closed', reservation_status_color='{1}' where reservation_stay='{0}'".format(stay.name,color))

        #create audit trail
        comment = {
            "reference_doctype":"Reservation Stay",
            "reference_name":stay.name,
            "subject": stay.reservation_status + " Reservation Stay",

        }
        comment["content"] = f"{stay.reservation_status} reservation stay. Reservation #: <a data-action='view_reservation_detail' data-name='{stay.reservation}'>{stay.reservation}</a>, reservation stay #: <a data-action='view_reservation_stay_detail' data-name='{stay.name}'>{stay.name}</a>, Room: {stay.rooms}, Guest:<a data-action='view_guest_detail' data-name='{stay.guest}'>{stay.guest} - {stay.guest_name}</a>"
        if stay.reservation_status =='No Show':
            comment["content"] = comment["content"] + f", reserved room: {'Yes' if reserved_room else 'No'}"
        if note:
            comment["content"] = comment["content"] + "<br/> Note: " + note
        comment_doc.append(comment)

        
     
    #check if reservation dont have master stay room then update date the first active reservation to master room

    frappe.enqueue("edoor.api.utils.update_reservation", queue='short', name=doc_reservation.name, doc=None, run_commit=True)

    frappe.db.commit()

    frappe.msgprint("{} reservation successfully".format(status))
    frappe.enqueue("edoor.api.reservation.update_master_room", queue='short', reservation=reservation)
    frappe.enqueue("edoor.api.utils.add_audit_trail", queue='long', data=comment_doc)
    frappe.enqueue("edoor.api.reservation.update_reservation_room_rate", queue='long', stays=[s["name"] for s in stays])

  

    return stays

@frappe.whitelist()
def update_reservation_room_rate(stays):
    for s in stays:
        is_active_reservation, is_reserved_room = frappe.db.get_value("Reservation Stay",s,["is_active_reservation","is_reserved_room"])
        frappe.db.sql("update `tabReservation Room Rate` set is_active={} where reservation_stay='{}'".format(
            1 if is_active_reservation or is_reserved_room else 0,
            s
        ))

    frappe.db.commit()


def update_master_room(reservation):
    pass
    sql = "select  name from `tabReservation Stay` where is_active_reservation=1 and reservation='{}' and is_master=1".format(reservation)
    data = frappe.db.sql(sql,as_dict=1)
    if not data:
        frappe.db.sql("update `tabReservation Stay` set is_master=0 where reservation='{}'".format(reservation) )
        frappe.db.commit()
        sql = "select  name from `tabReservation Stay` where is_active_reservation=1 and reservation='{}' limit 1".format(reservation)
        data = frappe.db.sql(sql,as_dict=1)
        if data:
            frappe.db.sql("update `tabReservation Stay` set is_master=1 where name ='{}'".format(data[0]["name"]) )
            frappe.db.commit()



@frappe.whitelist()
def get_folio_transaction(transaction_type="", transaction_number="",reservation="",reservation_stay="",show_account_code="-1", breakdown_account_code = "0"):

    if cint(breakdown_account_code) ==1:
        return get_folio_transaction_with_breakdown_account_code(transaction_type=transaction_type, transaction_number=transaction_number,reservation=reservation, reservation_stay=reservation_stay,show_account_code=show_account_code)
        
    else:
        return get_folio_transaction_without_breakdown_account_code(transaction_type=transaction_type, transaction_number=transaction_number,reservation=reservation, reservation_stay=reservation_stay,show_account_code=show_account_code)
        
@frappe.whitelist()
def get_folio_transaction_with_breakdown_account_code(transaction_type="", transaction_number="",reservation="",reservation_stay="",show_account_code="-1"):
    if show_account_code =="-1":
        show_account_code = frappe.db.get_single_value("eDoor Setting","show_account_code_in_folio_transaction")==1
    else:
        show_account_code = int(show_account_code)

   
    filters={
        "parent_reference":""
    }

    if transaction_type:
        filters["transaction_type"]=transaction_type
    if transaction_number:
        filters["transaction_number"]=transaction_number
    if reservation:
        filters["reservation"]=reservation
    if reservation_stay:
        filters["reservation_stay"]=reservation_stay
        
    data = frappe.db.get_list("Folio Transaction", fields=["*"], filters=filters, page_length=1000, order_by='name')
    
 

  
    # data = frappe.db.sql(sql,as_dict=1)

    balance = 0
    folio_transactions = []
    for d in data:
        if  d.bank_fee_amount > 0:
            balance = balance + d.bank_fee_amount
          
            folio_transactions.append({ 
                "reservation":d["reservation"],
                "name":d["name"],
                "room_number":d.room_number,
                "account_name": "{}-{}".format(d.bank_fee_account, d.bank_fee_description)  if show_account_code else d.bank_fee_description,
                "quantity": d["report_quantity"],
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
                "is_auto_post":d["is_auto_post"],
                "total_amount":d["total_amount"]

            })


      
        #this is main transaction
        amount = d.total_amount
         
        # if d.rate_include_tax=="Yes":
        #     amount =( amount - d.total_tax ) + d.discount_amount
        
        balance = balance + (amount * (1 if d.type=="Debit" else -1))        


        folio_transactions.append({ 
            "reservation":d["reservation"],
            "name":d["name"],
            "room_number":d.room_number,
            "account_name": "{}-{}".format(d.account_code, d.report_description or d.account_name)  if show_account_code else (d.report_description or d.account_name) ,
            "quantity": d["report_quantity"],
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
             "is_auto_post":d["is_auto_post"],
             "total_amount":d["total_amount"],
              "sale":d.sale,
              "tbl_number":d.tbl_number,
              "is_package":d.is_package
        })
        
        if  d.discount_amount > 0:
            balance = balance - d.discount_amount
            folio_transactions.append({
                "account_name": "{}-{}".format(d.discount_account, d.discount_description)  if show_account_code else d.discount_description,
                "credit":  d.discount_amount if d.type=='Debit' else 0,
                "debit":d.discount_amount if d.type=='Credit' else 0,
                "balance":balance,
                "total_amount":d.discount_amount,
                "parent_reference": d["name"],
                "quantity": 0,
            })
        
        if  d.tax_1_amount > 0:
            balance = balance + (d.tax_1_amount * (1 if d.type=='Debit' else -1))
            folio_transactions.append({
                "account_name": "{}-{}".format(d.tax_1_account, d.tax_1_description)  if show_account_code else d.tax_1_description,
                "debit": d.tax_1_amount if d.type=='Debit' else 0 ,
                "credit":d.tax_1_amount if d.type=='Credit' else 0,
                "balance":balance,
                "total_amount":d.tax_1_amount,
                "parent_reference": d["name"],
                "quantity": 0,
            })

        if  d.tax_2_amount > 0:
            balance = balance + (d.tax_2_amount * (1 if d.type=='Debit' else -1) )
            folio_transactions.append({
                "account_name": " {}-{}".format(d.tax_2_account, d.tax_2_description)  if show_account_code else d.tax_2_description,
                "debit":d.tax_2_amount if d.type=='Debit' else 0,
                "credit":d.tax_2_amount if d.type=='Credit' else 0,
                "balance":balance,
                "total_amount":d.tax_2_amount,
                "parent_reference": d["name"],
                "quantity": 0,
            })

        if  d.tax_3_amount > 0:
            balance = balance + (d.tax_3_amount * (1 if d.type=='Debit' else -1))
            folio_transactions.append({
                "account_name": "{}-{}".format(d.tax_3_account, d.tax_3_description)  if show_account_code else d.tax_3_description,
                "debit":d.tax_3_amount if d.type=='Debit' else 0,
                "credit":d.tax_3_amount if d.type=='Credit' else 0,
                "balance":balance,
                "total_amount":d.tax_3_amount,
                "parent_reference": d["name"],
                "quantity": 0,
            })
        
        
    return folio_transactions


def get_folio_transaction_without_breakdown_account_code(transaction_type="", transaction_number="",reservation="",reservation_stay="",show_account_code="-1"):
    if show_account_code =="-1":
        show_account_code = frappe.db.get_single_value("eDoor Setting","show_account_code_in_folio_transaction")==1
    else:
        show_account_code = int(show_account_code)

   
    filters={
        "parent_reference":""
    }

    if transaction_type:
        filters["transaction_type"]=transaction_type
    if transaction_number:
        filters["transaction_number"]=transaction_number
    if reservation:
        filters["reservation"]=reservation

    if reservation_stay:
        filters["reservation_stay"]=reservation_stay
    
    filters["parent_reference"]=""
    filters["is_package_charge"]=0
    
    data = frappe.db.get_list("Folio Transaction", fields=["*"], filters=filters, page_length=1000, order_by='name')
    
 

  
    # data = frappe.db.sql(sql,as_dict=1)

    balance = 0
    folio_transactions = []
    for d in data:
             
        #this is main transaction
        amount = d.total_amount + (d.total_sub_package_charge or 0)
         
        # if d.rate_include_tax=="Yes":
        #     amount =( amount - d.total_tax ) + d.discount_amount
        
        balance = balance + (amount * (1 if d.type=="Debit" else -1))        


        folio_transactions.append({ 
            "reservation":d["reservation"],
            "name":d["name"],
            "room_number":d['room_number'],
            "account_name": "{}-{}".format(d.account_code, d.report_description or d.account_name)  if show_account_code else (d.report_description or d.account_name) ,
            "quantity": d["report_quantity"],
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
             "is_auto_post":d["is_auto_post"],
             "total_amount":d["total_amount"],
              "sale":d.sale,
              "tbl_number":d.tbl_number,
              "is_package":d.is_package
        })
        

        
    return folio_transactions

@frappe.whitelist()
def get_folio_transaction_summary( transaction_type="Reservation Folio",transaction_number='', reservation="", reservation_stay='',sort_by_field='account_category_sort_order',show_room_number = 1,show_account_code=None, show_all_room_rate=None,breakdown_account_code=0,show_note=0):
 
    if cint(breakdown_account_code)==1:
        return get_folio_transaction_summary_with_breadown_account_code(
            transaction_type=transaction_type,
            transaction_number=transaction_number,
            reservation=reservation,
            reservation_stay=reservation_stay,
            sort_by_field = sort_by_field,
            show_room_number=show_room_number,
            show_account_code=show_account_code,
            show_all_room_rate=show_all_room_rate,
            show_note=show_note
        )
    else:
        return get_folio_transaction_summary_without_breadwon_account_code(
            transaction_type=transaction_type,
            transaction_number=transaction_number,
            reservation=reservation,
            reservation_stay=reservation_stay,
            sort_by_field = sort_by_field,
            show_room_number=show_room_number,
            show_account_code=show_account_code,
            show_all_room_rate=show_all_room_rate,
            show_note=show_note
        )


@frappe.whitelist()
def get_folio_transaction_summary_with_breadown_account_code( transaction_type="Reservation Folio",transaction_number='', reservation="", reservation_stay='',sort_by_field='account_category_sort_order',show_room_number = 1,show_account_code=None, show_all_room_rate=None,show_note = 0):
    
    if show_account_code == None:
        show_account_code =str(frappe.db.get_single_value("eDoor Setting","show_account_code_in_folio_transaction"))
    
    data = frappe.db.sql(f"""
                    select 
                        account_category,
                        account_code,
                        {'room_number,' if show_room_number =='1' else '' }
                        ifnull(report_description,account_name) as account_name,
                        sum(report_quantity) as quantity,
                        type,
                        {sort_by_field}, 
                        sum(amount) as amount,
                        sale,
                        tbl_number
                        {',note' if show_note==1 else ''},
                        is_package_breakdown
                    from `tabFolio Transaction` 
                    where 
                        transaction_number =if('{transaction_number}'='',transaction_number,'{transaction_number}')   and 
                        transaction_type = '{transaction_type}' and 
                        reservation_stay = if('{reservation_stay}'='',reservation_stay,'{reservation_stay}') and 
                        reservation = if('{reservation}'='',reservation,'{reservation}') 
                    group by 
                    account_category,
                        account_code,
                        ifnull(report_description,account_name),
                        {'room_number,' if show_room_number =='1' else '' }
                        type
                        {',note' if show_note==1 else ''},
                        sale,
                        tbl_number,
                        is_package_breakdown
                    order by 
                        {'room_number,' if show_room_number =='1' else '' }
                        {sort_by_field},
                        account_code_sort_order
                """,as_dict=1)
    
   
    summary_data = []
    balance = 0
   
    #  check if room show all room charge then get data from room rate include in guest invoice
    
    if show_all_room_rate=="1":
        room_rates = get_folio_room_charge_summary_from_reservation_room_rate(reservation_stay,transaction_number,show_room_number) or []
        for r in room_rates:
            charge = [d for d in data  if d["account_code"] == r["account_code"]]
            if charge:
                charge=charge[0]
                charge["quantity"] = charge["quantity"] + r["quantity"]
                charge["amount"] = charge["amount"] + r["amount"]
            else:
                data.append(r)
    data = sorted(data, key=lambda x: x['account_category_sort_order'])
    
    
             
    for d in data:
        balance = balance + d["amount"]  * (1 if d["type"] =="Debit" else -1)
        record = {
            "description": (d["account_code"] + " - " if show_account_code=='1' else "")  +  d["account_name"],
            "sale":d['sale'] or '',
            "tbl_number":d['tbl_number'] or '',
            "note":"" if not show_note else  d['note'],
            "debit": d["amount"] if d["type"] == "Debit" else 0,
            "credit": d["amount"] if d["type"] == "Credit" else 0,
            "balance":balance,
            "quantity":d["quantity"],
        }
        
        if show_room_number=='1':
            record["room_number"] = d["room_number"]
        summary_data.append(record)
    return summary_data


@frappe.whitelist()
def get_folio_transaction_summary_without_breadwon_account_code( transaction_type="Reservation Folio",transaction_number='', reservation="", reservation_stay='',sort_by_field='account_category_sort_order',show_room_number = 1,show_account_code=None, show_all_room_rate=None,show_note=0):

    if show_account_code == None:
        show_account_code =str(frappe.db.get_single_value("eDoor Setting","show_account_code_in_folio_transaction"))
   
    data = frappe.db.sql(f"""
                    select 
                        account_code,
                        {'room_number,' if show_room_number =='1' else '' }
                        ifnull(report_description,account_name) as account_name,
                        sum(report_quantity) as quantity,
                        type,
                        {sort_by_field}, 
                        sum(total_amount) as amount,
                        sale,
                        tbl_number
                        {',note' if show_note==1 else ''}
                    from `tabFolio Transaction` 
                    where 
                        transaction_number =if('{transaction_number}'='',transaction_number,'{transaction_number}')   and 
                        transaction_type = '{transaction_type}' and 
                        reservation_stay = if('{reservation_stay}'='',reservation_stay,'{reservation_stay}') and 
                        reservation = if('{reservation}'='',reservation,'{reservation}') and
                        coalesce(parent_reference,'') = '' 
                    group by 
                        account_code,
                        ifnull(report_description,account_name),
                        {'room_number,' if show_room_number =='1' else '' }
                        type
                        {',note' if show_note==1 else ''},
                        sale,
                        tbl_number
                    order by 
                        {'room_number,' if show_room_number =='1' else '' }
                        {sort_by_field},
                        account_code_sort_order
                """,as_dict=1)
    
    
    summary_data = []
    balance = 0
   
    #  check if room show all room charge then get data from room rate include in guest invoice
    
    if show_all_room_rate=="1":
        room_rates = get_folio_room_charge_summary_from_reservation_room_rate(reservation_stay,transaction_number,show_room_number) or []
        for r in room_rates:
            charge = [d for d in data  if d["account_code"] == r["account_code"]]
            if charge:
                charge=charge[0]
                charge["quantity"] = charge["quantity"] + r["quantity"]
                charge["amount"] = charge["amount"] + r["amount"]
            else:
                data.append(r)
    data = sorted(data, key=lambda x: x['account_category_sort_order'])
    
 
             
    for d in data:
        balance = balance + d["amount"]  * (1 if d["type"] =="Debit" else -1)
        record = {
            "description": (d["account_code"] + " - " if show_account_code=='1' else "")  +  d["account_name"],
            "sale":d['sale'] or '',
            "tbl_number":d['tbl_number'] or '',
            "note":"" if not show_note else d['note'],
            "debit": d["amount"] if d["type"] == "Debit" else 0,
            "credit": d["amount"] if d["type"] == "Credit" else 0,
            "balance":balance,
            "quantity":d["quantity"],
        }
        
        if show_room_number=='1':
            record["room_number"] = d["room_number"]
        summary_data.append(record)
    return summary_data

    
def get_folio_room_charge_summary_from_reservation_room_rate(reservation_stay,folio_number,show_room_number):

    sql = f"""select 
                rrr.rate_type,
                {'rrr.room_number,' if show_room_number =='1' else '' }
                count(rrr.name) as quantity,
                sum(rrr.rate) as rate,
                sum(rrr.tax_1_amount) as tax_1_amount ,
                sum(rrr.tax_2_amount) as tax_2_amount,
                sum(rrr.tax_3_amount) as tax_3_amount,
                sum(rrr.discount_amount) as discount_amount
            from `tabReservation Room Rate` rrr 
            where 
                reservation_stay='{reservation_stay}' and 
                name not in (select 
                                reservation_room_rate 
                            from `tabFolio Transaction` ft
                            where 
                                ft.transaction_type='Reservation Folio' and 
                                transaction_number='{folio_number}' and 
                                coalesce(reservation_room_rate,'') !=''
                )
            group by 
                {'rrr.room_number,' if show_room_number =='1' else '' }
                rrr.rate_type
                
        """
    data = frappe.db.sql(sql,as_dict=1)
    room_rates = []
     

    for d in data:
        account_code = get_account_code_detail_by_rate_type(d["rate_type"])
        # room  charge
        room_rates.append(
            {
            "account_code": account_code["room_charge"]["code"],
            "account_name": account_code["room_charge"]["account_name"],
            "room_number": d["room_number"] if show_room_number =='1' else '' ,
            "quantity": d["quantity"],
            "type": "Debit",
            "account_category_sort_order":  account_code["room_charge"]["account_category_sort_order"],
            "amount": d["rate"] or 0
        }
        )
        # discount
        if d["discount_amount"]:
            room_rates.append(
                {
                    "account_code": account_code["discount"]["code"],
                    "account_name": account_code["discount"]["account_name"],
                    "room_number": d["room_number"] if show_room_number =='1' else '' ,
                    "quantity": 0,
                    "type": "Credit",
                    "account_category_sort_order":  account_code["discount"]["account_category_sort_order"],
                    "amount": d["discount_amount"]
                }
            )
        # tax 1
        if d["tax_1_amount"]:
            room_rates.append(
                {
                    "account_code": account_code["tax_1"]["code"],
                    "account_name": account_code["tax_1"]["account_name"],
                    "room_number": d["room_number"] if show_room_number =='1' else '' ,
                    "quantity": 0,
                    "type": "Debit",
                    "account_category_sort_order":  account_code["tax_1"]["account_category_sort_order"],
                    "amount": d["tax_1_amount"]
                }
            )
        # tax 2
        if d["tax_2_amount"]:
            room_rates.append(
                {
                    "account_code": account_code["tax_2"]["code"],
                    "account_name": account_code["tax_2"]["account_name"],
                    "room_number": d["room_number"] if show_room_number =='1' else '' ,
                    "quantity": 0,
                    "type": "Debit",
                    "account_category_sort_order":  account_code["tax_2"]["account_category_sort_order"],
                    "amount": d["tax_2_amount"]
                }
            )
        # tax 3
        if d["tax_3_amount"]:
            room_rates.append(
                {
                    "account_code": account_code["tax_3"]["code"],
                    "account_name": account_code["tax_3"]["account_name"],
                    "room_number": d["room_number"] if show_room_number =='1' else '' ,
                    "quantity": 0,
                    "type": "Debit",
                    "account_category_sort_order":  account_code["tax_3"]["account_category_sort_order"],
                    "amount": d["tax_3_amount"]
                }
            )
    

    return room_rates
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

@lru_cache(maxsize=128)
def get_account_code_detail_by_rate_type(rate_type):
    account_code_doc  = frappe.get_doc("Account Code", frappe.db.get_value("Rate Type", rate_type, "account_code"))
    data = {
        "room_charge":{"code":account_code_doc.name,"account_name":account_code_doc.account_name, "account_category_sort_order":get_account_cagegory_sort_order_by_account_code(account_code_doc.name)},
        "discount":{"code":account_code_doc.discount_account,"account_name":account_code_doc.discount_account_name,"account_category_sort_order":get_account_cagegory_sort_order_by_account_code(account_code_doc.discount_account)},
    }
    tax_rule=None
    if account_code_doc.tax_rule:
        tax_rule = frappe.get_doc("Tax Rule", account_code_doc.tax_rule)
        
    
    
    if tax_rule:
        data["tax_1"] ={"code":tax_rule.tax_1_account or "","account_category_sort_order": get_account_cagegory_sort_order_by_account_code(tax_rule.tax_1_account or "")} 
        if data["tax_1"]["code"]:
            data["tax_1"]["account_name"] = frappe.db.get_value("Account Code",data["tax_1"]["code"],"account_name")
            
        data["tax_2"] ={"code":tax_rule.tax_2_account or "","account_category_sort_order": get_account_cagegory_sort_order_by_account_code(tax_rule.tax_2_account or "")} 
        if data["tax_2"]["code"]:
            data["tax_2"]["account_name"] = frappe.db.get_value("Account Code",data["tax_2"]["code"],"account_name")
            
        data["tax_3"] ={"code":tax_rule.tax_3_account or "","account_category_sort_order": get_account_cagegory_sort_order_by_account_code(tax_rule.tax_3_account or "")} 
        if data["tax_3"]["code"]:
            data["tax_3"]["account_name"] = frappe.db.get_value("Account Code",data["tax_3"]["code"],"account_name")
        
        
    
    return data
    
    
@lru_cache(maxsize=128)
def get_account_cagegory_sort_order_by_account_code(account_code):
    if not account_code:
        return 0
    category = frappe.db.get_value("Account Code",account_code, "account_category")
    return frappe.db.get_value("Account Category",category,"sort_order")

@frappe.whitelist(methods="POST")
def update_room_rate(room_rate_names= None,data=None,reservation_stays=None):
    get_package_charge_data.cache_clear()
    get_room_rate_breakdown.cache_clear()
    get_room_rate_account_code_breakdown.cache_clear()
    get_tax_breakdown.cache_clear()
    #validate reservation status 
    #reservation_stays is array string
    if reservation_stays:
        for s in reservation_stays:
            status = frappe.db.get_value("Reservation Stay",s,"reservation_status")
            if frappe.db.get_value("Reservation Status",status, "allow_user_to_edit_information")==0:
                frappe.throw("Reservation Stay: {0} is {1}. {1} reservation is not allow to change information".format(s, status) )
    else:
        reservation_stays.append(data["reservation_stay"])

    if  len(room_rate_names) ==0:
        room_rate_names.append(data["name"])
    for d in room_rate_names:
        doc = frappe.get_doc("Reservation Room Rate",d)
        doc.is_manual_rate = data["is_manual_rate"]
        doc.is_manual_change_pax = data["is_manual_change_pax"]
        doc.adult = data["adult"]
        doc.child = data["child"]
        doc.rate_type = data["rate_type"]
         
        doc.input_rate = data["input_rate"]
        doc.discount_type = data["discount_type"] 
        doc.discount = data["discount"] 
        doc.tax_rule = data["tax_rule"]
        doc.tax_rule_data = "{}" if "tax_rule_data" in data else d["tax_rule_data"]
        doc.tax_1_rate = data["tax_1_rate"]
        doc.tax_2_rate = data["tax_2_rate"]
        doc.tax_3_rate = data["tax_3_rate"]
        doc.note = "" if "note" not in data else  data["note"]
        doc.package_charge_data = data['package_charge_data']
        doc.rate_include_tax = data["rate_include_tax"]

        doc.flags.ignore_on_update = True
        doc.save()
    generate_forecast_revenue(reservation_stays, run_commit=False)
    
    # check if room rate have only 1 rate type then update rate type to stay and stay room
    for s in reservation_stays:
        rate_type_data = frappe.db.sql("select distinct rate_type,tax_rule from `tabReservation Room Rate` where reservation_stay='{}'".format(s),as_dict =1)
        if len(rate_type_data)==1:
            if  rate_type_data[0]["tax_rule"]:
                tax_rule = frappe.get_doc("Tax Rule", rate_type_data[0]["tax_rule"])
                update_data = {"stay_name":s,"rate_type":rate_type_data[0]["rate_type"] ,"tax_rule":tax_rule.name, "tax_1_rate":tax_rule.tax_1_rate, "tax_2_rate":tax_rule.tax_2_rate, "tax_3_rate":tax_rule.tax_3_rate}
            else:
                update_data = {"stay_name":s,"rate_type":rate_type_data[0]["rate_type"] ,"tax_rule":"", "tax_1_rate":0, "tax_2_rate":0, "tax_3_rate":0}
       
            frappe.db.sql("update `tabReservation Stay` set rate_type=%(rate_type)s,tax_rule=%(tax_rule)s, tax_1_rate=%(tax_1_rate)s, tax_2_rate = %(tax_2_rate)s,tax_3_rate = %(tax_3_rate)s where name=%(stay_name)s",update_data)
            frappe.db.sql("update `tabReservation Stay Room` set   rate_type=%(rate_type)s   where parent=%(stay_name)s",update_data)
            
    update_reservation_stay_and_reservation( reservation = data["reservation"], reservation_stay=reservation_stays,run_commit=False)
    
    frappe.db.commit()
    
    
    
    frappe.enqueue("edoor.api.utils.update_reservation_stay_and_reservation", queue='short', reservation = data["reservation"], reservation_stay=reservation_stays)

    
    
    
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

        update_reservation_stay_and_reservation(reservation_stay=active_stays, reservation=reservation,run_commit=False)

    frappe.db.commit()
    if reservation_stay:
        doc =  frappe.get_doc("Reservation Stay", reservation_stay)

        return doc
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
        if f == 'update_reservation_stay':
            update_reservation_stay(doc=doc)
    frappe.db.commit()
    return doc



 
@frappe.whitelist(methods="POST")
def change_pax(data , room_rates = None):
    stay= frappe.get_doc("Reservation Stay", data["stay_name"])
    stay.adult = data["adult"] or 1
    stay.child = data["child"] or 0
    stay.flags.ignore_validate = True
    stay.flags.ignore_on_update = True
    stay.save()
    get_room_rate_breakdown.cache_clear()
    get_room_rate_account_code_breakdown.cache_clear()
    get_charge_breakdown_by_account_code_breakdown.cache_clear()
    package_base_account_code_charge_breakdown.cache_clear()
    get_tax_breakdown.cache_clear()
    get_account_code_doc.cache_clear()
    get_base_rate_cache.cache_clear()
    get_rate_type_doc.cache_clear()
    
    # update room rate
    if room_rates is None:
        room_rates = frappe.db.sql("select name, rate_type, tax_rule, rate_include_tax,tax_1_rate, tax_2_rate, tax_3_rate, input_rate,is_package, package_charge_data,discount,discount_type,discount_amount from `tabReservation Room Rate` where reservation_stay=%(reservation_stay)s and is_manual_change_pax=0",{"reservation_stay":stay.name},as_dict=1)

    for r in room_rates:
         
        rate_breakdown = get_room_rate_breakdown(json.dumps({
            "rate_type":r["rate_type"],
            "tax_rule":r["tax_rule"],
            "rate_include_tax":r["rate_include_tax"],
            "tax_1_rate":r["tax_1_rate"],
            "tax_2_rate":r["tax_2_rate"],
            "tax_3_rate":r["tax_3_rate"],
            "input_rate":r["input_rate"],
            "is_package":r["is_package"],
            "discount_type":r["discount_type"],
            "discount":r["discount"] or 0,
            "discount_amount":r["discount_amount"] or 0,
            "adult":stay.adult,
            "child":stay.child,
            "package_charge_data":r["package_charge_data"]
        }))
        
        room_rate_doc = frappe.get_doc("Reservation Room Rate", r["name"])
        room_rate_doc.total_tax =rate_breakdown["total_tax"]
        room_rate_doc.total_room_charge = rate_breakdown["total_room_charge"]
        room_rate_doc.total_other_charge = rate_breakdown["total_other_charge"]
        room_rate_doc.total_rate = rate_breakdown["total_amount"]
        room_rate_doc.discount_amount= rate_breakdown["discount_amount"]
        room_rate_doc.adult = stay.adult
        room_rate_doc.child = stay.child
        
        room_rate_doc.flags.ignore_validate = True
        room_rate_doc.flags.ignore_on_update = True
        room_rate_doc.save()
        
    update_reservation_stay_and_reservation(reservation=stay.reservation, reservation_stay=[stay.name], ignore_validate=True, run_commit=False)    
    generate_forecast_revenue(stay_names=[stay.name],run_commit=False)
    frappe.db.commit()
    frappe.msgprint(_("Update pax successfully")) 
        
@frappe.whitelist(methods="POST")
def upgrade_room(doc,regenerate_rate=False):
    data = frappe.get_doc('Reservation Stay',doc['name'])
    for dc in doc['stays']:
        
        if 'name' in dc and dc['name']:
            indices = [i for i, d in enumerate(data.stays) if dc['name'] in d.name]
            data.stays[indices[0]].end_date = dc['end_date']
           
            
            frappe.db.sql("delete  from `tabReservation Room Rate` where date>='{}' and stay_room_id='{}'".format(dc["end_date"],dc["name"]))
        else:
            data.append('stays', dc) 

       
    data.save()
     
    last_stay = data.stays[len(data.stays)-1]
    generate_new_room_rate_by_stay_room_id(reservation_stay=data.name, stay_room_id=last_stay.name)

    generate_room_occupies(stay_names=[data.name], run_commit=False)
    generate_forecast_revenue(stay_names=[data.name], run_commit=False)
    update_reservation_stay_and_reservation(reservation=data.reservation, reservation_stay=[data.name], ignore_validate=True, run_commit=False)
    
    frappe.enqueue("edoor.api.utils.update_room_status_by_reservation_stay", queue='long', name=data.name)
    
    frappe.db.commit()

    return data

@frappe.whitelist(methods="POST")
def unassign_room(reservation_stay, room_stay):
    doc = frappe.get_doc('Reservation Stay', reservation_stay)
    if (doc.reservation_status not in ["Reserved","No Show"]):
        frappe.throw("{} is not allow to unassign room".format(doc.reservation_status))
    working_day = get_working_day(doc.property)
    if doc.reservation_status == 'No Show' and  getdate(working_day["date_working_day"])>= getdate(doc.departure_date):
        frappe.throw("This no show reservation is in the past date. You cannot change Information".format(doc.reservation_status))

    for s in doc.stays:
        if s.name == room_stay:
            s.room_id = None
            s.room_number = None

            #clear room id and room number from  temp room occupy and room occupy 
            frappe.db.sql("update `tabTemp Room Occupy` set room_id=null, room_number=null where stay_room_id=%(stay_room_id)s",
                          {"stay_room_id":s.name}
                          )
            
            frappe.db.sql("update `tabRoom Occupy` set room_id=null, room_number=null where stay_room_id=%(stay_room_id)s",
                          {"stay_room_id":s.name}
                          )
            
            #clear room id and room number from reservation room rate
            frappe.db.sql("update `tabReservation Room Rate` set room_id=null, room_number=null where stay_room_id=%(stay_room_id)s",
                          {"stay_room_id":s.name}
                          )
            

    if not doc.reservation_status=="No Show":
        if len([d for d in doc.stays if d.room_id])>0:
            doc.reservation_status ="Reserved"
        else:
            doc.reservation_status ="Confirmed"

    doc.save()
    # update room id room number to forecase revenue
    
    sql = """
        update `tabRevenue Forecast Breakdown` a
        join `tabReservation Room Rate` b on b.name = a.room_rate_id
        SET
            a.room_id ='',
            a.room_number = ''
        where
            a.stay_room_id = %(stay_room_id)s
    """
    frappe.db.sql(sql, {"stay_room_id": room_stay})
    
    if doc:
        frappe.enqueue("edoor.api.utils.update_reservation_stay_and_reservation", queue='short', reservation = doc.reservation, reservation_stay=doc.name)
    
    sql = """
        update `tabFolio Transaction` ft 
        SET
            ft.room_id = %(room_id)s,
            ft.room_number = %(room_number)s,
            ft.room_type_id = %(room_type_id)s,
            ft.room_type_alias = %(room_type_alias)s,
            ft.room_type = %(room_type)s
        where
            source_reservation_stay = %(reservation_stay)s 
    """
    
    frappe.db.sql(sql,{
        "reservation_stay":doc.name, 
        "room_id":doc.stays[0].room_id,
        "room_number":doc.stays[0].room_number,
        "room_type_id":doc.stays[0].room_type_id,
        "room_type_alias":doc.stays[0].room_type_alias,
        "room_type":doc.stays[0].room_type,
    })
    
    
    frappe.db.commit()

    frappe.msgprint(frappe._("Unassign room successfully"))
    return doc


@frappe.whitelist(methods="POST")
def assign_room(data):
    doc = frappe.get_doc('Reservation Stay', data['reservation_stay'])
    old_status = doc.reservation_status
    doc.reservation_status = 'Reserved'

    if 'room_id' in data:
        if not data['room_id']:
            frappe.throw(_("Please select a room to assign."))
    else:
        frappe.throw(_("Please select a room to assign."))
 
    for s in doc.stays:
          
        if s.name == data['stay_room']:
            s.room_id = data['room_id'] or None
            s.room_type_id = data['room_type_id']
            #update room number to room room occupy and temp room occupy
            room_number = frappe.db.get_value("Room", data["room_id"],"room_number")
            frappe.db.sql("update `tabTemp Room Occupy`  set room_type_id=%(room_type_id)s, room_type=%(room_type)s , room_id = %(room_id)s,room_number=%(room_number)s where stay_room_id=%(stay_room_id)s", 
                          {
                              "room_id":data["room_id"],
                              "room_number":room_number,
                              "room_type_id":data["room_type_id"],
                              "room_type":data["room_type"],
                              "stay_room_id": s.name
                          }
                        )
            #update room and room type to room occupy
            frappe.db.sql("update `tabRoom Occupy`  set room_type_id=%(room_type_id)s, room_type=%(room_type)s , room_id = %(room_id)s,room_number=%(room_number)s where stay_room_id=%(stay_room_id)s", 
                    {
                        "room_id":data["room_id"],
                        "room_number":room_number,
                        "room_type_id":data["room_type_id"],
                        "room_type":data["room_type"],
                        "stay_room_id": s.name
                    }
                )
           
            if   'is_override_rate' in data and  data['is_override_rate'] and  data['rate'] != data["old_rate"]:
              
                s.input_rate = data['rate']
                update_reservation_stay_room_rate(data = {"rate": data["rate"], "stay_room_id":  s.name,"room_type":data["room_type"],"room_type_id":data["room_type_id"], "room_id":data["room_id"],"room_number":room_number  })
            else:
                #update room type and room number to room rate only
               
                frappe.db.sql("update `tabReservation Room Rate` set room_type=%(room_type)s , room_type_id=%(room_type_id)s, room_id=%(room_id)s, room_number=%(room_number)s,room_type_alias=%(room_type_alias)s where stay_room_id=%(stay_room_id)s",
                            {
                                "stay_room_id":s.name,
                                "room_type":data["room_type"],
                                "room_type_id":data["room_type_id"],
                                "room_type_alias":frappe.db.get_value("Room Type", data["room_type_id"],"alias"),
                                "room_id":data["room_id"],
                                "room_number":room_number
                            })
                
    doc.save()
    
    if doc:
        generate_forecast_revenue(stay_names=[doc.name], run_commit=False)
        update_reservation_stay_and_reservation(reservation_stay=doc.name, reservation=doc.reservation, run_commit=False)
    if old_status=="No Show":
        generate_room_occupies(stay_names=[doc.name], run_commit=False)
    
    # update room number to folio trsansaction base on source reservation stay and date 
    # we we get room number from reservattion stay
    sql = """
        update `tabFolio Transaction` ft 
        SET
            ft.room_id = %(room_id)s,
            ft.room_number = %(room_number)s,
            ft.room_type_id = %(room_type_id)s,
            ft.room_type_alias = %(room_type_alias)s,
            ft.room_type = %(room_type)s
        where
            source_reservation_stay = %(reservation_stay)s and 
            coalesce(ft.room_id,'') = '' 
    """
    
    frappe.db.sql(sql,{
        "reservation_stay":doc.name, 
        "room_id":doc.stays[0].room_id,
        "room_number":doc.stays[0].room_number,
        "room_type_id":doc.stays[0].room_type_id,
        "room_type_alias":doc.stays[0].room_type_alias,
        "room_type":doc.stays[0].room_type,
    })
    
    
    frappe.db.commit()
    frappe.msgprint(_("Assign room successfully"))
    if old_status=='No Show':
        frappe.msgprint(_("Reservation has been change from No Show to Reserved"))
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
    reservation.group_color = doc["group_color"]
    if update_to_reservation or  doc["doctype"]=="Reservation":
        reservation.reference_number = doc["reference_number"]
        reservation.internal_reference_number = doc["internal_reference_number"]
        reservation.reservation_date = doc["reservation_date"]
    reservation.save()

 

    if doc["doctype"]=="Reservation Stay":
        return frappe.get_doc("Reservation Stay",doc["name"])
    else:
        return reservation



def update_reservation_keyword(reservation):
    stays = frappe.db.sql("select name from `tabReservation Stay` where reservation='{}'".format(reservation),as_dict=1)
    for s in stays:
        update_keyword(frappe.get_doc("Reservation Stay",s))

    
    

@frappe.whitelist(methods="POST")
def update_reservation_color(data):
    
    reservation = data['name']
    if data['doctype'] == 'Reservation Stay':
        reservation = data['reservation']

    frappe.db.set_value('Reservation', reservation, 'reservation_color', data['reservation_color'])
 
    stays = frappe.db.get_list('Reservation Stay', filters={'reservation':reservation, 'is_active_reservation': 1, "allow_user_to_edit_information":1})

    for t in stays:
        doc = frappe.get_doc('Reservation Stay', t.name)
        doc.reservation_color = data['reservation_color']
        doc.save()
    return frappe.get_doc(data['doctype'], data['name'])

@frappe.whitelist(methods="POST")
def update_group_color(data):
    frappe.db.sql("update `tabReservation` set group_color='{}' where name='{}'".format(data['group_color'],data['reservation']))
    frappe.db.sql("update `tabReservation Stay` set group_color='{}' where reservation='{}'".format(data['group_color'],data['reservation']))
    frappe.db.sql("update `tabReservation Stay Room` set group_color='{}' where reservation='{}'".format(data['group_color'],data['reservation']))
    frappe.db.commit()
    frappe.msgprint("Update Group Color successfully")

@frappe.whitelist(methods="POST")
def update_reservation_stay_color(data):
    stay_doc = frappe.get_doc("Reservation Stay", data["name"])
    if (stay_doc.allow_user_to_edit_information==1):
        stay_doc.reservation_color_code = data["reservation_color_code"]
        stay_doc.reservation_color = data["reservation_color"]
        stay_doc.save()
        #apply_to_all_reservation
        if data["apply_to_all_reservation"] == 1:
            other_stays = frappe.db.sql("select name  from `tabReservation Stay` where allow_user_to_edit_information=1 and reservation='{}' and name <>'{}'".format(stay_doc.reservation, stay_doc.name), as_dict=1)
            for d in other_stays:
                frappe.enqueue("edoor.api.reservation.update_reservation_stay_color", queue='short' , data = {
                    "name":d["name"],
                    "apply_to_all_reservation":0,
                    "reservation_color_code":data["reservation_color_code"],
                    "reservation_color":data["reservation_color"],
                })

    else:
        frappe.throw("This reservation stay is not allow to change information")

    return stay_doc


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
    frappe.enqueue("edoor.api.reservation.update_reservation_room_rate", queue='long', stays=[stay.name])


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

        if s.room_id:
            data = frappe.db.sql("select count(room_id) as total from `tabTemp Room Occupy` where  room_id='{}' and stay_room_id !='{}' and date between '{}' and '{}'".format(s.room_id, s.name,s.start_date, add_to_date(s.end_date,days=-1) ),as_dict=1)

            if data[0]["total"] > 0:
                frappe.throw("Room Number {} is not available".format(s.room_number))

    
    stay.is_reserved_room=1
    stay.save()

    frappe.enqueue("edoor.api.generate_occupy_record.generate_room_occupies",queue='short', stay_names=[stay.name] )
    
    #show no show reservation to room chart
    frappe.db.sql("update `tabReservation Stay Room` set show_in_room_chart = 1 where parent='{}'".format(stay.name))

    frappe.db.commit()
    frappe.msgprint("Reserved room successfully")
    frappe.enqueue("edoor.api.reservation.update_reservation_room_rate", queue='long', stays=[stay.name])


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
                                input_rate as rate,
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
    occupy_stays = []
    room_rate_stays = []
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

                doc.save()
                occupy_stays.append({"stay":s, "room_number":room_number, "room_type":room_type } )
                
                
                if   'is_override_rate' in stay and  stay['is_override_rate'] and  stay['rate'] != stay["old_rate"]:
                    s.input_rate = stay['rate']
                    frappe.throw(str(stay["rate"]))
                    update_reservation_stay_room_rate(data = {"rate": stay["rate"], "stay_room_id":  s.name,"room_type":stay["room_type"],"room_type_id":stay["room_type_id"], "room_id":stay["room_id"],"room_number":room_number  })
                    
                if not stay["is_generate_rate"] == 1:
                    #update room to room rate
                    room_rate_stays.append({"stay":s, "room_number":room_number, "room_type":room_type, "room_type_alias":room_type_alias } )
                    



    
    update_room_number_to_room_rate(stays=room_rate_stays,run_commit=False)
    generate_forecast_revenue(stay_names=[d["reservation_stay"] for d in reservation_stays], run_commit=False )
    
    
    frappe.db.commit()
    
    frappe.enqueue("edoor.api.utils.update_reservation_stay_and_reservation", queue='short' , reservation = reservation, reservation_stay=[d["reservation_stay"] for d in reservation_stays])
    frappe.enqueue("edoor.api.reservation.update_room_number_to_occupy_data", queue='default' , stays =occupy_stays)
    frappe.msgprint(_("Assign room successfully"))

@frappe.whitelist()     
def update_room_number_to_room_rate(stays,run_commit = True):
    for stay in stays:
        sql = """update `tabReservation Room Rate` 
                set room_id='{0}' ,
                room_number='{1}' ,
                room_type_id = '{2}',
                room_type = '{3}',
                room_type_alias='{4}'
                where stay_room_id= '{5}'
                """.format(
                    stay["stay"].room_id,
                    stay["room_number"],
                    stay["stay"].room_type_id,
                    stay["room_type"],
                    stay["room_type_alias"],
                    stay["stay"].name
                )
        
        frappe.db.sql(sql)
    if run_commit:
        frappe.db.commit()

@frappe.whitelist()     
def update_room_number_to_occupy_data(stays):
    for stay in stays:
        sql = """update `{0}` 
                        set room_id='{1}' ,
                        room_number='{2}' ,
                        room_type_id = '{3}',
                        room_type = '{4}'
                        where stay_room_id= '{5}'
                        """
        
        frappe.db.sql(sql.format(
                            "tabTemp Room Occupy",
                            stay["stay"].room_id, 
                            stay["room_number"],
                            stay["stay"].room_type_id,
                            stay["room_type"],
                            stay["stay"].name
                            )
        )
        
        frappe.db.sql(sql.format(
                            "tabRoom Occupy",
                            stay["stay"].room_id, 
                            stay["room_number"],
                            stay["stay"].room_type_id,
                            stay["room_type"],
                            stay["stay"].name
                )
        )

    frappe.db.commit()

@frappe.whitelist()
def get_reservation_room_rate(reservation):
    sql="select * from `tabReservation Room Rate` where reservation = '{}' and is_active_reservation = 1 order by date, room_number "
    data = frappe.db.sql(sql.format(reservation),as_dict=1)
    return data
    
    
@frappe.whitelist(methods="POST")
def update_mark_as_paid_by_master_room(reservation, stays, paid_by_master_room):
    if paid_by_master_room==1:
        #validate if there is master stay have active
        data = frappe.db.sql("select name from `tabReservation Stay` where is_master=1 and reservation='{}' and reservation_status in ('In-house','Reserved','Confirmed')".format(reservation),as_dict=1)
        if len(data)==0:
            frappe.throw("There is no master room. Please assign a master room first")

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



    
@frappe.whitelist(methods="POST")
def get_pickup_and_drop_off_data(stays):
    if len(stays)==1:
        return frappe.get_doc("Reservation Stay",stays[0])
    else:
        data = frappe.db.sql("select * from `tabReservation Stay` where name in  %(stays)s and  not last_update_pickup_and_drop_off is null order by last_update_pickup_and_drop_off desc limit 1",{"stays":stays},as_dict=1 )
        if data:
            return data[0]
        else:
            return frappe.get_doc("Reservation Stay",stays[0])
        
@frappe.whitelist(methods="POST")
def update_pickup_and_drop_off(stays,data):
    stay={}
    data["doctype"] = "Reservation Stay"
    data =  frappe.get_doc(data, doctype="Reservation Stay")
     
    for s in stays:
        doc = frappe.get_doc("Reservation Stay",s)
        if not doc.is_active_reservation and len(stays) == 1:
            frappe.throw(_("This reservation stay cannot require pickup and drop off."))
        else:
            doc.require_pickup = data.require_pickup  
            doc.require_drop_off = data.require_drop_off  
            doc.pickup_time = data.pickup_time  
            doc.arrival_mode = data.arrival_mode  
            doc.arrival_flight_number = data.arrival_flight_number  
            doc.pickup_location = data.pickup_location 
            doc.pickup_driver = data.pickup_driver
            doc.pickup_note = data.pickup_note
            doc.drop_off_time = data.drop_off_time
            doc.departure_mode = data.departure_mode
            doc.departure_flight_number= data.departure_flight_number
            doc.drop_off_location= data.drop_off_location
            doc.drop_off_driver= data.drop_off_driver
            doc.drop_off_note= data.drop_off_note
            doc.last_update_pickup_and_drop_off= now()
            doc.save()
            stay = doc

            

            frappe.db.sql("update `tabRoom Occupy` set pick_up=0, drop_off=0 where reservation_stay='{}'".format(doc.name))
            if doc.require_pickup==1:
                frappe.db.sql("update `tabRoom Occupy` set pick_up=1 where reservation_stay='{}' and date='{}'".format(doc.name,doc.arrival_date))		
            if doc.require_drop_off==1:
                frappe.db.sql("update `tabRoom Occupy` set drop_off=1 where reservation_stay='{}' and date='{}'".format(doc.name, (doc.checked_out_system_date if doc.is_early_checked_out==1 else doc.departure_date)))
    


    frappe.db.commit()
    frappe.msgprint("Update pick up and drop off successfully")
    if len(stays)==1:
        return stay
    

@frappe.whitelist(methods="POST")
def get_document_count(attacheds):
    if attacheds:
        data = frappe.db.sql("select count(name) from `tabFile` where attached_to_name in ({})".format(attacheds))
        return data[0][0]
    
@frappe.whitelist()
def get_room_tax_summary(reservation=None, reservation_stay=None):
    if reservation:
        sql="""
            select tax_1_name as tax_name, tax_1_rate as tax_rate, sum(tax_1_amount) as tax_amount  from `tabReservation Room Rate` where reservation = '{0}'  and tax_1_rate> 0  and is_active_reservation = 1 group by tax_1_name, tax_1_rate
            union all 
            select tax_2_name as tax_name, tax_2_rate as tax_rate, sum(tax_2_amount) as tax_amount  from `tabReservation Room Rate` where reservation = '{0}'   and tax_2_rate> 0 and is_active_reservation = 1 group by tax_2_name, tax_2_rate
            union all
            select tax_3_name as tax_name, tax_3_rate as tax_rate, sum(tax_3_amount) as tax_amount  from `tabReservation Room Rate` where reservation= '{0}'  and tax_3_rate> 0 and is_active_reservation = 1 group by tax_3_name, tax_3_rate
        """.format(reservation)
        return frappe.db.sql(sql,as_dict=1)
    else:
        sql="""
            select tax_1_name as tax_name, tax_1_rate as tax_rate, sum(tax_1_amount) as tax_amount  from `tabReservation Room Rate` where reservation_stay = '{0}'  and tax_1_rate> 0  and is_active_reservation = 1 group by tax_1_name, tax_1_rate
            union all 
            select tax_2_name as tax_name, tax_2_rate as tax_rate, sum(tax_2_amount) as tax_amount  from `tabReservation Room Rate` where reservation_stay = '{0}'   and tax_2_rate> 0 and is_active_reservation = 1 group by tax_2_name, tax_2_rate
            union all
            select tax_3_name as tax_name, tax_3_rate as tax_rate, sum(tax_3_amount) as tax_amount  from `tabReservation Room Rate` where reservation_stay= '{0}'  and tax_3_rate> 0 and is_active_reservation = 1 group by tax_3_name, tax_3_rate
        """.format(reservation_stay)
        return frappe.db.sql(sql,as_dict=1)

@frappe.whitelist(methods="POST")
def folio_transfer(data):
    if not data["new_folio_number"]:
        frappe.throw("Please select new folio number")
    
    #validate folio is still open
    new_folio_doc = frappe.get_doc("Reservation Folio", data["new_folio_number"])
    new_room_id = None
    new_room_type_id = None 
    if data["change_room"]==1:
        #check room from room occupy of current working day
        working_day = get_working_day(property=data["property"])
        occupy_data = frappe.db.sql("select room_type_id,room_id from `tabTemp Room Occupy` where is_departure = 0 and reservation_stay='{}' and date='{}' limit 1".format(new_folio_doc.reservation_stay, working_day["date_working_day"]),as_dict=1)
        if occupy_data:
            new_room_id = occupy_data[0]["room_id"]
            new_room_type_id= occupy_data[0]["room_type_id"]

    if new_folio_doc.status == "Closed":
        frappe.throw(_("Target folio number {} is already closed".format(data["new_folio_number"])))
    #check reservation status in new folio is not allow to edit
    reservation_status_doc = frappe.get_doc("Reservation Status", new_folio_doc.reservation_status)
    if not reservation_status_doc.allow_user_to_edit_information or not reservation_status_doc.is_active_reservation:
        frappe.throw(_("Reservation stay # {} of target folio number {} is not allow to edit information".format(new_folio_doc.reservation_stay, new_folio_doc.name)))

    

    old_folio_doc = frappe.get_doc("Reservation Folio", data["folio_number"])
    #check if old folio doc is already close 
    if old_folio_doc.status == "Closed":
        frappe.throw(_("Current folio number {} is already closed".format(data["folio_number"])))
    
    #check reservation status in new folio is not allow to edit
    reservation_status_doc = frappe.get_doc("Reservation Status", old_folio_doc.reservation_status)
    if not reservation_status_doc.allow_user_to_edit_information or not reservation_status_doc.is_active_reservation:
        frappe.throw(_("Reservation stay # {} of source folio number {} is not allow to edit information".format(new_folio_doc.reservation_stay, old_folio_doc.name)))

    comment_doc = []
    for d in data["folio_transaction"]:
        folio_transaction_doc = frappe.get_doc("Folio Transaction", d)
        folio_transaction_doc.transaction_number = new_folio_doc.name
        folio_transaction_doc.reservation = new_folio_doc.reservation
        folio_transaction_doc.reservation_stay = new_folio_doc.reservation_stay
        folio_transaction_doc.ignore_validate_auto_post = 1
        folio_transaction_doc.ignore_update_folio_transaction = 1
        folio_transaction_doc.valiate_input_amount = 0
        folio_transaction_doc.flags.ingore_validate = True
        folio_transaction_doc.flags.ignore_on_update = True
        
        
        #check if user want to change room
        if data["change_room"] ==1:
            if new_room_type_id and new_room_id:
                folio_transaction_doc.room_type_id = new_room_type_id
                folio_transaction_doc.room_id = new_room_id

        #check keep guest infor
        if data["change_guest"] ==1:
            folio_transaction_doc.guest = new_folio_doc.guest



        
        folio_transaction_doc.save()
        

        comment_doc.append(
            {
                "reference_doctype":"Folio Transaction",
                "reference_name":folio_transaction_doc.name,
                "subject":"Transfer folio item",
                "custom_audit_trail_type":"Folio",
			    "custom_icon":"pi pi-dollar",
                "content":f'Folio Transfer from room # {old_folio_doc.rooms}. Folio Number  {data["folio_number"]}, Reservation Stay # {old_folio_doc.reservation}, Reservation # {old_folio_doc.reservation_stay}, Note: {data["note"]}'
            }
        )
 
   
       
        #update sub record
        sub_transaction = frappe.db.sql("select name from `tabFolio Transaction` where parent_reference='{}'".format(d), as_dict=1)
        # sub transaction second level
        if sub_transaction:
            sub_transaction = sub_transaction +  frappe.db.sql("select name from `tabFolio Transaction` where parent_reference in %(parent_references)s",{"parent_references":[d["name"] for d in sub_transaction]}, as_dict=1)
 
        for s in sub_transaction:
            sub_transaction_doc = frappe.get_doc("Folio Transaction", s["name"])
            sub_transaction_doc.transaction_number = new_folio_doc.name
            sub_transaction_doc.reservation = new_folio_doc.reservation
            sub_transaction_doc.reservation_stay = new_folio_doc.reservation_stay
            sub_transaction_doc.ignore_validate_auto_post = 1
            sub_transaction_doc.ignore_update_folio_transaction = 1
            sub_transaction_doc.valiate_input_amount = 0
            sub_transaction_doc.flags.ingore_validate = True
            sub_transaction_doc.flags.ignore_on_update = True


            #check if user want to change room
            if data["change_room"] ==1:
                if new_room_type_id and new_room_id:
                    sub_transaction_doc.room_type_id = new_room_type_id
                    sub_transaction_doc.room_id = new_room_id
            

            #check keep guest infor
            #check keep guest infor
            if data["change_guest"] ==1:
                sub_transaction_doc.guest = new_folio_doc.guest

            sub_transaction_doc.save()
        
    #end updatre sub
    update_reservation_folio(name=data["folio_number"],run_commit=False,ignore_validate=True)
    # update folio balance to source folio
    
    update_reservation_folio(name=data["new_folio_number"],run_commit=False,ignore_validate=True)
    
    
    frappe.db.commit()
    
    # add audit trail to source reservation stay
    comment_doc.append(
        {
            "reference_doctype":"Reservation Stay",
            "reference_name":data["reservation_stay"],
            "subject":"Transfer folio item",
            "custom_audit_trail_type":"Folio",
            "custom_icon":"pi pi-dollar",
            "content": f'Folio transaction numbers: {", ".join(data["folio_transaction"])} has been transfer to Folio #: {data["new_folio_number"]}, Stay #: {new_folio_doc.reservation_stay}, Guest: {new_folio_doc.guest_name}, Room #: {new_folio_doc.rooms},Note: {data["note"]}'
        }
    )
        
    #enque update job source folio
    frappe.enqueue("edoor.api.utils.update_reservation_stay_and_reservation", queue='short', reservation_folio=data["folio_number"] , reservation = data["reservation"], reservation_stay=data["reservation_stay"])
    #enque update target folio
    frappe.enqueue("edoor.api.utils.update_reservation_stay_and_reservation", queue='short', reservation_folio=data["new_folio_number"] , reservation = new_folio_doc.reservation, reservation_stay=new_folio_doc.reservation_stay)    
    frappe.enqueue("edoor.api.utils.add_audit_trail", queue='long', data=comment_doc)


    frappe.msgprint("Folio transfer successfully")



@frappe.whitelist()
def get_guest_by_reservation(reservation):
    guests =[frappe.db.get_value("Reservation",reservation, "guest")]
    sql = "select guest,name from `tabReservation Stay` where reservation='{}'".format(reservation)
    data = frappe.db.sql(sql,as_dict=1)   
    
 
 
    guests = guests + [d["guest"] for d in data]
 

    sql = "select distinct guest from `tabAdditional Stay Guest` where parent in %(reservation_stays)s"

    data = frappe.db.sql(sql,{"reservation_stays":[d["name"] for d in data]},as_dict=1) 

    guests = guests + [d["guest"] for d in data]

    return set(guests)


@frappe.whitelist()
def check_reservation_exist_in_future(property, fieldname,value):
    working_day = get_working_day(property)

    is_exist = frappe.db.exists("Reservation Stay", {fieldname: value, "is_active_reservation":1,"property":property,"arrival_date":[">=",working_day["date_working_day"]]} ) 
    if is_exist:
        return is_exist
    
    is_exist = frappe.db.exists("Reservation", {fieldname: value,"property":property,"arrival_date":[">=",working_day["date_working_day"]]} )
    return is_exist

@frappe.whitelist()  
def verify_reservation_stay(stay_name= None):
    stay = frappe.get_doc("Reservation Stay", stay_name)
    # verify room occupy and temp room occupy
    # if total record not matchy with room nights then regenerate it again

    if stay.is_active_reservation ==1:
        sql = "select count(name) as total from `tabRoom Occupy` where reservation_stay = '{}' and date between '{}' and '{}'".format(stay_name, stay.arrival_date, stay.departure_date)
    
        data = frappe.db.sql(sql,as_dict=1)
        
        if not  cint(stay.room_nights) == cint(data[0]["total"])-1:
            generate_room_occupies(stay_names=[stay.name])

        sql = "select count(name) as total from `tabTemp Room Occupy` where reservation_stay = '{}' and date between '{}' and '{}'".format(stay_name, stay.arrival_date, stay.departure_date)
        data = frappe.db.sql(sql,as_dict=1)
        if not cint(stay.room_nights) == cint(data[0]["total"]) :
            generate_room_occupies(stay_names=[stay.name])
        #validate credit debit balance
        sql_folio = """
            select  
                    coalesce(sum(if(type='Debit',amount,0)),0) as debit,
                    coalesce(sum(if(type='Credit',amount,0)),0) as credit
                from `tabFolio Transaction` 
                where
                    reservation_stay = '{}' and 
                    transaction_type = 'Reservation Folio'
            """.format(
                    stay_name
                )

        folio_data = frappe.db.sql(sql_folio, as_dict=1)
        if len(folio_data)>0:
            
            if folio_data[0]["credit"] != stay.total_credit or folio_data[0]["debit"] != stay.total_debit:
               
                frappe.db.sql("update `tabReservation Stay` set total_credit={0} , total_debit={1}, balance={1}-{0} where name='{2}'".format(folio_data[0]["credit"],folio_data[0]["debit"], stay_name))

 

@frappe.whitelist(methods="POST")
def make_as_verify_folio_transaction(name):
    doc = frappe.get_doc("Folio Transaction",name)
    doc.flags.ignore_validate=True
    doc.is_verify = not doc.is_verify
    doc.save()
    frappe.db.commit()
    if doc.is_verify:
        frappe.msgprint(_("Mask as verify successfully"))
    else:
        frappe.msgprint(_("Unmask as verify successfully"))
    
    return doc