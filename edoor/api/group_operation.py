from edoor.edoor.doctype.reservation_stay.reservation_stay import update_reservation_stay_room_rate_after_resize
from edoor.api.frontdesk import get_working_day
from edoor.api.reservation import check_room_type_availability
from edoor.api.utils import validate_role
from py_linq import Enumerable
import frappe
from frappe import _ 

from frappe.utils.data import add_to_date, getdate,now,date_diff

@frappe.whitelist(methods="POST")
def group_change_stay(data):
    #BASIC VALIDATION
    allow_back_date = frappe.db.get_single_value("eDoor Setting","allow_user_to_add_back_date_transaction")
    #check if user move from departure date and move behind current working date 
    working_day = get_working_day(data["property"])
    
    if getdate(data["departure"])< getdate(working_day["date_working_day"]) :
        if allow_back_date==1:
                validate_role("role_for_back_date_transaction","You don't have permission to add back date reservation")
        else:
            frappe.throw(_("Depature date must be greater then or equal to current working date"))
            
    note = ""
    if hasattr(data,"note"):
        note = data["note"]
    data_for_change_stays = []
    data_for_check_validation = []
    for s in data["stays"]:
        doc = frappe.get_doc("Reservation Stay",s)              
        if (getdate(data["arrival"]) != getdate(doc.arrival_date) or getdate(data["departure"]) != getdate(doc.departure_date)) and doc.is_active_reservation==1 and doc.allow_user_to_edit_information==1:
            #validate back date for reservation that is reserve and confrim
            if getdate(data["arrival"])<getdate(working_day["date_working_day"]):
                if doc.reservation_status in ["Reserved","Confirm"]:
                    if frappe.db.get_single_value("eDoor Setting","allow_user_to_add_back_date_transaction")==1:
                        validate_role("role_for_back_date_transaction","You don't have permission to add back date reservation")
                    else:
                        frappe.throw("You cannot change arrival date to the back date")
                else:
                    for d in doc.stays:
                        if d.start_date != getdate(data["arrival"]):
                            frappe.throw("{} is not allow to change arrival date".format(doc.reservation_status))


            if len(doc.stays)>1:
                #check arrival date change for first stay room
                first_stay = doc.stays[0]
                if getdate(data["arrival"]) != getdate(first_stay.start_date):
                    data_for_check_validation.append({
                        "room_id": first_stay.room_id,
                        "property": doc.property,
                        "room_type_id": first_stay.room_type_id,
                        "start_date": data["arrival"],
                        "end_date": first_stay.end_date,
                        "parent": s,
                        "generate_rate_type": data["generate_new_stay_rate_by"],
                        "note": note,
                        "name": first_stay.name,
                        "ignore_check_room_occupy": 1, #TODO#
                        })
                
                #check departure change for last stay room 
                last_stay = doc.stays[len(doc.stays)-1]

                if getdate(data["departure"]) != getdate(last_stay.end_date):
                    data_for_check_validation.append({
                        "room_id": last_stay.room_id,
                        "property": doc.property,
                        "room_type_id": last_stay.room_type_id,
                        "start_date": last_stay.start_date,
                        "end_date": data["departure"],
                        "parent": s,
                        "generate_rate_type": data["generate_new_stay_rate_by"],
                        "note":note,
                        "name": last_stay.name,
                        "ignore_check_room_occupy": 1, #TODO#
                        })
            else:
                # when stay have only 1 room
                first_stay = doc.stays[0]
                data_for_check_validation.append({
                    "room_id": first_stay.room_id,
                    "property": doc.property,
                    "room_type_id": first_stay.room_type_id,
                    "start_date": data["arrival"],
                    "end_date": data["departure"],
                    "parent": s,
                    "generate_rate_type": data["generate_new_stay_rate_by"],
                    "note": note,
                    "name": first_stay.name,
                    "ignore_check_room_occupy": 1, #TODO#
                    })
                
    if len(data_for_check_validation)==0:
        frappe.throw("There is no record to change stay")
            
    for d in data_for_check_validation:
        data_for_change_stays.append(can_change_stay_date(d))
    
    can_change_stay_data = [d for d in data_for_change_stays if d["can_change_stay"]==True ]
    if len(can_change_stay_data)> 0:
        for d in can_change_stay_data:
            change_stay(d)
        
        #commit data change to database
        frappe.db.commit()
        

        
     
        frappe.enqueue("edoor.api.utils.update_reservation_stay_and_reservation", queue='short', reservation = data["reservation"],reservation_stay=[d["parent"] for d in data_for_change_stays if d["can_change_stay"] == True]) 
        frappe.msgprint("Change stay successfully")


        
        return [d for d in data_for_change_stays if d["can_change_stay"]==False]
    else:
        return [d for d in data_for_change_stays if d["can_change_stay"]==False]


def change_stay(data):
    #this method is do not have validation
    doc = frappe.get_doc("Reservation Stay",data['parent'])
    doc.is_override_rate = 'is_override_rate' in data and data['is_override_rate']

    for s in doc.stays:
        if s.name == data['name']:
            s.start_date = data['start_date']
            s.end_date = data['end_date']
            if  date_diff(s.end_date, s.start_date)<=0:
                frappe.db.sql("delete from `tabReservation Stay Room` where name='{}'".format(s.name))
                frappe.db.sql("delete from `tabTemp Room Occupy` where stay_room_id='{}'".format(s.name))
                frappe.db.sql("delete from `tabRoom Occupy` where stay_room_id='{}'".format(s.name))
                frappe.db.sql("delete from `tabReservation Room Rate` where stay_room_id='{}'".format(s.name))



    if hasattr(data,"note"):
        doc.change_stay_note = data["note"]  
        
    doc.save()

    if doc:
        #regenerate rate is base on field name generate_new_stay_rate_by in data object
        #there are 2 value
        #1. stay_rate get from last and first stay rate
        #2 is from rate plan
        # we not enqueue this because we want to get rate for update to reservation
        update_reservation_stay_room_rate_after_resize(data=data,stay_doc= doc)
        frappe.enqueue("edoor.edoor.doctype.reservation_stay.reservation_stay.change_room_occupy", queue='short', self = doc)

    return doc

def can_change_stay_date(data):
    
    room_id = ""
    
    if 'room_id' in data and data["room_id"]:
        room_id = data["room_id"]

    
    # when we change stay date from drap and drop in room chart calendar we allow to overlap

    if frappe.db.get_single_value("eDoor Setting","enable_over_booking")==0: 
        if room_id:        
            check_room_occupy = frappe.db.sql("select stay_room_id, date from `tabTemp Room Occupy` where is_departure = 0 and date between %(start_date)s and %(end_date)s and stay_room_id<>%(stay_room_id)s and room_id=%(room_id)s limit 1",
                {"start_date":data["start_date"],"end_date":add_to_date(data["end_date"],days=-1),"stay_room_id":data["name"],"room_id":data["room_id"]},
                as_dict = 1
                )
            
            if check_room_occupy:
                return {
                        "can_change_stay": False, 
                        "reservation_stay": data["parent"],
                        "message":_("You cannot change stay of this reservation. Because this room is not available or block on {}".format(frappe.format(check_room_occupy[0]["date"]),{"fieldtype":"Date"}) )
                    }
            
                


        #check room type occupy
        available_room = check_room_type_availability(
            property=data["property"],
            room_type_id=data["room_type_id"],
            start_date=data["start_date"],
            end_date=data["end_date"],
            exclude_stay_room_id=data["name"]
        )

         
        if available_room[0]["total_vacant_room"]<=0:
            return {
                    "can_change_stay": False, 
                    "reservation_stay": data["parent"],
                    "message":"You cannot change stay of this reservation. Because you don't have enough room for room type {}".format(available_room[0]["room_type"])
                }
            
    else:
        #check if the room is block
        if room_id:        
            check_room_occupy = frappe.db.sql("select stay_room_id, date from `tabTemp Room Occupy` where type='Block' and date between %(start_date)s and %(end_date)s and stay_room_id<>%(stay_room_id)s and room_id=%(room_id)s limit 1",
                {"start_date":data["start_date"],"end_date":add_to_date(data["end_date"],days=-1),"stay_room_id":data["name"],"room_id":data["room_id"]},
                as_dict = 1
                )
            
            if check_room_occupy:
                return {
                    "can_change_stay": False, 
                    "reservation_stay": data["parent"],
                    "message":_("You cannot change stay of this reservation. Because this room is not available or block on {}".format(frappe.format(check_room_occupy[0]["date"]),{"fieldtype":"Date"}) )
                }
            
    
    doc = frappe.get_doc("Reservation Stay",data['parent'])
    
    #validate move room that have mulltiple stay is not allow to change stay date
    stay_room = [d for d in  doc.stays if d.name ==data["name"]][0]


        

    # validate if reservation is check in and they and they already stay so we cannot 

    working_day  =get_working_day(doc.property)
    if doc.stays.index(stay_room)==0:
        if getdate( stay_room.start_date) != getdate(data["start_date"]) and  getdate(  working_day["date_working_day"])>= getdate( stay_room.start_date) and doc.reservation_status =='In-house':
            return {
                    "can_change_stay": False, 
                    "reservation_stay": data["parent"],
                    "message":_("Checked-In reservation is not allow to change arrival date")
                }
            
        
        if  getdate(working_day["date_working_day"])>=getdate( stay_room.start_date) and doc.reservation_status =='In-house' and getdate(stay_room.start_date) !=getdate(data["start_date"]) :
            return {
                    "can_change_stay": False, 
                    "reservation_stay": data["parent"],
                    "message":_("Checked-In reservation is not allow to change arrival date")
            }
        
        
   
    #check if current dsate date range have room block
    if hasattr(data,"room_id") and data["room_id"]: 
        block_data =frappe.db.sql("select name from `tabTemp Room Occupy` Where  type='Block' and room_id=%(room_id)s and date between %(start_date)s and %(end_date)s",
                                {
                                    "room_id":data["room_id"],
                                    "start_date":data["start_date"],
                                    "end_date":add_to_date(getdate(  data["end_date"]),days=-1)
                                },as_dict=1)
        if block_data:
            return {
                    "can_change_stay": False, 
                    "reservation_stay": data["parent"],
                    "message":"You cannot change stay or extend stay on a block room"
            }
    
    data["can_change_stay"] = True
    return data

@frappe.whitelist()
def group_change_rate_type(data):
    #data is 
    # {
    #     "start_date", "end_date", "rate_type", "is_override_rate"
    # }
    

    frappe.msgprint("Change rate type successfully")

