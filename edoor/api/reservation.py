import json

from edoor.api.frontdesk import get_working_day
import frappe
from frappe.utils.data import add_to_date

@frappe.whitelist()
def get_reservation_detail(name):
    reservation= frappe.get_doc("Reservation",name)
    return {
        "reservation":reservation
    }


@frappe.whitelist()
def get_reservation_stay_detail(name):
    reservation_stay= frappe.get_doc("Reservation Stay",name)
    reservation = frappe.get_doc("Reservation",reservation_stay.reservation)
    guest=frappe.get_doc("Customer",reservation_stay.guest)
    master_guest = guest
    if reservation.guest != reservation_stay.guest:
        master_guest = frappe.get_doc("Customer",reservation.guest)
    return {
        "reservation":reservation,
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
                    room_id 
                from `tabTemp Room Occupy` 
                where
                    date between '{2}' and '{3}' 
            )   
    """
    sql = sql.format(property,room_type_id,start_date, end_date)
    data = frappe.db.sql(sql,as_dict=1)
    return data

@frappe.whitelist()
def check_room_type_availability(property,start_date=None,end_date=None):
    end_date = add_to_date(end_date,days=-1)
    #get all room type and total room 

    room_type = frappe.db.sql("select room_type_id as name, room_type, count(name) as total_room, 0 as occupy from `tabRoom` where disabled = 0 and property='{}' group by room_type_id,room_type".format(property),as_dict=1)
    for t in room_type:
        sql = "select coalesce(count(  distinct room_id),0) as total_room from `tabTemp Room Occupy` where room_type_id = '{}' and date between '{}' and '{}'".format(t["name"],start_date,end_date)
        t["occupy"] = frappe.db.sql(sql,as_dict=1)[0]["total_room"]

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

    reservation = frappe.get_doc(doc["reservation"]).insert()
    
    #start insert insert reservation stay
    for d in doc["reservation_stay"]:
        stay = {
            "doctype":"Reservation Stay",
            "reservation":reservation.name,
            "reservation_status":"Reserved",
            "arrival_time":reservation.arrival_time,
            "departure_time":reservation.departure_time,
            "stays":[
                {
                    "doctype":"Reservation Stay Room",
                    "room_type_id": d["room_type_id"],
                    "room_id":d["room_id"],
                    "rate":d["rate"],
                    "guest":reservation.guest,
                    "reservation_status":"Reserved",
                    "start_time":reservation.arrival_time,
                    "end_time":reservation.departure_time,
                }
            ]
        }
        frappe.get_doc(stay).insert()


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
