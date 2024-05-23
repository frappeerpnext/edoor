from edoor.api.utils import get_date_range,get_reservation_stay_additional_information
import frappe
import uuid  
from frappe.model.document import bulk_insert
from frappe.utils import getdate

@frappe.whitelist()
def generate_room_occupies(stay_names,run_commit = True):
    if not stay_names:
        return
    
    frappe.db.sql("delete from `tabTemp Room Occupy` where reservation_stay in %(stay_names)s",{"stay_names":stay_names})
    frappe.db.sql("delete from `tabRoom Occupy` where reservation_stay in %(stay_names)s",{"stay_names":stay_names})
   
    sql = """select 
                property, 
                room_type_id,
                room_type,room_type_alias, 
                name,
                room_id,
                room_number, 
                parent as reservation_stay, 
                reservation, 
                start_date, 
                end_date,
                adult,
                child,
                pax 
            from `tabReservation Stay Room` where parent in %(stay_names)s
            order by start_date
            """
    
    stays_info = frappe.db.sql(sql, {"stay_names":stay_names}, as_dict=1)
 
    generate_temp_room_occupy(stays_info=stays_info)
    generate_room_occupy(stays_info=stays_info)
    if run_commit:
        frappe.db.commit()
    
def generate_temp_room_occupy(stays_info):	
    bulk_insert("Temp Room Occupy",get_temp_room_occupy_record(stays_info=stays_info) , chunk_size=10000)

def generate_room_occupy(stays_info):	
    bulk_insert("Room Occupy",get_room_occupy_record(stays_info=stays_info) , chunk_size=10000)

def get_room_occupy_record(stays_info):
    reservation_stays_info = get_reservation_stay_additional_information([d["reservation_stay"] for d in stays_info])
    rooms_info = get_rooms_info([d["room_id"] for d in stays_info])
    for stay in stays_info:
        # get stay record informaation for update to room occupy
        reservation_stay_info = [d for d in reservation_stays_info if d["name"]==stay["reservation_stay"]][0]
        room_info = [d for d in rooms_info if d["name"]==stay["room_id"]]
        if room_info:
            room_info = room_info[0]
        
        stays = [s for s in stays_info if s["reservation_stay"] == stay["reservation_stay"]]
        
        exlude_last_date=False if stay["name"] == stays[len(stays)-1]["name"] else True
        dates = get_date_range(getdate( stay["start_date"]), getdate(stay["end_date"]),exlude_last_date=exlude_last_date)
        for d in dates:    
            doc = frappe.new_doc("Room Occupy")
            doc.name  = str(uuid.uuid4())
            doc.room_type_id = stay["room_type_id"]
            doc.room_type = stay["room_type"]
            doc.room_type_alias = stay["room_type_alias"]
            doc.room_id = stay["room_id"]
            doc.room_number = stay["room_number"]
            doc.date = d
            doc.type = "Reservation"
            doc.property = stay["property"]
            doc.stay_room_id = stay["name"]
            doc.reservation = stay["reservation"]
            doc.reservation_stay = stay["reservation_stay"]
            doc.adult = stay["adult"]
            doc.child = stay["child"]
            doc.pax = stay["pax"]
            doc.is_stay_over = 1 if (getdate(d)>getdate(reservation_stay_info["checked_in_system_date"] or reservation_stay_info["arrival_date"]) and getdate(d)< getdate(reservation_stay_info["departure_date"])) or  reservation_stay_info["is_early_checked_out"] ==1  else 0
            doc.is_arrival = 1 if getdate(d)==getdate(reservation_stay_info["checked_in_system_date"] or  reservation_stay_info["arrival_date"]) else 0
            doc.is_departure = 1 if getdate(d)==getdate(reservation_stay_info["departure_date"]) else 0 
            doc.is_active =1 if (getdate(d)<getdate(reservation_stay_info["departure_date"]) or reservation_stay_info["is_early_checked_out"]) and getdate(d)>=getdate(reservation_stay_info["checked_in_system_date"] or reservation_stay_info["arrival_date"]) else 0 
            doc.pick_up =  1 if getdate(d)==getdate(reservation_stay_info["arrival_date"]) and reservation_stay_info["is_pickup"]==1 else 0
            doc.drop_off = 1 if getdate(d)==getdate(reservation_stay_info["departure_date"]) and reservation_stay_info["is_drop_off"] ==1 else 0 
            doc.rate_type =reservation_stay_info["rate_type"]
            doc.is_complimentary =reservation_stay_info["is_complimentary"]
            doc.is_house_use =reservation_stay_info["is_house_use"]
            doc.is_walk_in =reservation_stay_info["is_walk_in"]
            doc.reservation_type =reservation_stay_info["reservation_type"]
            doc.reservation_status =reservation_stay_info["reservation_status"]
            doc.business_source =reservation_stay_info["business_source"]
            doc.business_source_type =reservation_stay_info["business_source_type"]
            doc.is_active_reservation =reservation_stay_info["is_active_reservation"]
            
            if room_info:
                doc.floor =room_info["floor"]
                doc.building=room_info["building"]
            
            # guest info
            doc.guest=reservation_stay_info["guest"]
            doc.guest_name=reservation_stay_info["guest_name"]
            doc.guest_type=reservation_stay_info["guest_type"]
            doc.nationality=reservation_stay_info["nationality"]

            if doc.is_stay_over==1 and doc.is_arrival==1:
                doc.is_stay_over==0
            yield doc



def get_rooms_info(room_ids):
    sql ="select name, building,floor from `tabRoom` where name in %(room_ids)s"
    return frappe.db.sql(sql,{"room_ids":room_ids},as_dict=1)

def get_temp_room_occupy_record(stays_info):
    for stay in stays_info: 
        dates = get_date_range(getdate(stay["start_date"]), getdate( stay["end_date"]),exlude_last_date=True)
        for d in dates:
            #generate room to temp room occupy
            
            doc = frappe.new_doc("Temp Room Occupy")
            doc.name  = str(uuid.uuid4())
            doc.reservation = stay["reservation"]
            doc.reservation_stay = stay["reservation_stay"]
            doc.room_type_id = stay["room_type_id"]
            doc.room_id= stay["room_id"]
            doc.property= stay["property"]
            doc.type='Reservation'
            doc.date=d
            doc.stay_room_id=stay["name"]
            doc.is_active=1
            yield doc