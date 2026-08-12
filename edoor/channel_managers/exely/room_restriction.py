import frappe
from edoor.channel_managers.utils import group_date_ranges,get_channal_manager_info,get_occupancy_codes,can_sync_data,get_date_range
from edoor.channel_managers.exely.utils import get_exely_property_code,get_exely_room_type_code,get_edoor_rate_type, get_edoor_room_type_id
from edoor.channel_managers.utils import get_sync_session_id,add_cm_task,delete_synced_data_log
from edoor.channel_managers.exely.soap_request import send_soap_request
from edoor.channel_managers.exely.rate_limit import get_rate_limit,update_rate_limit_balance
from frappe.utils import now_datetime, add_to_date,getdate,today,add_days
from epos_restaurant_2023.custom_socket_client import emit_event
from itertools import groupby
from frappe.rate_limiter import rate_limit
from edoor.api.room_restriction import RESTRICTION_TYPE_PREFIX
from edoor.api.utils import make_hash,generate_unique_dates




    
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
                
                
                session_id = get_sync_session_id(room_type_limit = room_type_limit,rate_type=rp,request_type=REQUEST_TYPE,order_by='room_type,restriction_type,date')

                
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
        order by room_type,restriction_type,date

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
    pass



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
    

@frappe.whitelist()
def testme():
    return get_room_restriction_from_channel_manager(
        property="ESTC HOTEL 6",
        cm_hotel_code="501674",
        add_cm_sync_log_when_no_data=False

    )

@rate_limit(limit=10, seconds=60)
def get_room_restriction_from_channel_manager( 
        property , 
        cm_hotel_code,
        add_cm_sync_log_when_no_data = True,
        notify_user=False
    ):
    

    # validate if can sync data or not 
    if not can_sync_data( request_type =  "Restriction update", property = property, provider="Exely"):
        frappe.throw("The room restriction sync from the channel manager has been blocked. Please check the sync status.") 

    # emit channel manager loading notification
    emit_event("ChannelManagerUpdate",{
        "action":"update_cm_notification_status",
        "property":property,
        "status":True
    })
    
    root = etree.Element(
        "OTA_HotelAvailGetRQ",
        xmlns="http://www.opentravel.org/OTA/2003/05",
        Version="1.17"
    )
    

    HotelAvailRequests = etree.SubElement(root, "HotelAvailRequests")
    HotelAvailRequest = etree.SubElement(HotelAvailRequests, "HotelAvailRequest")
    etree.SubElement(HotelAvailRequest, "HotelRef" ,HotelCode = cm_hotel_code)
 
    
    soap_body = etree.tostring(root, pretty_print=True).decode()

   
    
    response =  send_soap_request(property,"OTA_HotelAvailGetRQ",soap_body)
 

    # prepare data for cm sync log doc
    cm_sync_doc = {
            "property": property,
            "doctype":"Channel Manager Sync Log",
            "provider":"Exely",
            "request_type":REQUEST_TYPE,
            "status" : response.get("status"),
            "response_text": f"{(response.get('response_text') or '').strip() }.\nPlease verify the room restriction synchronization settings in the Exely Channel Manager and ensure that the settings in the Channel Manager and PMS are consistent and correctly matched."
            
    }
    
     
    if response.get("status") == "Success":
        OTA_HotelAvailGetRS= response.get("data").get("s:Envelope").get("s:Body").get("OTA_HotelAvailGetRS")


        # no room rate data 
        if not OTA_HotelAvailGetRS.get("RatePlans"):
            if add_cm_sync_log_when_no_data:
                frappe.db.sql("delete from `tabChannel Manager Sync Log` where request_type = %(request_type)s and coalesce(rate_type,'')='' and coalesce(data,'')='' and coalesce(response_text,'') = '' ",{"request_type":REQUEST_TYPE})

                frappe.get_doc(cm_sync_doc).insert(ignore_permissions=True)
                frappe.db.commit()
            # emit socket event to disable loading in cm notification
            
            emit_event("ChannelManagerUpdate",{
                "action":"update_cm_notification_status",
                "property":property,
                "status":False
            })

            if notify_user:
                emit_event("ChannelManagerUpdate",{
                    "action":"update_sync_rate_plan_status",
                    "property":property,
                    "status":"Success",
                    "title":"Sync Room Restriction",
                    "message":"Sync room restriction from channel manager successfully"
                })
                
            return "Complete, No more restriction to sync"


        room_restriction_data =  get_room_restriction_group_data_from_cm(OTA_HotelAvailGetRS)
        

        
        # update room restriction data to cm sync log doc
        cm_sync_doc["data"] = frappe.as_json(room_restriction_data)

       
        # update rate type to cm sync data log get rate type from first record of room_restriction_data
        cm_sync_doc["rate_type"] = get_edoor_rate_type(room_restriction_data[0].get("cm_rate_plan_code"))

        room_restriction_update_result =  bulk_update_room_restriction(property = property, room_restriction_data = room_restriction_data)
       
        # check room restriction result if have warning then log to do and cm sync log

        # notify back to cm that we update success 
        if not room_restriction_update_result.get("warnings"):
            RateAmountMessageId = response.get("data").get("s:Envelope").get("s:Body").get("OTA_HotelAvailGetRS").get("RatePlans").get("RatePlan").get("AvailStatusMessageId")
            confirm_request_response =  send_notify_sync_room_restriction_request(property = property, hotel_code = cm_hotel_code, message_id =  RateAmountMessageId)
            

           
            
        else:
            # append warning text to reponse text in cm sync data log
            # change sync status to warning
            cm_sync_doc["status"] = "Warning"
            warning_message = "\n".join(price_update_result.get("warnings"))
            cm_sync_doc["response_text"] =  cm_sync_doc["response_text"] +"\n"+ warning_message

            # add to do stop sync prices update
            cm_sync_doc["sync_action"] = "Stop Sync"
    else:
        # when reponse fail 
        if "error_code" in response:
            cm_sync_doc["sync_action"] = response.get("error_code").get("action")
 

        


    # save data to cm sync log
    sync_log_doc = frappe.get_doc(cm_sync_doc).insert(ignore_permissions=True)

    if (cm_sync_doc.get("sync_action") or "") == "Stop Sync":
        description = f"{(cm_sync_doc.get('response_text') or '').strip() }.\nPlease verify the room restriction synchronization settings in the Exely Channel Manager and ensure that the settings in the Channel Manager and PMS are consistent and correctly matched."

        task_doc = {
            "property":property,
            "subject": "Sync {0} has been stoped.".format(cm_sync_doc.get("request_type")),
            "description": description ,
            "reference_type": "Channel Manager Sync Log",
            "reference_name": sync_log_doc.name,
            "priority":"High",
            "custom_job_name":"resync_data.sync_room_restriction_from_channel_manager"
        }

        add_cm_task(task_doc,run_commit=False)

        # Stop schedule task
        frappe.db.sql("update `tabScheduled Job Type` set stopped =1 where name = 'resync_data.sync_room_restriction_from_channel_manager'")


    frappe.db.commit()
 

    # emit socket event  to notify client


    # check cm_sync_doc if status success start send sync request until all room rate are
    # fetch from cm 

    if (cm_sync_doc.get("sync_action") or "") != "Stop Sync":
        time.sleep(10)
        frappe.enqueue(
            "edoor.channel_managers.exely.room_restriction.get_room_restriction_from_channel_manager",
            queue="long" if frappe.conf.get("developer_mode") else "channel_manager",
                property=property,
                cm_hotel_code = cm_hotel_code,
                add_cm_sync_log_when_no_data = False,
                notify_user = notify_user
        )
    



    



    return "Complete"



@frappe.whitelist()
def get_room_restriction_group_data_from_cm(data = None):
    from edoor.channel_managers.exely.dummy_data import room_restriction_data
    if not data:
        data = room_restriction_data
    result = []
    # return data expect
    # {
    #     "cm_rate_plan_code":111,
    #     "start_date":,
    #     "end_date",
    #     "restriction_type":
    #     "value":
    # } 

    # get rate plan  if dict convert to array dict
    def get_rate_plans(data):
        if isinstance(data.get("RatePlans").get("RatePlan"), dict):
            return [data.get("RatePlans").get("RatePlan")]
            
        return data.get("RatePlans").get("RatePlan")
        
    def get_restriction(data):
        if isinstance(data.get("AvailStatusMessages").get("AvailStatusMessage"), dict):
            return [data.get("AvailStatusMessages").get("AvailStatusMessage")]
        return data.get("AvailStatusMessages").get("AvailStatusMessage")

    def get_LengthsOfStay(data):
        if isinstance(data.get("LengthsOfStay"), dict):
            return [data.get("LengthsOfStay")]
        return data.get("LengthsOfStay")
        
    def get_LengthOfStay(data):
        if isinstance(data.get("LengthOfStay"), dict):
            return [data.get("LengthOfStay")]
        return data.get("LengthOfStay")

    def get_LOS_Pattern(data):
        if isinstance(data.get("LOS_Pattern"), dict):
            return [data.get("LOS_Pattern")]
        return data.get("LOS_Pattern") 

    def get_RestrictionStatus(data):
        if isinstance(data.get("RestrictionStatus"), dict):
            return [data.get("RestrictionStatus")]
        return data.get("RestrictionStatus") 



 
 
    
    for rp in get_rate_plans(data):
        # return get_rates(rp)
        for rs in get_restriction(rp):
            _base_row = {
                "cm_rate_plan_code": rp.get("@RatePlanCode"),
                "start_date": rs.get("StatusApplicationControl").get("@Start"),
                "end_date": rs.get("StatusApplicationControl").get("@End"),
                "cm_room_type_code": rs.get("StatusApplicationControl").get("@InvTypeCode"),
                
            }
            
            LengthsOfStay = get_LengthsOfStay(rs) or []
            for a in LengthsOfStay:
                LengthOfStay = get_LengthOfStay(a) or []
                
                
                # leng of stay rule
                for b in LengthOfStay:
                    _row = {**_base_row}
                   
                    if  "@ArrivalDateBased" in a:
                        if "@MinMaxMessageType" in b:
                            if b.get("@MinMaxMessageType") == "RemoveMinLOS" :
                                _row["restriction_type"] = "MinLosArrival"
                                _row["value"] = ""
                            elif b.get("@MinMaxMessageType") == "RemoveMaxLOS" :
                                _row["restriction_type"] = "MaxLosArrival"
                                _row["value"] = ""
                            elif b.get("@MinMaxMessageType") == "SetMinLOS" :
                                # SET MinLos
                                _row["restriction_type"] = "MinLosArrival"
                                _row["value"] = b.get("@Time")
                            elif b.get("@MinMaxMessageType") == "SetMaxLOS" :
                                # SET MaxLos
                                _row["restriction_type"] = "MaxLosArrival"
                                _row["value"] = b.get("@Time")
                            
                        # append row to result
                        result.append(_row)
                    else:
                        # remove MinLOS set MinLOS = ""
                        if "@MinMaxMessageType" in b:
                            if b.get("@MinMaxMessageType") == "RemoveMinLOS" :
                                _row["restriction_type"] = "MinLos"
                                _row["value"] = ""
                            elif b.get("@MinMaxMessageType") == "RemoveMaxLOS" :
                                _row["restriction_type"] = "MaxLos"
                                _row["value"] = ""
                                
                            elif b.get("@MinMaxMessageType") == "SetMinLOS" :
                                # SET MinLos
                                _row["restriction_type"] = "MinLos"
                                _row["value"] = b.get("@Time")
                            elif b.get("@MinMaxMessageType") == "SetMaxLOS" :
                                # SET MaxLos
                                _row["restriction_type"] = "MaxLos"
                                _row["value"] = b.get("@Time")

                            # append row to result
                            result.append(_row)
                
                    # full patern lost
                    LOS_Pattern = get_LOS_Pattern(b) or []

                    for p in LOS_Pattern:
                        if "@FullPatternLOS" in p:
                            _row = {**_base_row,
                                "restriction_type": "FullPatternLos",
                                "value": p.get("@FullPatternLOS")
                            }
                            result.append(_row)
            
            # restriction status
            
            RestrictionStatus = get_RestrictionStatus(rs) or []
            for _rs in RestrictionStatus:
                if "@Status" in _rs:
                    restriction_type = "Closed"
                    if "@Restriction" in _rs :
                        if  _rs.get("@Restriction") == "Arrival":
                            restriction_type = "Cta"
                        elif  _rs.get("@Restriction") == "Departure":
                            restriction_type = "Ctd"


                    _row = {**_base_row,
                            "restriction_type": restriction_type,
                            "value": 1 if _rs.get("@Status") =="Close" else 0
                        }
                    result.append(_row)
                
                # MinAdvBooking and MaxAdvBooking 
                
                if "@MinAdvancedBookingOffset" in _rs:
                    _row = {
                        **_base_row,
                        "restriction_type":"MinAdvBooking",
                        "value": _rs.get("@MinAdvancedBookingOffset") 
                    } 
                    result.append(_row)
                if "@MaxAdvancedBookingOffset" in _rs:
                    _row = {
                        **_base_row,
                        "restriction_type":"MaxAdvBooking",
                        "value": _rs.get("@MaxAdvancedBookingOffset") 
                    } 
                    result.append(_row)

 

    return result

 

def bulk_update_room_restriction(property , room_restriction_data):
  
    values = []
    warnings = set()
    for rs in room_restriction_data:
        rate_type = get_edoor_rate_type(rs.get("cm_rate_plan_code"))
        # check if rate plan not valid stop sync add to do log and notify to user and stop sync imediately
        if not rate_type:
            warnings.add(_("No edoor rate plan mapping for exely rate plan code {0}. Please check in channel manager integration".format(rs.get("cm_rate_plan_code"))))
            break


        room_type_id = get_edoor_room_type_id(rs.get("cm_room_type_code"))
        room_type_name = frappe.get_cached_value("Room Type", room_type_id,"room_type")
        dates = get_date_range(rs.get("start_date"), rs.get("end_date"))
        for dt in dates:
            
            
            has_text = f"rs{RESTRICTION_TYPE_PREFIX.get(rs.get('restriction_type'))}{rate_type}{room_type_id}{dt}"
            row_name = make_hash(has_text)

            _value = (
                f"('{row_name}', '{property}', '{rs.get('restriction_type')}', "
                f"'{dt}', '{rate_type}', '{room_type_id}', '{rs.get('value')}','{rs.get('value')}')"
            )

            values.append(_value)
   

    if values and not warnings:
        value_str = ", ".join(values)
        
        sql = f"""
            INSERT INTO `tabRoom Restriction`
            (`name`,`property`,`restriction_type`, `date`,`rate_type`, `room_type_id`, `value`,`old_value`)
            VALUES {value_str}
            ON DUPLICATE KEY UPDATE
            value = VALUES(value),
            old_value = VALUES(old_value)

        """

 

        frappe.db.sql(sql)

        frappe.db.commit()

 
    return {
        "room_restriction_value_count":len(values),
        "warnings":list(warnings)
    }

def send_notify_sync_room_restriction_request(property,hotel_code,message_id):
    root = etree.Element(
        "OTA_NotifReportRQ",
        xmlns="http://www.opentravel.org/OTA/2003/05",
        Version="1.17"
    )
    Success = etree.SubElement(root, "Success")
    NotifDetails = etree.SubElement(root, "NotifDetails",HotelCode=hotel_code)
    HotelNotifReport = etree.SubElement(NotifDetails, "HotelNotifReport")
    RatePlanMessages = etree.SubElement(HotelNotifReport, "RatePlanMessages")
    RatePlanMessage = etree.SubElement(RatePlanMessages, "RatePlanMessage",AvailStatusMessageId=str(message_id))
    etree.SubElement(RatePlanMessage, "Success")

    soap_body = etree.tostring(root, pretty_print=True).decode()
    response =  send_soap_request(property = property,ota_request = "OTA_NotifReportRQ",body_content =  soap_body,emit_socket_event = False)

    return response
