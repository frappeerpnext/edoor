import frappe
import requests
import xmltodict
from datetime import datetime
from edoor.channel_managers.exely.utils import get_exely_property_code,get_exely_room_type_code
from edoor.channel_managers.utils import get_sync_max_date,get_sync_session_id, group_date_ranges,get_channal_manager_info,get_occupancy_codes,can_sync_data,delete_synced_data_log,add_cm_task
from edoor.channel_managers.exely.soap_request import send_soap_request
from edoor.channel_managers.exely.rate_limit import get_rate_limit,update_rate_limit_balance
from frappe.utils import getdate, add_days,now,today
from epos_restaurant_2023.custom_socket_client import emit_event
from itertools import groupby
import json
from lxml import etree
from itertools import product
from frappe.utils import add_to_date, now_datetime
import time

REQUEST_TYPE = "Availability update"


@frappe.whitelist()
def testme():
    return sync_room_availability("ESTC HOTEL 6")
  

@frappe.whitelist()
def sync_room_availability(property=None,retry_sync =True):
    if not property:
        properties = frappe.db.sql("select name from `tabBusiness Branch`",as_dict=1)
    else:
        properties = [{"name":property}]

    change_data =[]
    room_type_limit=None
    
    error_code = None

    for p in properties:
        cm_info = get_channal_manager_info(p.get("name"))
        availability_blocks = list(set([d.availability_block for d in cm_info.rate_plans if d.availability_block]))
      
       


        if not can_sync_data(property = p.get("name"), title ='Availability update',provider="Exely"):
            frappe.throw("Data sync to Exely is temporarily blocked. Please check the sync status.")

        # reset session id on pending 
        frappe.db.sql("update `tabChannel Manager Sync Data Log` set sync_session_id = '' where request_type = %(request_type)s and  sync_session_id <> '' and property=%(property)s" ,{"request_type":REQUEST_TYPE,"property":p.get("name")})
        

        room_type_data = frappe.db.sql("select distinct room_type from `tabChannel Manager Sync Data Log` where request_type = %(request_type)s and property = %(property)s and provider=%(provider)s",{
                "property":p.get("name"),
                "request_type":REQUEST_TYPE,
                "provider": cm_info.get("provider")
            },
            as_dict = 1
        )
        room_types = [d.get("room_type") for d in room_type_data]

        # get room type limit and update session id to data to sync record
        # this is very important to avoid rate limit to CM
        room_type_limit =  get_rate_limit(property =  p.get("name"),room_types = room_types)
        for rt_key in room_type_limit:
            room_type_limit[rt_key] = int( room_type_limit[rt_key] / max(1,len(availability_blocks or [])) )

        
        session_id = get_sync_session_id(room_type_limit = room_type_limit,request_type=REQUEST_TYPE)

        _group_data = get_group_availability_data(session_id)  

        # Mulitple group data by invBlockCode
        if len((availability_blocks or []))>0:
            group_data = [
            {
                **d,
                "inv_block_code": inv_block_code
            }
            for d, inv_block_code in product(_group_data,availability_blocks)
            ]
        else:
            group_data = _group_data
      


        
        

        if group_data:
            soap_body = build_availability_xml(property = p.get("name"), group_data=group_data)

            
            
            response =  send_soap_request(p.get("name"),"OTA_HotelAvailNotifRQ",soap_body)
            


            # add sync log 
            doc = {
                "property": p.get("name"),
                "doctype":"Channel Manager Sync Log",
                "provider":"Exely",
                "request_type":REQUEST_TYPE,
                "status" : response.get("status"),
                "data": frappe.as_json(group_data),
                "response_text": response.get("response_text"),
                "response":frappe.as_json(response.get("data")),
            }
            error_code = response.get("error_code")

            if error_code:
                doc["sync_action"] = error_code.get("action")
                if error_code.get("action") == "Delay Sync" and error_code.get("delay"):
                    doc["sync_until"] =   add_to_date(now_datetime(),seconds = error_code.get("delay"))

            
            
            sync_log_doc=frappe.get_doc(doc).insert(ignore_permissions=True)
            sync_log_doc.add_comment(
                comment_type="Comment",
                text= soap_body
            )

            # add channel manager task to alert user to take action
            if error_code:
                if doc.get("sync_action") == "Stop Sync":
                    
                    
                    task_doc = {
                        "property":sync_log_doc.property,
                        "subject": "Sync {0} has been stoped.".format(doc.get("request_type")),
                        "description":  response.get("response_text"),
                        "reference_type": "Channel Manager Sync Log",
                        "reference_name": sync_log_doc.name,
                        "priority":"High"
                    }

                    add_cm_task(task_doc,run_commit=False)

                    

            

            # check success by have warning
            if response.get("status") == "Success":
                # update rate limit 
                # get actual count by session id
                sql = "select room_type, count(*) as total from `tabChannel Manager Sync Data Log` where sync_session_id = %(session_id)s group by room_type"
                change_data = frappe.db.sql(sql,{"session_id":session_id},as_dict = 1)
                for cd in change_data:
                    update_rate_limit_balance(p.get("name"), cd.get("room_type"), cd.get("total"))

                # return soap_body
                delete_synced_data_log(session_id=session_id,provider="Exely",request_type=REQUEST_TYPE, run_commit=False)
                emit_event("ChannelManagerUpdate",{
                    "action":"alert_cm_sync_message",
                    "property": p.get("name"),
                    "status":response.get("status"),
                    "title":"Sync Availabilty Successfully",
                    "message": "Room availability has been successfully synced with the channel manager.",
                    "docname": sync_log_doc.name
                })
            else:
                
                emit_event("ChannelManagerUpdate",{
                    "action":"alert_cm_sync_message",
                    "property": p.get("name"),
                    "status":response.get("status"),
                    "title":"Sync Room Availabilty Fail",
                    "message": response.get("response_text"),
                    "docname": sync_log_doc.name
                })
                        

    
    frappe.db.commit()
    
    if retry_sync and not error_code:
        resync_pending_availability_data(property)


    return "Success"


def get_group_availability_data(session_id):
    max_date = get_sync_max_date()
    sql= """
        select 
            date,
            room_type,
            value
        from `tabChannel Manager Sync Data Log`
        where
            date between CURDATE() and %(max_date)s  and
            sync_session_id = %(session_id)s and 
            request_type = %(request_type)s 
        order by room_type,date
    """
    
    data = frappe.db.sql(sql,{"session_id":session_id,"request_type":REQUEST_TYPE,"max_date":max_date},as_dict = 1)
  
    
    results = []

    for room_type, items in groupby(data, key=lambda x: x["room_type"]):

        items = list(items)

        start = items[0]["date"]
        end = items[0]["date"]
        last_date = getdate(start)
        booking_limit = items[0]["value"]

        for r in items[1:]:

            current_date = getdate(r["date"])
            if (
                r["value"] == booking_limit
                and current_date == add_days(last_date, 1)
            ):
                end = r["date"]

            else:

                results.append({
                    "room_type": room_type,
                    "start": start,
                    "end": end,
                    "booking_limit": booking_limit
                })

                start = r["date"]
                end = r["date"]
                booking_limit = r["value"]

            last_date = current_date

        results.append({
            "room_type": room_type,
            "start": start,
            "end": end,
            "booking_limit": booking_limit
        })

    return results
 

def build_availability_xml(property,group_data):

    hotel_code = get_exely_property_code(property)
    

    root = etree.Element(
        "OTA_HotelAvailNotifRQ",
        xmlns="http://www.opentravel.org/OTA/2003/05",
        Version="1.17"
    )


    messages = etree.SubElement(root, "AvailStatusMessages", HotelCode=hotel_code)
    
    for r in group_data:
        msg = etree.SubElement(
            messages,
            "AvailStatusMessage",
            BookingLimit=str(r["booking_limit"])
        )
 
        if r.get("inv_block_code"):
            etree.SubElement(
                msg,
                "StatusApplicationControl",
                Start=str(r["start"]),
                End=str(r["end"]),
                InvTypeCode=get_exely_room_type_code(r.get("room_type")),
                InvBlockCode = r.get("inv_block_code")

            )
        else:
            etree.SubElement(
                msg,
                "StatusApplicationControl",
                Start=str(r["start"]),
                End=str(r["end"]),
                InvTypeCode=get_exely_room_type_code(r.get("room_type"))

            )

    return etree.tostring(root, pretty_print=True).decode()



def resync_pending_availability_data(property=None):

    if not property:
         properties = frappe.db.sql("select name from `tabBusiness Branch`",as_dict=1)
    else:
        properties = [{"name":property}]

    for p in properties:
        sql ="""
            select 
                distinct room_type 
            from `tabChannel Manager Sync Data Log` 
            where 
                property = %(property)s and 
                provider='Exely' and 
                request_type = %(request_type)s and 
                coalesce(sync_session_id,'')  = ''
        """

        room_types = frappe.db.sql(sql,{"property":p.get("name"),"request_type":REQUEST_TYPE},as_dict = 1)
        room_types = [d.get("room_type")  for d in room_types]
        if len(room_types)>0:
            room_type_limit =  get_rate_limit(property =  p.get("name"),room_types = room_types)
            # this function return as dict with key as room_type
            # {"RT-0001":1460,"RT-0002":1460,"RT-0003":1460,"RT-0004":1460}
            if any(v > 0 for v in room_type_limit.values()):
                time.sleep(2)
                frappe.enqueue(
                    "edoor.channel_managers.exely.availability.sync_room_availability",
                    queue="short" if frappe.conf.get("developer_mode") else "channel_manager",
                    property=property ,
                    retry_sync = False
                )


      


def get_total_value_change(data):
    total = 0
    for row in data:
        start = getdate(row["start"])
        end = getdate(row["end"])

        # inclusive range
        days = (end - start).days + 1

        total += days

    return total
