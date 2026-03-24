import frappe
import edoor.channel_managers.exely.availability as exely_availability

@frappe.whitelist()
def re_sync_fail_job():
    properties =frappe.db.sql( "select distinct  property, provider from `tabChannel Manager Sync Data Log`",as_dict = 1)
    
    if properties:
        for d in properties:
            if d.get("provider") == "Exely": 
                exely_availability.update_room_availability(d.get("property"))