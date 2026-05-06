import frappe
from edoor.channel_managers.utils import group_date_ranges,get_channal_manager_info,get_occupancy_codes,can_sync_data
from edoor.channel_managers.exely.utils import get_exely_property_code,get_exely_room_type_code
from edoor.channel_managers.utils import get_sync_session_id,add_cm_task,delete_synced_data_log
from edoor.channel_managers.exely.soap_request import send_soap_request
from edoor.channel_managers.exely.rate_limit import get_rate_limit,update_rate_limit_balance
from frappe.utils import now_datetime, add_to_date,getdate,today,add_days
from epos_restaurant_2023.custom_socket_client import emit_event
from itertools import groupby


    
from lxml import etree

from decimal import Decimal
import time


 
 
REQUEST_TYPE = "Restriction update"


@frappe.whitelist()
def testme():
    emit_event("ChannelManagerUpdate",{"action":"update_cm_notification_status","property":"ESTC HOTEL 6", "status": True})

    time.sleep(3)
    emit_event("ChannelManagerUpdate",{"action":"update_cm_notification_status","property":"ESTC HOTEL 6", "status": False})


@frappe.whitelist()
def sync_room_restriction(property=None,retry_sync =True):
      
    if not property:
        properties = frappe.db.sql("select name from `tabBusiness Branch`",as_dict=1)
    else:
        properties = [{"name":property}]
    change_data =[]
    room_type_limit=None
    error_code = None
    for p in properties:
        
        if not can_sync_data(property = p.get("name"), title ='Restriction update',provider="Exely"):
            frappe.throw("Data sync to Exely is temporarily blocked. Please check the sync status.")

        # reset session id on pending 
        frappe.db.sql("update `tabChannel Manager Sync Data Log` set sync_session_id = '' where request_type = %(request_type)s and  sync_session_id <> '' and property=%(property)s" ,{"request_type":REQUEST_TYPE,"property":p.get("name")})
        

        rate_types = frappe.db.sql("select distinct room_type,rate_type from `tabChannel Manager Sync Data Log` where property = %(property)s and provider='Exely' and request_type=%(request_type)s",{"request_type":REQUEST_TYPE,"property":p.get("name")},as_dict = 1)
        
        if len(rate_types)>0:
            
            for rp in set([d.get("rate_type") for d in rate_types]):
                room_types = [d.get("room_type") for d in rate_types if d.get("rate_type") == rp]

                # get room type limit and update session id to data to sync record
                # this is very important to avoid rate limit to CM
                room_type_limit =  get_rate_limit(property =  p.get("name"),room_types = room_types)
                
                
                session_id = get_sync_session_id(room_type_limit = room_type_limit,rate_type=rp,request_type=REQUEST_TYPE)

                
                group_data = get_group_restriction_data(session_id,rp)   
                
             
              

                if group_data:
                     
                    soap_body = build_restriction_xml(property = p.get("name"), group_data=group_data,rate_type = rp)
                 
                    
                   
                    response =  send_soap_request(p.get("name"),"OTA_HotelAvailNotifRQ",soap_body)
                  
                   

                    # check response status and add sync log
                    
                
                    
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
                        "rate_type":rp
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
                        delete_synced_data_log(session_id=session_id ,request_type=REQUEST_TYPE , provider="Exely",cm_response = response,xml_body=soap_body,run_commit=False)
                        emit_event("ChannelManagerUpdate",{

                                "action":"update_sync_rate_plan_status",
                                "property": p.get("name"),
                                "status":"Success",
                                "title":"Sync Room Restriction",
                                "message":"Room restriction have been successfully synced to the channel manager."})

                    else:
                        
                        emit_event("ChannelManagerUpdate",{
                            "action":"update_sync_rate_plan_status",
                            "property": p.get("name"),
                            "status":response.get("status"),
                            "title":"Sync Room Restriction Fail",
                            "message": response.get("response_text"),
                            "docname": sync_log_doc.name
                        })
                        

    
    frappe.db.commit()
    
    if retry_sync and not error_code:
        resync_pending_restriction_data(property)


    return "Success"


def resync_pending_restriction_data(property=None):

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
                    "edoor.channel_managers.exely.restriction.sync_room_restriction",
                    queue="short" if frappe.conf.get("developer_mode") else "channel_manager",
                    property=property ,
                    retry_sync = False
                )


      






def get_group_restriction_data(session_id,rate_type):
    
    sql= """
        select 
            date,
            room_type,
            restriction_type,
            value
        from `tabChannel Manager Sync Data Log`
        where
            sync_session_id = %(session_id)s and 
            rate_type = %(rate_type)s and 
            request_type = %(request_type)s
        order by date,restriction_type

    """
    data = frappe.db.sql(sql,{"session_id":session_id, "rate_type":rate_type,"request_type":REQUEST_TYPE},as_dict = 1)
    restriction_types = set([d.get("restriction_type") for d in data])
    
    group_data = {}
    for rt in restriction_types:
        group_data[rt] = get_group_peroid_data([x for x in data if x.get("restriction_type") == rt])
        
    return group_data
 


def get_group_peroid_data(data):
 
    # remove past date
    data = [d for d in data if getdate( d.get("date"))>=getdate(today())]
     
    # sort by room_type and date
    
    data = sorted(data, key=lambda x: (x["room_type"], x["date"]))
    
    results = []

    for room_type, items in groupby(data, key=lambda x: x["room_type"]):

        items = list(items)

        start = items[0]["date"]
        end = items[0]["date"]
        last_date = getdate(start)
        value = items[0]["value"]

        for r in items[1:]:

            current_date = getdate(r["date"])

            if (
                r["value"] == value
                and current_date == add_days(last_date, 1)
            ):
                end = r["date"]

            else:
                results.append({
                    "room_type": room_type,
                    "start": str(start),
                    "end": str(end),
                    "value": value
                })
                start = r["date"]
                end = r["date"]
                value = r["value"]

            last_date = current_date

        results.append({
            "room_type": room_type,
            "start": str(start),
            "end": str(end),
            "value": value
        })
 
    return results



def get_unique_restriction_values_by_restriction_types(session_id,restriction_types,rate_type):
    xxx



def get_use_restriction_types(filters):
    # filters = {"session_id":"", "rate_type"}
    sql = """
        select 
            distinct 
            a.restriction_type
            
        from `tabChannel Manager Sync Data Log` a 
        where
            a.provider= 'Exely' and
            a.request_type = %(request_type)s  and 
            a.sync_session_id = %(session_id)s and 
            a.rate_type = %(rate_type)s
    """
    return frappe.db.sql(sql, {**filters,"request_type":REQUEST_TYPE},as_dict = 1)


def build_restriction_xml(property,group_data,rate_type):
     
    cm_info = get_channal_manager_info(property)
    rate_plan_code = [d for d in cm_info.get("rate_plans") if d.get("edoor_rate_plan") == rate_type]
    if len(rate_plan_code) == 0:
        frappe.throw("Sync room rate to exely channel manager fail. No rate plan code mapping for rate type " + rate_type)
    rate_plan_code = rate_plan_code[0].get("rate_plan_code")

    root = etree.Element(
        "OTA_HotelAvailNotifRQ",
        xmlns="http://www.opentravel.org/OTA/2003/05",
        Version="1.17"
    )


    AvailStatusMessages = etree.SubElement(root, "AvailStatusMessages", HotelCode=cm_info.get("property_code"))
    for restriction_type in  group_data:
      
        for d in group_data[restriction_type]:
            if restriction_type == "Closed":
                build_closed_tag(parent_tag = AvailStatusMessages,rate_type = rate_plan_code,data = d)
            elif restriction_type in ["Cta","Ctd"]:
                build_cta_ctd_tag(parent_tag = AvailStatusMessages,rate_type = rate_plan_code,data = d,restriction_type=restriction_type)
            elif restriction_type in ["MinLos","MaxLos"]:
                build_min_max_los_tag(parent_tag = AvailStatusMessages,rate_type = rate_plan_code,data = d,restriction_type = restriction_type)
            elif restriction_type in ["MinLosArrival","MaxLosArrival"]:
                build_min_max_los_arrival_tag(parent_tag = AvailStatusMessages,rate_type = rate_plan_code,data = d,restriction_type = restriction_type)
            elif restriction_type in ["MinAdvBooking","MaxAdvBooking"]:
                build_min_max_adv_booking_tag(parent_tag = AvailStatusMessages,rate_type = rate_plan_code,data = d,restriction_type = restriction_type )
            elif restriction_type =="FullPatternLos":
                build_full_pattern_los_tag(parent_tag = AvailStatusMessages,rate_type = rate_plan_code,data = d)

    
    
    return etree.tostring(root, pretty_print=True).decode()

def build_status_application_control_tag(parent_tag, rate_type,data):
    cm_room_type = get_exely_room_type_code(data.get("room_type"))
    etree.SubElement(parent_tag, 
                                    "StatusApplicationControl",
                                    Start=data.get("start") ,
                                    End=data.get("end"),
                                    InvTypeCode=cm_room_type,
                                    RatePlanCode = rate_type )

def build_closed_tag(parent_tag,rate_type,data):
    AvailStatusMessage =   etree.SubElement(parent_tag, "AvailStatusMessage")
    build_status_application_control_tag(AvailStatusMessage, rate_type,data)
    etree.SubElement(AvailStatusMessage, 
                                    "RestrictionStatus",
                                    Status= "Close" if str(data.get("value")) == "1" else "Open"
                    )

def build_cta_ctd_tag(parent_tag,rate_type,data,restriction_type):
    AvailStatusMessage =   etree.SubElement(parent_tag, "AvailStatusMessage")
    build_status_application_control_tag(AvailStatusMessage, rate_type,data)
    etree.SubElement(AvailStatusMessage, 
                                    "RestrictionStatus",
                                    Status= "Close" if str(data.get("value")) == "1" else "Open",
                                    Restriction="Arrival" if restriction_type == "Cta" else "Departure"
                    )
    
def build_min_max_los_tag(parent_tag,rate_type,data,restriction_type):
    AvailStatusMessage =   etree.SubElement(parent_tag, "AvailStatusMessage")
    build_status_application_control_tag(AvailStatusMessage, rate_type,data)
   
    LengthsOfStay = etree.SubElement(AvailStatusMessage, "LengthsOfStay")
    if data.get("value")=="":
        etree.SubElement(
            LengthsOfStay, 
            "LengthOfStay",
            MinMaxMessageType  =  "RemoveMinLOS" if restriction_type == "MinLos" else "RemoveMaxLOS"
        )
    else:

        etree.SubElement(
            LengthsOfStay, 
            "LengthOfStay",
            MinMaxMessageType  =  "SetMinLOS" if restriction_type == "MinLos" else "SetMaxLOS",
            Time = data.get("value")

        )

def build_min_max_los_arrival_tag(parent_tag,rate_type,data,restriction_type):
    AvailStatusMessage =   etree.SubElement(parent_tag, "AvailStatusMessage")
    build_status_application_control_tag(AvailStatusMessage, rate_type,data)
   
    LengthsOfStay = etree.SubElement(AvailStatusMessage, "LengthsOfStay", ArrivalDateBased="true")
    if data.get("value")=="":
        etree.SubElement(
            LengthsOfStay, 
            "LengthOfStay",
            MinMaxMessageType  =  "RemoveMinLOS" if restriction_type == "MinLosArrival" else "RemoveMaxLOS"
        )
    else:

        etree.SubElement(
            LengthsOfStay, 
            "LengthOfStay",
            MinMaxMessageType  =  "SetMinLOS" if restriction_type == "MinLosArrival" else "SetMaxLOS",
            Time = data.get("value")

        )

def build_min_max_adv_booking_tag(parent_tag,rate_type,data,restriction_type):
    AvailStatusMessage =   etree.SubElement(parent_tag, "AvailStatusMessage")
    build_status_application_control_tag(AvailStatusMessage, rate_type,data)
    if restriction_type == "MinAdvBooking":
        if data.get("value")=="":
            etree.SubElement(AvailStatusMessage, 
                                    "RestrictionStatus",
                                    MinAdvancedBookingOffset="-1"
                    )
        else:
            etree.SubElement(AvailStatusMessage, 
                                    "RestrictionStatus",
                                     MinAdvancedBookingOffset=data.get("value")
                    )
    else:
        if data.get("value")=="":
            etree.SubElement(AvailStatusMessage, 
                                    "RestrictionStatus",
                                    MaxAdvancedBookingOffset="-1"
                    )
        else:
            etree.SubElement(AvailStatusMessage, 
                                    "RestrictionStatus",
                                     MaxAdvancedBookingOffset=data.get("value")
                    )


 
def build_full_pattern_los_tag(parent_tag,rate_type,data):
    AvailStatusMessage =   etree.SubElement(parent_tag, "AvailStatusMessage")
    build_status_application_control_tag(AvailStatusMessage, rate_type,data)
    LengthsOfStay = etree.SubElement(AvailStatusMessage, "LengthsOfStay")
    LengthOfStay = etree.SubElement(LengthsOfStay, "LengthOfStay", MinMaxMessageType="FullPatternLOS")

    etree.SubElement(
        LengthOfStay, 
        "LOS_Pattern",
        FullPatternLOS = data.get("value")

    )
 
 
def validate_zerow_rate(data):
    frappe.throw("validate 0 rate")


 
def get_value_from_xml_by_tag(xml_text: str, path: str, namespaces=None):
    import xmltodict
    return xmltodict.parse(xml_text)
    
    

def normalize_amount(value):
    d = Decimal(value)
  
    if d == d.to_integral():
        return int(d)

    # otherwise return float without trailing zeros
    return float(d.normalize())
    