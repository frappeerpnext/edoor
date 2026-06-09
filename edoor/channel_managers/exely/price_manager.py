import frappe
from edoor.channel_managers.utils import group_date_ranges,get_channal_manager_info,get_occupancy_codes,can_sync_data,get_date_range,get_occupancy_code_mapping
from edoor.channel_managers.exely.utils import get_exely_property_code,get_exely_room_type_code,get_edoor_rate_type, get_edoor_room_type_id
from edoor.channel_managers.utils import get_sync_session_id,add_cm_task,delete_synced_data_log
from edoor.channel_managers.exely.soap_request import send_soap_request
from edoor.channel_managers.exely.rate_limit import get_rate_limit,update_rate_limit_balance
from frappe.utils import now_datetime, add_to_date
from epos_restaurant_2023.custom_socket_client import emit_event
from frappe.rate_limiter import rate_limit
from edoor.api.utils import make_hash
from decimal import Decimal
from frappe import _

    
from lxml import etree

from decimal import Decimal
import time


# flow to sync rate 
# get use occupancy code from cm data log, G1,G2,...
# convert occupancy code from cm data log from row to column then select unique rate value 
# take unique rate value for occupancy code find date that use it 
# after get dates then convert date list to period match with uniquevalue
# build uiqnue value with period to XML to send to chanel manager
# channel manager sync by property code and sync by rate type (rate plan)

# synch limitaion, this limitation include rate, restriction, discount, serverice
# 1 second limit max 1460 value change 
# 3 minute limit max 4380 value change
# 1 hour limit max 13140 value change
# 1 day limit max 43800 value change

# constant variable


REQUEST_TYPE = "Prices update"

@frappe.whitelist()
def testme():
    emit_event("ChannelManagerStartStopSync", True)

    time.sleep(3)
    emit_event("ChannelManagerStartStopSync",False)

@frappe.whitelist()
def sync_room_rate(property=None,retry_sync=True):
     

    if not property:
        properties = frappe.db.sql("select name from `tabBusiness Branch`",as_dict=1)
    else:
        properties = [{"name":property}]
    change_data =[]
    room_type_limit=None
    error_code = None
    for p in properties:
        
        if not can_sync_data(property = p.get("name"), title ='Prices update',provider="Exely"):
            frappe.throw("Data sync to Exely is temporarily blocked. Please check the sync status.")

        # reset session id on pending 
        frappe.db.sql("update `tabChannel Manager Sync Data Log` set sync_session_id = '' where request_type=%(request_type)s and  sync_session_id <> '' and property=%(property)s" ,{"request_type":REQUEST_TYPE,"property":p.get("name")})


        rate_types = frappe.db.sql("select distinct room_type,rate_type from `tabChannel Manager Sync Data Log` where property = %(property)s and provider='Exely' and request_type=%(request_type)s",{"request_type":REQUEST_TYPE,"property":p.get("name")},as_dict = 1)
        
        if len(rate_types)>0:
            
            for rp in set([d.get("rate_type") for d in rate_types]):
                room_types = [d.get("room_type") for d in rate_types if d.get("rate_type") == rp]

                # get room type limit and update session id to data to sync record
                # this is very important to avoid rate limit to CM
                room_type_limit =  get_rate_limit(property =  p.get("name"),room_types = room_types)
                
                session_id = get_sync_session_id(room_type_limit = room_type_limit,rate_type=rp,request_type=REQUEST_TYPE)

    
                group_data = get_group_room_rate_data(session_id,rp)   
               
                
      

                if group_data:
                     
                    soap_body = build_room_rate_xml(property = p.get("name"), group_data=group_data,rate_type = rp)
                    
                    
                    response =  send_soap_request(p.get("name"),"OTA_HotelRateAmountNotifRQ",soap_body)
                  
                   

                    # check response status and add sync log
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
                        delete_synced_data_log(session_id=session_id,provider="Exely",request_type = REQUEST_TYPE,run_commit=False)



                        emit_event("ChannelManagerUpdate",{
                            "action":"update_sync_rate_plan_status",
                            "property":p.get("name"),"status":"Success","title":"Sync Room Rate","message":"Room rates have been successfully synced to the channel manager."
                        })

                    else:
                        
                        emit_event("ChannelManagerUpdate",{
                            "action":"update_sync_rate_plan_status",
                            "property":p.get("name"),
                            "status":response.get("status"),
                            "title":"Sync Room Rate Fail",
                            "message": response.get("response_text"),
                            "docname": sync_log_doc.name

                        })
                        # send socket to socket server

    
    frappe.db.commit()
    if retry_sync and not error_code:
        resync_pending_room_rate_data(property)


    return (change_data,room_type_limit)

def resync_pending_room_rate_data(property=None):
    if not property:
         properties = frappe.db.sql("select name from `tabBusiness Branch`",as_dict=1)
    else:
        properties = [{"name":property}]
    for p in properties:
        sql ="""select 
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
                    "edoor.channel_managers.exely.price_manager.sync_room_rate",
                    queue="short" if frappe.conf.get("developer_mode") else "channel_manager",
                    property=property ,
                    retry_sync = True
                )


      


 

def get_group_room_rate_data(session_id,rate_type):
    occupancy_codes = get_use_occupancy_codes({
        "session_id":session_id,
        "rate_type":rate_type
    })


    if occupancy_codes:
        unique_data =  get_unique_room_rate_values_by_occupancy_codes(session_id=session_id,occupancy_codes=occupancy_codes,rate_type=rate_type)
        occupancy_codes_by_room_type = []
        
        for d in unique_data:
            d["period"] =  get_period(session_id = session_id, data = d,rate_type =  rate_type)
          
            # clean up occupancy code that dont have in sync log by room type
            occupancy_codes_by_room_type = get_occupancy_codes_by_room_type(session_id=session_id, rate_type=rate_type,start_date= d["period"][0].get("start_date"),end_date =  d["period"][0].get("end_date"))
           
            
            for key in list(d.keys()):
                
                
                if key in ["room_type","period"]:
                    continue  # skip room_type
                if not ( 
                        key in  
                            [
                                    x.get("occupancy_code") for x in 
                                    occupancy_codes_by_room_type 
                                    if x.get("room_type") == d.get("room_type")
                        ]):
                    d.pop(key)  


        return unique_data
    return None

def get_occupancy_codes_by_room_type(session_id,rate_type,start_date, end_date):
    sql = """
        select distinct room_type,occupancy_code
        from `tabChannel Manager Sync Data Log`
        where
            date between %(start_date)s and %(end_date)s and
            rate_type = %(rate_type)s and sync_session_id = %(session_id)s
        
    """
    return frappe.db.sql(sql,{"session_id":session_id,"rate_type":rate_type,"start_date":start_date,"end_date":end_date},as_dict = 1)





def get_period(session_id,data,rate_type):
    # data= {"room_type":"RT001","G1":10,"G2":25,...}
    occupancy_fields =  [k for k in data.keys() if k != "room_type"]
    occupancy_sql =",".join( [
            "max(CASE WHEN a.occupancy_code = '{0}' THEN coalesce(value,0) ELSE 0 END)  AS {0}".format(d)
        for d in  occupancy_fields])


    
    sql = """
        select  
            date
        FROM (
            select 
                date, 
                {occupancy_sql}
            from 
                `tabChannel Manager Sync Data Log` a 
            where
                a.sync_session_id = %(session_id)s and 
                a.room_type = %(room_type)s and 
                a.provider = 'Exely' AND 
                a.request_type = %(request_type)s and 
                rate_type = %(rate_type)s and
                a.date>=CURDATE()
            group by 
                date
        ) as data
        WHERE
            {occupancy_filter} 
        order by 
            date

    """.format(
        occupancy_sql = occupancy_sql,
        occupancy_fields = ",".join(occupancy_fields),
        occupancy_filter = " and ".join( [ "{0}=%({0})s".format(x) for x in  occupancy_fields])
        )
     
    
    data = frappe.db.sql(sql, {**data, "rate_type": rate_type,"session_id":session_id,"request_type":REQUEST_TYPE},as_dict=1)

    return group_date_ranges(data)
  


def get_unique_room_rate_values_by_occupancy_codes(session_id,occupancy_codes,rate_type):
    # prepare dynamic sql 

    occupancy_sql =",".join( [
             "max(CASE WHEN a.occupancy_code = '{0}' THEN coalesce(value,0) ELSE 0 END)  AS {0}".format(d.get("occupancy_code"))
         for d in  occupancy_codes])

    sql = """
        select 
            distinct 
            room_type,
            {occupancy_field}
        FROM (
            select 
                room_type, 
                {occupancy_sql}
            from 
                `tabChannel Manager Sync Data Log` a 
            where
                a.sync_session_id = %(session_id)s and 
                a.provider = 'Exely' AND 
                a.request_type = %(request_type)s and 
                a.rate_type = %(rate_type)s and 
                a.date >=CURDATE()
            group by 
                date, 
                room_type
        ) as data
    """.format(
        occupancy_sql = occupancy_sql,
        occupancy_field = ",".join([d.get("occupancy_code") for d in occupancy_codes])
    )
    
    return frappe.db.sql(sql,{"session_id":session_id,"rate_type":rate_type,"request_type":REQUEST_TYPE},as_dict=1)



def get_use_occupancy_codes(filters):
    # filters = {"session_id":"", "rate_type"}
    sql = """
        select 
            distinct 
            a.occupancy_code,
            b.min_age,
            b.max_age
        from `tabChannel Manager Sync Data Log` a 
        join `tabOccupancy Code`  b on b.name = a.occupancy_code
        where
            a.provider= 'Exely' and
            a.request_type = %(request_type)s  and 
            a.sync_session_id = %(session_id)s and 
            a.rate_type = %(rate_type)s
    """
    filters["request_type"] = REQUEST_TYPE
    return frappe.db.sql(sql, filters,as_dict = 1)


def build_room_rate_xml(property,group_data,rate_type):
     
    cm_info = get_channal_manager_info(property)
    rate_plan_code = [d for d in cm_info.get("rate_plans") if d.get("edoor_rate_plan") == rate_type]
    if len(rate_plan_code) == 0:
        frappe.throw("Sync room rate to exely channel manager fail. No rate plan code mapping for rate type " + rate_type)
    rate_plan_code = rate_plan_code[0].get("rate_plan_code")

    root = etree.Element(
        "OTA_HotelRateAmountNotifRQ",
        xmlns="http://www.opentravel.org/OTA/2003/05",
        Version="1.17"
    )


    RateAmountMessages = etree.SubElement(root, "RateAmountMessages", HotelCode=cm_info.get("property_code"))
    
    for rt in set([d.get("room_type") for d in group_data]):
        cm_room_type = get_exely_room_type_code(rt)
        
        RateAmountMessage = etree.SubElement(RateAmountMessages, "RateAmountMessage")
        # status control set room type code and rate plan code
        StatusApplicationControl = etree.SubElement(
                                    RateAmountMessage, 
                                    "StatusApplicationControl",
                                    InvTypeCode=cm_room_type,
                                    RatePlanCode=rate_plan_code)
        # Rates
        Rates = etree.SubElement(
            RateAmountMessage, 
            "Rates",
        )

        rate_data = [d for d in group_data if d.get("room_type") == rt]
        # Rate by period
        for rate in rate_data:
            
            for pr in rate.get("period"):
                Rate = etree.SubElement(
                    Rates, 
                    "Rate",
                    Start = str(pr.get("start_date")),
                    End = str(pr.get("end_date")) 
                )
                # add rate to Rate
                get_BaseByGuestAmts_xml(Rate,rate)

 
    return etree.tostring(root, pretty_print=True).decode()

def get_BaseByGuestAmts_xml( node, rate_data):
    occupancy_codes = get_occupancy_codes()
    # Main Guest
    main_adult = [d for d in occupancy_codes if d.get("occupancy_type") =="AdultBed"]
    main_adult = {item["name"]: item for item in main_adult}
    main_child = [d for d in occupancy_codes if d.get("occupancy_type") =="ChildBandBed"]
    main_child = {item["name"]: item for item in main_child}
    # Extra Bed 
    # adult 
    extra_bed_adult = [d for d in occupancy_codes if d.get("occupancy_type") =="AdultExtraBed"]
    extra_bed_adult = {item["name"]: item for item in extra_bed_adult}
    # exttra bed child 
    extra_bed_child = [d for d in occupancy_codes if d.get("occupancy_type") =="ChildBandExtraBed"]
    extra_bed_child = {item["name"]: item for item in extra_bed_child}

    # exttra bed child 
    child_without_bed = [d for d in occupancy_codes if d.get("occupancy_type") =="ChildBandWithoutBed"]
    child_without_bed = {item["name"]: item for item in child_without_bed}
    
    BaseByGuestAmts =   etree.SubElement(
                    node, 
                    "BaseByGuestAmts",       
                )

    # set node extra bed 
    AdditionalGuestAmounts = None
 

    

    
    if  any( 
            x in list(rate_data.keys()) 
            for x in 
            [d.get("name") for d in occupancy_codes if d.get("occupancy_type") in ["AdultExtraBed","ChildBandExtraBed","ChildBandWithoutBed"]]
        ):
         
            AdditionalGuestAmounts =   etree.SubElement(
                    node, 
                    "AdditionalGuestAmounts",       
                )


    for key, value in rate_data.items():
        if key in main_adult:
            BaseByGuestAmt =   etree.SubElement(
                    BaseByGuestAmts, 
                    "BaseByGuestAmt",    
                    AmountAfterTax=str(normalize_amount(value) or 0),
                    NumberOfGuests= str( main_adult.get(key).get("occupancy")  )
                )
        if key in main_child:
            BaseByGuestAmt =   etree.SubElement(
                    BaseByGuestAmts, 
                    "BaseByGuestAmt",    
                    AmountAfterTax=str(normalize_amount(value) or 0),
                    MinAge= str( main_child.get(key).get("min_age")  ),
                    MaxAge= str( main_child.get(key).get("max_age")  )
                )
        # Extra guest adult
        if key in extra_bed_adult:
            AdditionalGuestAmount =  etree.SubElement(
                    AdditionalGuestAmounts, 
                    "AdditionalGuestAmount",    
                    AmountAfterTax=str(normalize_amount(value) or 0)
            )
        
        # Extra bed child
        if key in extra_bed_child:
            AdditionalGuestAmount =  etree.SubElement(
                    AdditionalGuestAmounts, 
                    "AdditionalGuestAmount",    
                    AmountAfterTax=str(normalize_amount(value) or 0),
                    MinAge= str( extra_bed_child.get(key).get("min_age")  ),
                    MaxAge= str( extra_bed_child.get(key).get("max_age")  )
            )

        # additional child without bed
        # BedRequired
        if key in child_without_bed:
            AdditionalGuestAmount =  etree.SubElement(
                    AdditionalGuestAmounts, 
                    "AdditionalGuestAmount",    
                    AmountAfterTax=str(normalize_amount(value) or 0),
                    MinAge= str( child_without_bed.get(key).get("min_age")  ),
                    MaxAge= str( child_without_bed.get(key).get("max_age")  ),
                    BedRequired = "0"
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
    
# in production mode we should enable rate limit to prevent user click multiple request
@rate_limit(limit=10, seconds=60)
def get_room_rate_from_channel_manager( property , cm_hotel_code,add_cm_sync_log_when_no_data = True,notify_user=False):
    


    # from edoor.channel_managers.exely.dummy_data import room_rate_data
    # room_rate_data =  get_room_rate_group_data_from_cm(room_rate_data)
    # return bulk_update_room_rate (property = property, room_rate_data = room_rate_data)

    # validate if can sync data or not 
    if not can_sync_data( request_type =  "Prices update", property = property, provider="Exely"):
        frappe.throw("The room rate sync from the channel manager has been blocked. Please check the sync status.") 

    # emit channel manager loading notification
    emit_event("ChannelManagerUpdate",{
        "action":"update_cm_notification_status",
        "property":property,
        "status":True
    })
    
    root = etree.Element(
        "OTA_HotelRatePlanRQ",
        xmlns="http://www.opentravel.org/OTA/2003/05",
        Version="1.17"
    )
    RatePlans = etree.SubElement(root, "RatePlans")
    RatePlan = etree.SubElement(RatePlans, "RatePlan")
    etree.SubElement(RatePlan, "HotelRef" ,HotelCode = cm_hotel_code)
    
    soap_body = etree.tostring(root, pretty_print=True).decode()
    
    response =  send_soap_request(property,"OTA_HotelRatePlanRQ",soap_body)

    # prepare data for cm sync log doc
    cm_sync_doc = {
            "property": property,
            "doctype":"Channel Manager Sync Log",
            "provider":"Exely",
            "request_type":REQUEST_TYPE,
            "status" : response.get("status"),
            # "data": frappe.as_json(group_data),
            "response_text": response.get("response_text")
    }
    
    if response.get("status") == "Success":
        # save rate to table Room Rate
        OTA_HotelRatePlanRS= response.get("data").get("s:Envelope").get("s:Body").get("OTA_HotelRatePlanRS")

        # no room rate data 
        if not OTA_HotelRatePlanRS.get("RatePlans"):
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
                    "title":"Sync Room Rate",
                    "message":"Sync room rate from channel manager successfully"
                })
                
            return "Complete, No more rate to sync"


        room_rate_data =  get_room_rate_group_data_from_cm(OTA_HotelRatePlanRS)

        # update rate data to cm sync log doc
       
        cm_sync_doc["data"] = frappe.as_json(get_cm_convert_room_rate_data_rate_by_occupancy_code(room_rate_data))
       
        # update rate type to cm sync data log get rate type from first record of room_rate_data
        cm_sync_doc["rate_type"] = get_edoor_rate_type(room_rate_data[0].get("cm_rate_plan_code"))



       
        price_update_result =  bulk_update_room_rate(property = property, room_rate_data = room_rate_data)
       
        # check price update result if have warning then log to do and cm sync log

        # notif back to cm that we update success 
        if not price_update_result.get("warnings"):
            RateAmountMessageId = response.get("data").get("s:Envelope").get("s:Body").get("OTA_HotelRatePlanRS").get("RatePlans").get("RatePlan").get("RateAmountMessageId")
            
            confirm_request_response =  send_notify_sync_room_rate_request(property = property, hotel_code = cm_hotel_code, message_id =  RateAmountMessageId)
           
            
        else:
            # append warning text to reponse text in cm sync data log
            # change sync status to warning
            cm_sync_doc["status"] = "Warning"
            warning_message = "\n".join(price_update_result.get("warnings"))
            cm_sync_doc["response_text"] =  cm_sync_doc["response_text"] +"\n"+ warning_message

            # add to do stop sync prices update
            cm_sync_doc["sync_action"] = "Stop Sync"
            

        


    # save data to cm sync log
    sync_log_doc = frappe.get_doc(cm_sync_doc).insert(ignore_permissions=True)

    if (cm_sync_doc.get("sync_action") or "") == "Stop Sync":
        task_doc = {
            "property":property,
            "subject": "Sync {0} has been stoped.".format(cm_sync_doc.get("request_type")),
            "description": (cm_sync_doc.get("response_text") or "").strip() ,
            "reference_type": "Channel Manager Sync Log",
            "reference_name": sync_log_doc.name,
            "priority":"High",
        }

        add_cm_task(task_doc,run_commit=False)

    frappe.db.commit()
 

    # emit socket event  to notify client


    # check cm_sync_doc if status success start send sync request until all room rate are
    # fetch from cm 

    if (cm_sync_doc.get("sync_action") or "") != "Stop Sync":
        time.sleep(10)
        frappe.enqueue(
            "edoor.channel_managers.exely.price_manager.get_room_rate_from_channel_manager",
            queue="long" if frappe.conf.get("developer_mode") else "channel_manager",
                property=property,
                cm_hotel_code = cm_hotel_code,
                add_cm_sync_log_when_no_data = False,
                notify_user = notify_user
        )
    



    



    return "Complete"


def send_notify_sync_room_rate_request(property,hotel_code,message_id):
    root = etree.Element(
        "OTA_NotifReportRQ",
        xmlns="http://www.opentravel.org/OTA/2003/05",
        Version="1.17"
    )
    Success = etree.SubElement(root, "Success")
    NotifDetails = etree.SubElement(root, "NotifDetails",HotelCode=hotel_code)
    HotelNotifReport = etree.SubElement(NotifDetails, "HotelNotifReport")
    RatePlanMessages = etree.SubElement(HotelNotifReport, "RatePlanMessages")
    RatePlanMessage = etree.SubElement(RatePlanMessages, "RatePlanMessage",RateAmountMessageId=str(message_id))
    etree.SubElement(RatePlanMessage, "Success")

    soap_body = etree.tostring(root, pretty_print=True).decode()
    response =  send_soap_request(property = property,ota_request = "OTA_NotifReportRQ",body_content =  soap_body,emit_socket_event = False)
    return response


    


def get_room_rate_group_data_from_cm(data):
    result = []
    # get rate plan  if dict convert to array dict
    def get_rate_plans(data):
        if isinstance(data.get("RatePlans").get("RatePlan"), dict):
            return [data.get("RatePlans").get("RatePlan")]
            
        return data.get("RatePlans").get("RatePlan")

    # get rate if dict convert to array dict
    def get_rates(data):
        if isinstance(data.get("Rates").get("Rate"), dict):
            return [data.get("Rates").get("Rate")]
        return data.get("Rates").get("Rate")
    
    # get BaseByGuestAmt if dict convert to array dict
    def get_base_guest_amount(data):
        if isinstance(data.get("BaseByGuestAmts").get("BaseByGuestAmt"), dict):
            return [data.get("BaseByGuestAmts").get("BaseByGuestAmt")]
        return data.get("BaseByGuestAmts").get("BaseByGuestAmt")
    

    # get AdditionalGuestAmounts if dict convert to array dict
    def get_additional_guest_amount(data):
        if isinstance(data.get("AdditionalGuestAmounts",{}).get("AdditionalGuestAmount"), dict):
            return [data.get("AdditionalGuestAmounts",{}).get("AdditionalGuestAmount")]
        return data.get("AdditionalGuestAmounts",{}).get("AdditionalGuestAmount") or []

 

    for rp in get_rate_plans(data):
        # return get_rates(rp)
        for rate in get_rates(rp):
            _row = {
                "cm_rate_plan_code": rp.get("@RatePlanCode"),
                "start_date": rate.get("@Start"),
                "end_date": rate.get("@End"),
                "cm_room_type_code": rate.get("@InvTypeCode"),
                "rates":[]
            }
            # get base rate adult and child
            for base_rate in  get_base_guest_amount(rate):
                _occupancy_type =  "ChildBandBed" if base_rate.get("@MinAge") and base_rate.get("@MaxAge") else "AdultBed" 
                _base_rate_row = {
                    "occupancy_type":_occupancy_type,
                    "occupancy":base_rate.get("@NumberOfGuests"),
                    "min_age": base_rate.get("@MinAge"),
                    "max_age": base_rate.get("@MaxAge"),
                    "rate": base_rate.get("@AmountAfterTax")
                }
                _row["rates"].append(_base_rate_row)
            
            # get base rate adult and child
            # return get_additional_guest_amount(rate)
            for additional_rate in  get_additional_guest_amount(rate):

                _occupancy_type =  "AdultExtraBed"
                if additional_rate.get("@MinAge") and additional_rate.get("@MaxAge"):
                    if "@BedRequired" in additional_rate:
                        _occupancy_type = "ChildBandWithoutBed"
                    else:
                        _occupancy_type = "ChildBandExtraBed"

                

                _additional_rate_row = {
                    "occupancy_type":_occupancy_type,
                    "occupancy":additional_rate.get("@NumberOfGuests"),
                    "min_age": additional_rate.get("@MinAge"),
                    "max_age": additional_rate.get("@MaxAge"),
                    "rate": additional_rate.get("@AmountAfterTax")
                }

                _row["rates"].append(_additional_rate_row)
            
            result.append(_row)


    return result

def bulk_update_room_rate(property , room_rate_data):
    # return room_rate_data
    room_type_occupancy_code_mapping = get_occupancy_code_mapping()
    values = []
    warnings = set()
    for rr in room_rate_data:
        rate_type = get_edoor_rate_type(rr.get("cm_rate_plan_code"))
        # check if rate plan not valid stop sync add to do log and notify to user and stop sync imediately
        if not rate_type:
            warnings.add(_("No edoor rate plan mapping for exely rate plan code {0}. Please check in channel manager integration".format(rr.get("cm_rate_plan_code"))))
            break


        room_type_id = get_edoor_room_type_id(rr.get("cm_room_type_code"))
        room_type_name = frappe.get_cached_value("Room Type", room_type_id,"room_type")
        dates = get_date_range(rr.get("start_date"), rr.get("end_date"))

        # get specific occupancy code by room type
        occupancy_code_mapping = next((x for x in room_type_occupancy_code_mapping if x.get("room_type") == room_type_id), None)
        occupancy_code_mapping = (occupancy_code_mapping or {}).get("occupancy_codes")


        for dt in dates:
            for _rate in rr.get("rates"):

                occupancy_key = (
                    f"{_rate.get('occupancy_type')}_"
                    f"{_rate.get('occupancy') or 1}_"
                    f"{_rate.get('min_age') or 0}_"
                    f"{_rate.get('max_age') or 0}"
                )

                occupancy_code = occupancy_code_mapping.get(occupancy_key) or ""
                if not occupancy_code:
                    if _rate.get("min_age") and _rate.get("max_age"):
                        warnings.add(f"No occpancy code mapping for Room Type: {room_type_name}, Bed Type: {_rate.get('occupancy_type')}, Min Age: {_rate.get('min_age') }, Max Age: {_rate.get('max_age') }")
                    else:
                        warnings.add(f"No occpancy code mapping for Room Type: {room_type_name}, Bed Type: {_rate.get('occupancy_type')}, Occupancy: {_rate.get('occupancy') }")
                    
                 

                room_rate = Decimal(_rate.get("rate") or 0)

                has_text = f"p_{room_type_id}_{rate_type}_{occupancy_code}_{dt}"
                row_name = make_hash(has_text)

                _value = (
                    f"('{row_name}', '{property}', '{rate_type}', "
                    f"'{room_type_id}', '{occupancy_code}', "
                    f"'{dt}', {room_rate})"
                )

                values.append(_value)

    if values and not warnings:
 
       
        value_str = ", ".join(values)
        
        sql = f"""
            INSERT INTO `tabRoom Rates`
            (name, property, rate_type,room_type_id,  occupancy_code,date, rate)
            VALUES {value_str}
            ON DUPLICATE KEY UPDATE
            rate = VALUES(rate)
        """

 

        frappe.db.sql(sql)

        frappe.db.commit()


 
    return {
        "room_rate_value_count":len(values),
        "warnings":list(warnings)
    }

def get_cm_convert_room_rate_data_rate_by_occupancy_code(data):
    occupancy_codes_mapping ={item["room_type"]: item["occupancy_codes"] for item in  get_occupancy_code_mapping()} 
  
    room_rates = []
    def get_occopancy_key(occupancy_codes,_data):

        _occupancy_key = f"{_data.get('occupancy_type')}_{_data.get('occupancy') or 1}_{_data.get('min_age') or 0}_{_data.get('max_age') or 0}"
        
        return occupancy_codes.get(_occupancy_key)


    for d in data:
        room_type_id = get_edoor_room_type_id(d.get("cm_room_type_code"))
        _room_rate = {
            "room_type": room_type_id,
            "period":[{
                "start_date":d.get("start_date"),
                "end_date":d.get("end_date")
            }]
        }
        for r in d.get("rates"):
            _room_rate[get_occopancy_key(occupancy_codes_mapping.get(room_type_id),r)] = r.get("rate") or 0
        room_rates.append(_room_rate)

    return room_rates
            

        