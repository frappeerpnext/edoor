import json
import frappe

@frappe.whitelist()
def get_reservation_detail(name):
    reservation= frappe.get_doc("Reservation",name)
    return {
        "reservation":reservation
    }

@frappe.whitelist()
def check_room_availability(property,room_type_id=None,start_date=None,end_date=None):
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
    sql = """
        select 
            room_type,
            name
        from `tabRoom Type` 
        where 
            property = '{0}' and 
            name not in (
                select 
                    room_type_id 
                from `tabTemp Room Occupy` 
                where
                    date between '{1}' and '{2}' 
            )   
    """
    sql = sql.format(property,start_date, end_date)
    data = frappe.db.sql(sql,as_dict=1)
    return data



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
            "stays":[
                {
                    "doctype":"Reservation Stay Room",
                    "room_type_id": d["room_type_id"],
                    "room_id":d["room_id"],
                    "rate":d["rate"],
                    "guest":reservation.guest,
                    "reservation_status":"Reserved",
                }
            ]
        }
        frappe.get_doc(stay).insert()


    frappe.db.commit()
    return reservation

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
