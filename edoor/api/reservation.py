import json

from edoor.api.frontdesk import get_working_day
import frappe
from frappe.utils.data import add_to_date

@frappe.whitelist()
def get_reservation_detail(name):
    reservation= frappe.get_doc("Reservation",name)
    reservation_stays = frappe.get_list("Reservation Stay",filters={'reservation': name},fields=['name', 'reference_number','arrival_date','arrival_time','departure_date','departure_time','room_types','rooms'])
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
    master_guest = guest
    if reservation.guest != reservation_stay.guest:
        master_guest = frappe.get_doc("Customer",reservation.guest)
    return {
        "reservation":reservation,
        "total_reservation_stay": total_reservation_stay,
        "reservation_stay":reservation_stay,
        "guest":guest,
        "master_guest":master_guest
    }

@frappe.whitelist()
def check_room_availability(property,room_type_id=None,start_date=None,end_date=None):
    end_date = add_to_date(end_date,days=-1)

    if not room_type_id:
        room_type_id = ''

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
                    date between '{2}' and '{3}' 
            )   
    """

    sql = sql.format(property,room_type_id,start_date, end_date)
     
    data = frappe.db.sql(sql,as_dict=1)
    return data

@frappe.whitelist()
def check_room_type_availability(property,start_date=None,end_date=None,rate_type=None, business_source=None):
    end_date = add_to_date(end_date,days=-1)
    #get all room type and total room 

    room_type = frappe.db.sql("select room_type_id as name, room_type, count(name) as total_room, 0 as occupy from `tabRoom` where disabled = 0 and property='{}' group by room_type_id,room_type".format(property),as_dict=1)
    for t in room_type:
        sql = "select coalesce(count(  distinct room_id),0) as total_room from `tabTemp Room Occupy` where room_type_id = '{}' and date between '{}' and '{}'".format(t["name"],start_date,end_date)
        t["occupy"] = frappe.db.sql(sql,as_dict=1)[0]["total_room"]
        t["rate"] = get_room_rate(property, rate_type, t["name"], business_source, start_date)

    return  [d for d in room_type if d['total_room'] - d["occupy"] > 0]
 


@frappe.whitelist()
def add_new_fit_reservation(doc):
    
    doc = json.loads(doc)
    #check if not have guest selected then create new guest

    if not check_field(doc["reservation"],"guest"):
        guest = frappe.get_doc(doc["guest_info"]).insert()
        doc["reservation"]["guest"] = guest.name
    else:
        guest = frappe.get_doc(doc["guest_info"]).save()
    
    #prevent code call on_pdate to reservation stay
    doc["update_reservation_stay"] = False
    reservation = frappe.get_doc(doc["reservation"]).insert()
    
    #start insert insert reservation stay
    i = 0
    for   d in doc["reservation_stay"]:
      
        room = None
        if   'room_id' in d.keys():
            room = d["room_id"]
        #set virtural attribute field to update reservation after all stay is add to database
        
        update_reservation = False
        if i ==len(doc["reservation_stay"])-1:
            update_reservation = True

        stay = {
            "doctype":"Reservation Stay",
            "update_reservation":update_reservation,
            "reservation":reservation.name,
            "reservation_status":"Reserved",
            "arrival_time":reservation.arrival_time,
            "departure_time":reservation.departure_time,
            "stays":[
                {
                    "doctype":"Reservation Stay Room",
                    "room_type_id": d["room_type_id"],
                    "room_id":room,
                    "rate":d["rate"] or 0,
                    "guest":reservation.guest,
                    "reservation_status":"Reserved",
                    "start_time":reservation.arrival_time,
                    "end_time":reservation.departure_time,
                }
            ]
        }

        frappe.get_doc(stay).insert()
        
        i=i+1
    frappe.db.commit()
    return reservation


@frappe.whitelist(methods="POST")
def check_in(reservation,reservation_stays=None):
    #reservation_stays is list of stay in a reservation separate by comma
    #reservation_stays is apply then we skip check reservation 
    doc = frappe.get_doc("Reservation",reservation)
    working_day = get_working_day(doc.property)
   
    if not working_day["cashier_shift"]:
        frappe.throw("There is no cashier shift open. Please open cashier shift first")

    
    
   
    stays = []
    if not reservation:
        frappe.throw("There is no reservation to check in")

    if reservation_stays:
        stays = reservation_stays.split(',')
    else:
        stays = frappe.get_list("Reservation Stay",filters={"reservation":reservation},limit=100) # limit 100 to prevent reservation that have more than 20 stay
    

    for s in stays:
        stay = frappe.get_doc("Reservation Stay", s)
        if stay.reservation_status=="Inhouse":
            frappe.throw("Stay #: {}. Room: {}. This room is already checkin.".format(stay.name, stay.rooms))

      
        if str(stay.arrival_date) != str(working_day["date_working_day"]):
            frappe.throw("Stay #: {}. Room: {}. Arrival date must be equal to current date.".format(stay.name, stay.rooms))

        stay.reservation_status = "Inhouse"
        stay.save()

    frappe.db.commit()

    return {
        "reservation":doc
    }



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
    if(is_only_master_guest == 'false'):
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
        guest_name = doc_guest['name']
    doc_stay = frappe.get_doc('Reservation Stay', reservation_stay)
    if doc_stay.guest == guest_name:
        frappe.throw('This guest is already selected.')
    for i in doc_stay.additional_guests:
        if i.guest ==guest_name or i.guest == doc_stay.guest:
            frappe.throw('This guest is already selected.')
            # return {
            #     'status': 406,
            #     'message': 'This guest is already selected.'
            # }
    
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

def update_reservation(self):

    #update room, and room_type
    sql = "select rooms, room_types from `tabReservation Stay` where reservation='{}'".format(self.name)
    data = frappe.db.sql(sql, as_dict=1)
    frappe.throw(','.join([d["rooms"] for d in data]))
    
    #update adult and pax

    #update room_chage, tax and payment and balance

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
    sql = """
            select 'all' as name , 'All Folio' as folio
            union
            select name, name as folio from `tabReservation Folio`
            union 
            select name, name as folio from `tabReservation Folio`
        """
    # sql = sql.format((reservation or ''), (reservation_stay or ''))
    return frappe.db.sql(sql, as_dict=1)


@frappe.whitelist()
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
            data = frappe.db.sql(sql, as_dict=1)
            rate = data[0]["rate"] or 0
            
    if rate == 0:
        rate = room_type_rate
    return rate


