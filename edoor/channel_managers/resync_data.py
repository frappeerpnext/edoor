import frappe
import edoor.channel_managers.exely.availability as exely_availability

from edoor.channel_managers.utils import get_sync_action_status,get_channal_manager_info

@frappe.whitelist()
def re_sync_fail_job():
    delete_past_sync_data()
    properties =frappe.db.sql( "select distinct  property, provider,request_type from `tabChannel Manager Sync Data Log`",as_dict = 1)

    if properties:
        
        for d in properties:
            # check from cached synch status is temporary stop 
            # we do this to prevent data from first upload
            if str(frappe.cache.get_value(f"{d.get('property')}_channel_manager_stop_resync_fail_job")) == "1":
                continue
            
            property_name = d.get("property")
            cm_info = get_channal_manager_info(d.get("property"))
            if not cm_info:
                clean_sync_data_log(d.get("property"),False)
            if cm_info.get("enable") == 0:
                clean_sync_data_log(d.get("property"),False)


            if d.get("provider") == "Exely": 

                if d.get("request_type") == "Availability update":
                    frappe.enqueue(
                        "edoor.channel_managers.exely.availability.sync_room_availability",
                        queue="short" if frappe.conf.get("developer_mode") else "channel_manager",
                        property=property_name
                    )

                elif d.get("request_type") == "Prices update":

                    frappe.enqueue(
                        "edoor.channel_managers.exely.price_manager.sync_room_rate",
                        queue="short" if frappe.conf.get("developer_mode") else "channel_manager",
                        property=property_name
                    )
                elif d.get("request_type") == "Restriction update":
                    frappe.enqueue(
                        "edoor.channel_managers.exely.room_restriction.sync_room_restriction",
                        queue="short" if frappe.conf.get("developer_mode") else "channel_manager",
                        property=property_name
                    )

    frappe.db.commit()


def clean_sync_data_log(propety,run_commit = True):
    sql="delete from `tabChannel Manager Sync Data Log` where property = %(property)s"
    frappe.db.sql(sql,{"property":property})
    if run_commit:
        frappe.db.commit()
    




def delete_past_sync_data():
    frappe.db.sql("delete from `tabChannel Manager Sync Data Log` where date<CURDATE()")
    frappe.db.commit()


@frappe.whitelist(methods="POST")
def restart_sync_data_to_channel_manager(property,request_type,provider=None):
    status = get_sync_action_status(property = property,request_type = request_type,provider=provider)
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
          
            if request_type=="Prices update" and provider == "Exely":
                 
                frappe.enqueue(
                    "edoor.channel_managers.exely.price_manager.sync_room_rate",
                    queue="short" if frappe.conf.get("developer_mode") else "channel_manager",
                        property=property
                )
            elif request_type=="Restriction update" and provider == "Exely":
                frappe.enqueue(
                    "edoor.channel_managers.exely.room_restriction.sync_room_restriction",
                    queue="short" if frappe.conf.get("developer_mode") else "channel_manager",
                    property=property
                )

              
    
    return "Success"

