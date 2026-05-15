import frappe
from edoor.channel_managers.utils import get_channal_manager_info
import copy
import time

@frappe.whitelist()
def get_data_upload_status(property = "ESTC HOTEL 6"):
   
    
    
    cm_info = get_channal_manager_info(property)
    room_types = [
        {
            "room_type":d.edoor_room_type,
            "room_type_name":d.room_type_name,
            "room_type_code":d.room_type_code
        }
        for d in cm_info.room_types 
        if d.edoor_room_type and d.room_type_code
    ]

    
    return { 
        "availability": get_availability_status(property=property, cm_info = cm_info,room_types=copy.deepcopy(room_types)),
        "room_rate":get_price_upload_status(property=property, cm_info = cm_info,room_types=copy.deepcopy(room_types)),
        "restriction":get_restriction_upload_status(property=property, cm_info = cm_info,room_types=copy.deepcopy(room_types)),
        "extra_service":get_extra_service_update_status(property=property, cm_info = cm_info)
    }


def get_availability_status(property=None, cm_info=None,room_types=None):
    
    if not cm_info:
        cm_info = get_channal_manager_info(property)
    if not room_types:
        room_types =copy.deepcopy( [
                        {
                            "room_type":d.edoor_room_type,
                            "room_type_name":d.room_type_name,
                            "room_type_code":d.room_type_code
                        }
                        for d in cm_info.room_types 
                        if d.edoor_room_type and d.room_type_code
                    ])

    data = []
    status = "Pending" if cm_info.initialized_availability_upload == 0 else "Complete"

    for rt in room_types:

        status_key = f"data_initialize_availability_{rt.get('room_type')}"
        rt["total_room"] = frappe.db.count("Room",{
            "room_type_id":rt.get("room_type"),
            "disabled":0
        })

        rt["status"] = "Complete" if status == "Complete" else ( frappe.cache().get_value(status_key) or "Pending")

        if rt.get("status") == "In Progress":
            filter ={
                "property":property,
                "room_type":rt.get("room_type"),
                "request_type": "Availability update"
            }
            if not frappe.db.exists("Channel Manager Data Sync Log",filter):
                rt["status"] = "Complete"


        data.append(rt)


    

    if not status == "Complete":
        if len([d for d in data if d.get("status") == 'In Progress'])>0:
            status = "In Progress"
        elif len([d for d in data if d.get("status") == 'Complete'])>0:
            status = "Complete"
    
    
    return {
        "sync_mode":cm_info.rooms_availability,
        "status": status,
        "room_types": data
    }

def get_price_upload_status(property=None, cm_info=None,room_types=None):
    def get_occupancy_codes(room_type):
        doc = frappe.get_cached_doc("Room Type",room_type)
        return [
            frappe.get_cached_value("Occupancy Code", d.occupancy_code, "title") or d.occupancy_code 
            for d in doc.rates if d.occupancy_code
        ]

    if not cm_info:
        cm_info = get_channal_manager_info(property)

    data = []
    status = "Pending" if cm_info.initialized_prices_upload == 0 else "Complete"
    for rt in room_types:
        status_key = f"data_initialize_room_rate_{rt.get('room_type')}"
        rt["total_room"] = frappe.db.count("Room",{
            "room_type_id":rt.get("room_type"),
            "disabled":0
        })

        rt["status"] = "Complete" if status == "Complete" else ( frappe.cache().get_value(status_key) or "Pending")
        rt["occupancy_codes"] = get_occupancy_codes(rt.get('room_type'))
        data.append(rt)

    

    if not status == "Complete":
        if len([d for d in data if d.get("status") == 'In Progress'])>0:
            status = "In Progress"
        elif len([d for d in data if d.get("status") == 'Complete'])>0:
            status = "Complete"
    
    
    return {
         "sync_mode":cm_info.prices_for_accommodation,
        "status": status,
        "room_types": data
    }

 

def get_restriction_upload_status(property=None, cm_info=None,room_types=None):
    if not cm_info:
        cm_info = get_channal_manager_info(property)
    _restrictions = ["Closed","Cta","Ctd","MinLos","MaxLos","MinLosArrival","MaxLosArrival","MinAdvBooking","MaxAdvBooking","FullPatternLos"]
    restrictions =[]
    for rs in _restrictions:
        if cm_info.get(rs.lower())==1:
            restrictions.append(rs)

    data = []
    status =  None 
    if cm_info.initialized_restrictions_upload == 1:
        status =  "Complete"
    
    
    def get_status_by_restriction_code():
        restriction_data = []
        for rs in restrictions:
            restriction_cached_key = f"data_initialize_restriction_{rt.get('room_type')}_{rs}"
            restriction_data.append({
                "restriction": rs,
                "status": status or (frappe.cache().get_value(restriction_cached_key) or "Pending")
            })
        return  restriction_data

    for rt in room_types:
        status_key = f"data_initialize_restriction_{rt.get('room_type')}"
        rt["total_room"] = frappe.db.count("Room",{
            "room_type_id":rt.get("room_type"),
            "disabled":0
        })

        rt["status"] = status or ( frappe.cache().get(status_key) or "Pending")
        rt["restrictions"] = get_status_by_restriction_code()
        # check if restriction type sync status all complete then set status in room type = Complete also
        if any(x.get("status") == "In Progress" for x in rt["restrictions"]):
            rt["status"] = "In Progress" 
        else:
            if any(x.get("status") == "Pending" for x in rt["restrictions"]):
                rt["status"] = "Pending" 
            else:
                rt["status"] = "Complete" 

        

        data.append(rt)


  
    
    
    return {
        "sync_mode":cm_info.restrictions,
        "status": status,
        "restrictions":restrictions,
        "room_types": data
    }



 
def get_extra_service_update_status(property,cm_info):
     
    status = frappe.cache().get_value("data_initialize_extra_service_status") or "Pending"
    if cm_info.initialized_service_upload == 1:
        status = "Complete"
    return {
        "sync_mode":cm_info.prices_for_extra_services,
        "status":status,
        "extra_services":[
            {
                "service_code":"0001",
                "service_name":"Service name",
                "rate":45,
                "status":"Pending"
            }
        ]
    }