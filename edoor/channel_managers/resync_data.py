import frappe
import edoor.channel_managers.exely.availability as exely_availability

from edoor.channel_managers.utils import get_sync_action_status,get_channal_manager_info

@frappe.whitelist()
def re_sync_fail_job():
    properties =frappe.db.sql( "select distinct  property, provider,request_type from `tabChannel Manager Sync Data Log`",as_dict = 1)
    
    if properties:
        for d in properties:
            if d.get("provider") == "Exely": 
                exely_availability.update_room_availability(d.get("property"))

                



@frappe.whitelist(methods="POST")
def restart_sync_data_to_channel_manager(property,title,provider=None):
    status = get_sync_action_status(property = property,title = title,provider=provider)
    if not provider:
        cm_info = get_channal_manager_info(property)
        if cm_info:
            provider = cm_info.get("provider")
        else:
            frappe.throw("There is no channel manager integration setting available.")
    
    if status:
        if status.get("sync_action") == "Stop Sync":
            frappe.db.set_value("Channel Manager Sync Log",status.get("name"),"is_retry_sync",1)
            frappe.db.commit()
          
            if title=="Prices update" and provider == "Exely":
                 
                frappe.enqueue(
                    "edoor.channel_managers.exely.price_manager.sync_room_rate",
                    queue="short" if frappe.conf.get("developer_mode") else "channel_manager",
                        property=property
                )
            elif title=="Restriction update" and provider == "Exely":
                
              
    
    return "Success"

