import frappe
import json
from frappe.utils import getdate, add_days,get_datetime,now_datetime,today,nowdate, add_years
 

from itertools import groupby
from frappe.utils.caching import redis_cache


@frappe.whitelist()
def clear_cache():
    get_sync_max_date.clear_cache()
    get_cm_provider_list.clear_cache()
    get_occupancy_code_mapping.clear_cache()

 

@redis_cache(ttl=60*60)
def get_cm_provider_list():
    sql="select property,property_code,provider,prices_for_accommodation,initialized_prices_upload from `tabChannel Manager Integration` where enable=1"
    return frappe.db.sql(sql,as_dict = 1)



@frappe.whitelist()
def get_channal_manager_info(property):
    cached_key = f"{property}_channel_manager_info"
    if cached_value := frappe.cache.get_value(cached_key):
        
        return cached_value

    data = {
        "enable": False
    }
    if frappe.db.exists("Channel Manager Integration",property):
        data = frappe.get_cached_doc("Channel Manager Integration",property)
    
    frappe.cache.set_value(cached_key, data)
    
    return data



def get_sync_session_id(room_type_limit=0,rate_type="",request_type=None,order_by ='date'):
    # this method is very important
    # we use this method to apply sync session id to channel manager sync log table 
    # when get data to sync to cm we use this session id to get data from sync log 
    # and delete it by session  by session id after sync success 

    # if sync faild session id will be clear from queue job retry sync cm data in queue job
    # we check if last modified date over 60 second


    import uuid
    session_id = str(uuid.uuid4())
    max_date =  get_sync_max_date()
  

    for room_type, limit in room_type_limit.items():

        rows = frappe.db.sql("""
            SELECT name
            FROM `tabChannel Manager Sync Data Log`
            WHERE 
                coalesce(sync_session_id,'') = ''  AND 
                room_type = %(room_type)s  and 
                (%(rate_type)s = '' or rate_type = %(rate_type)s) and 
                request_type = %(request_type)s and 
                date<= %(max_date)s
            ORDER BY {order_by}
            LIMIT %(limit)s
            FOR UPDATE SKIP LOCKED
        """.format(order_by=order_by)
        , {"room_type":room_type,"limit":limit,"rate_type":rate_type,"request_type":request_type,"max_date":max_date}, as_dict=True)

        if len(rows) ==0:
            continue
        keys = [r.get("name") for r in rows]
        frappe.db.sql("""
            UPDATE `tabChannel Manager Sync Data Log`
            SET sync_session_id = %(session_id)s,modified = NOW()
            WHERE name IN %(names)s
        """, {"session_id":session_id, "names":tuple(keys)})

    frappe.db.commit()

    return session_id
    

def group_date_ranges(dates_data):
    if not dates_data:
        return []

    # Convert and sort dates
    dates = sorted(getdate(d["date"]) for d in dates_data)

    ranges = []

    start = dates[0]
    prev = dates[0]

    for d in dates[1:]:
        if d == add_days(prev, 1):
            prev = d
        else:
            ranges.append({
                "start_date": start,
                "end_date": prev
            })
            start = d
            prev = d

    # Add last range
    ranges.append({
        "start_date": start,
        "end_date": prev
    })

    return ranges

 
def get_occupancy_codes():
    cached_key = "occupancy_codes"
    if cached_value := frappe.cache.get_value(cached_key):
        
        return cached_value


    sql = """
        select 
            name,
            is_base_guest,
            is_child,
            min_age,
            max_age,
            occupancy,
            require_bed,
            occupancy_type
        from `tabOccupancy Code`

    """

    data = frappe.db.sql(sql,as_dict = 1)
    frappe.cache.set_value(cached_key, data)
    return data

@frappe.whitelist(methods="POST")
def get_sync_action_status(request_type,property,provider=None):
    def get_last_status(_request_type):
        sql = "select status from `tabChannel Manager Sync Log` where request_type = %(request_type)s order by creation desc limit 1"
        data = frappe.db.sql(sql,{"request_type":_request_type},as_dict = 1)
        
        if data:
            return data[0].get("status") or "dummy"
        return "dummy"

    request_types = []
    
    if isinstance(request_type, str):
        if get_last_status(request_type) != "Success":
            request_types = [request_type]
    else:
        for rt in request_type:
            if get_last_status(rt) !="Success":
                request_types.append(rt)
            else:
                request_types.append("dummy")
     

    cm_info = get_channal_manager_info(property)
    if not cm_info:
        return None

    if not provider:
        provider = cm_info.provider
        
    sql="select is_retry_sync, name, sync_action,request_type, sync_until,response_text,property,provider,creation from `tabChannel Manager Sync Log` where request_type in %(request_types)s and provider=%(provider)s and property = %(property)s and status <> 'Success' and is_retry_sync = 0 order by creation desc limit 1"

    data = frappe.db.sql(sql,{"request_types":request_types,"property":property,"provider":provider},as_dict = 1)
 

    data = [d for d in data if d.get("is_retry_sync") ==0]
    if data:
        
        data = data[0]
        if data.get("sync_action") == "Delay Sync":
            sync_until = get_datetime(data.get("sync_until") )
            if now_datetime()<sync_until:
                return data
        else:
            return data


    return {"status":"Success"}
   
    

@frappe.whitelist()
def can_sync_data(title=None,property=None,provider=None,request_type=None):
    request_type = title or request_type

    sql="select  sync_action, sync_until,is_retry_sync from `tabChannel Manager Sync Log` where request_type = %(request_type)s and provider=%(provider)s and property = %(property)s  order by creation desc limit 1"

    data = frappe.db.sql(sql,{"request_type":request_type,"property":property,"provider":provider},as_dict = 1)
    
    
    if not data:
        return True
    else:
        if data[0].get("is_retry_sync") == 1:
            return True
    
    data = data[0]
    if data.get("sync_action") =="Stop Sync":
        return False

    if data.get("sync_action") =="Delay Sync":
        if get_datetime(now_datetime())>=get_datetime(data.get("sync_until")):
            return True
        else:
            return False
    return True


def can_save_data(title,property,provider):
    sql="select sync_action, sync_until,is_retry_sync from `tabChannel Manager Sync Log` where title = %(title)s and provider=%(provider)s and property = %(property)s order by creation desc limit 1"

    data = frappe.db.sql(sql,{"title":title,"property":property,"provider":provider},as_dict = 1)
    
    data = [d for d in data if d.get("is_retry_sync") == 0]
    
    if not data:
        return True
        
    data = data[0]
    if data.get("sync_action") =="Stop Sync":
        return False
    
    return True


@frappe.whitelist()
def get_cm_sync_log_data(docname):
    doc = frappe.get_cached_doc("Channel Manager Sync Log",docname)
    raw_data = json.loads(doc.data or "{}") if doc else {}
    return_data = {
        "title":doc.title,
        "request_type":doc.request_type,
        "provider":doc.provider,
        "property":doc.property,
        "status":doc.status,
        "response_text":doc.response_text,
        "sync_action":doc.sync_action,
        "sync_until":doc.sync_until,
        "creation":doc.creation,
        "is_retry_sync":doc.is_retry_sync,
        "raw_data": raw_data
    }
    def get_price_data():
        data =  json.loads(doc.data or "{}") if doc else {}
        _datas = []
        
        
        if data:
            for x in data:
                _data = {"period":x.get("period")}
                _data["room_type"] = frappe.get_cached_value("Room Type", x.get("room_type"),"room_type" ) 
                rates=[]
                for key in x:
                    
                    if not key in ["period","room_type"]:
                        occupancy_name,sort_order = frappe.get_cached_value("Occupancy Code", key,["title","sort_order"])
                        rate= {
                            "title":occupancy_name,
                            "sort_order": sort_order,
                            "rate": float( x.get(key))
                        }
                        rates.append(rate)
                _data["rates"] =  sorted(rates, key=lambda x: x["sort_order"])

                _datas.append(_data)
               

        return _datas

    def get_restriction_data():
        _restriction_data = json.loads( doc.data)
        restriction_data = []
        for key in _restriction_data:
            for d in _restriction_data[key]:
                restriction_data.append({
                    "restriction_type": key,
                    "room_type":frappe.get_cached_value("Room Type",d.get("room_type"),"room_type"),
                    "start_date":d.get('start'),
                    "end_date":d.get('end'),
                    "value":d.get('value'),
                })
        return restriction_data

    if doc.request_type == "Prices update":
        return_data["data"] = get_price_data()
    if doc.request_type == "Restriction update":
        return_data["data"] = get_restriction_data()

    
    
    return return_data

@frappe.whitelist()  
def get_all_cm_sync_status(property = "ESTC HOTEL 6"):
    methods =["Get Reservation","Prices update","Restriction update","Availabilty update"]
    data = []
    for m in methods:
        _data = {
            "title":m
        }
        sql = "select name,sync_action,provider, sync_until, is_retry_sync, response_text,status,creation  from `tabChannel Manager Sync Log` where property=%(property)s and request_type = %(title)s order by creation desc limit 1 "
        log = frappe.db.sql(sql,{"property":property,"title":m},as_dict = 1)
        if log:
            log = log[0]
            _data = {**_data,**log}
        data.append(_data)

    return data



@frappe.whitelist()
def get_pending_sync_data_status(property):
    max_sync_years = int(frappe.get_cached_value("eDoor Setting",None,"maximum_future_years_allowed") or 1)
    max_date =  add_years(nowdate(), max_sync_years)
    
    sql="select name from `tabChannel Manager Sync Data Log` where property=%(property)s and date<=%(date)s limit 1"
      
    if len(frappe.db.sql(sql,{"property":property, "date": max_date},as_dict = 1))>0:
        return {
            "has_pending_data":1
        }

    return {
            "has_pending_data":0
        }

@frappe.whitelist()
def get_pending_sync_data(property="ESTC HOTEL 6"):
    rate_types = frappe.db.sql("select distinct rate_type from `tabChannel Manager Sync Data Log` where property=%(property)s",{"property":property}, as_dict = 1)

    room_rates = []
    restrictions = []
    availabilities = []
    
    for rt in rate_types:
        room_rate_data = get_pending_group_room_rate_data(rt.get("rate_type"))
        if room_rate_data:
            room_rates.append({
                "rate_type":rt.get("rate_type"),
                "data":room_rate_data
            })
        restriction_data = get_pending_room_restriction(rt.get("rate_type"))
        if restriction_data:
            restrictions.append({
                "rate_type":rt.get("rate_type"),
                "data":restriction_data
            })
    availabilities = get_pending_room_availability(property)
    return {"room_rates": room_rates,"restrictions":restrictions,"availabilities":availabilities}

    
def get_pending_group_room_rate_data(rate_type):
    def get_use_occupancy_codes(rate_type):
        sql = """
            select 
                distinct 
                a.occupancy_code,
                b.min_age,
                b.max_age
            from `tabChannel Manager Sync Data Log` a 
            join `tabOccupancy Code`  b on b.name = a.occupancy_code
            where
                a.request_type = 'Prices update'  and 
                a.rate_type = %(rate_type)s
        """
        return frappe.db.sql(sql, {"rate_type":rate_type},as_dict = 1)


    def get_occupancy_codes_by_room_type(rate_type,start_date, end_date):
        sql = """
            select distinct room_type,occupancy_code
            from `tabChannel Manager Sync Data Log`
            where
                date between %(start_date)s and %(end_date)s and
                rate_type = %(rate_type)s  
            
        """
        return frappe.db.sql(sql,{"rate_type":rate_type,"start_date":start_date,"end_date":end_date},as_dict = 1)

    def get_price_data(data):
        
        _datas = []
        
        
        if data:
            for x in data:
                _data = {"period":x.get("period")}
                _data["room_type"] = frappe.get_cached_value("Room Type", x.get("room_type"),"room_type" ) 
                rates=[]
                for key in x:
                    
                    if not key in ["period","room_type"]:
                        occupancy_name,sort_order = frappe.get_cached_value("Occupancy Code", key,["title","sort_order"])
                        rate= {
                            "title":occupancy_name,
                            "sort_order": sort_order,
                            "rate": float( x.get(key))
                        }
                        rates.append(rate)
                _data["rates"] =  sorted(rates, key=lambda x: x["sort_order"])

                _datas.append(_data)
               

        return _datas

    occupancy_codes = get_use_occupancy_codes(rate_type)

    if occupancy_codes:
        unique_data =  get_unique_room_rate_values_by_occupancy_codes(occupancy_codes=occupancy_codes,rate_type=rate_type)
        occupancy_codes_by_room_type = []
        
        for d in unique_data:
            d["period"] =  get_pending_room_rate_period( data = d,rate_type =  rate_type)
          
            # clean up occupancy code that dont have in sync log by room type
            occupancy_codes_by_room_type = get_occupancy_codes_by_room_type( rate_type=rate_type,start_date= d["period"][0].get("start_date"),end_date =  d["period"][0].get("end_date"))
           
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


        return get_price_data(unique_data)
    return None

def get_unique_room_rate_values_by_occupancy_codes(occupancy_codes,rate_type):
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
                a.request_type = 'Prices update' and 
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
    
    return frappe.db.sql(sql,{"rate_type":rate_type},as_dict=1)


def get_pending_room_rate_period(data,rate_type):
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
                a.room_type = %(room_type)s and 
                a.request_type = 'Prices update' and 
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
     
    
    data = frappe.db.sql(sql, {**data, "rate_type": rate_type},as_dict=1)

    return group_date_ranges(data)

# get pending room availability data
def get_pending_room_availability(property):
    max_date = get_sync_max_date()
  
    sql= """
        select 
            date,
            room_type,
            value
        from `tabChannel Manager Sync Data Log`
        where
            date between CURDATE() and %(max_date)s and
            request_type = 'Availability update' and 
            property = %(property)s
        order by room_type,date
    """
    
    data = frappe.db.sql(sql,{"max_date": max_date, "property":property},as_dict = 1)
   

  
    
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
                    "start_date": start,
                    "end_date": end,
                    "value": value
                })

                start = r["date"]
                end = r["date"]
                value = r["value"]

            last_date = current_date

        results.append({
            "room_type": room_type,
            "start_date": start,
            "end_date": end,
            "value": value
        })
    for rt in results:
        rt["room_type_name"] = frappe.get_cached_value("Room Type",rt.get("room_type"),"room_type")
    return results
 

# get peding room restriction 
def get_pending_room_restriction(rate_type):
    
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



    sql= """
        select 
            date,
            room_type,
            restriction_type,
            value
        from `tabChannel Manager Sync Data Log`
        where
            rate_type = %(rate_type)s  and 
            request_type = 'Restriction update'
        order by date,restriction_type

    """
    data = frappe.db.sql(sql,{ "rate_type":rate_type},as_dict = 1)
    restriction_types = set([d.get("restriction_type") for d in data])

    group_data = {}
    for rt in restriction_types:
        group_data[rt] = get_group_peroid_data([x for x in data if x.get("restriction_type") == rt])
    
    def get_restriction_data(_restriction_data):
        restriction_data = []
        for key in _restriction_data:
            for d in _restriction_data[key]:
                restriction_data.append({
                    "restriction_type": key,
                    "room_type":frappe.get_cached_value("Room Type",d.get("room_type"),"room_type"),
                    "start_date":d.get('start'),
                    "end_date":d.get('end'),
                    "value":d.get('value'),
                })
        return restriction_data

    return get_restriction_data(group_data)

def add_cm_task(data,run_commit=True):
    # find existing cm task by subject and status open and property
    sql = "select name from `tabToDo` where custom_property=%(property)s and custom_subject = %(subject)s and status='Open' order by modified limit 1"
    existing_data = frappe.db.sql(sql,{"property":data.get("property"),"subject":data.get("subject")},as_dict = 1)
    if existing_data:
        doc = frappe.get_doc("ToDo", existing_data[0].get("name"))
        doc.description = doc.description + "\n" + (data.get("description") or data.get("subject"))
        doc.reference_type = data.get("reference_type")
        doc.reference_name = data.get("reference_name")
        doc.save(
            ignore_permissions=True,  
            ignore_version=True  
        )
        
    else:
        doc = {
            "doctype":"ToDo",
            "reference_type":data.get("reference_type"),
            "reference_name":data.get("reference_name"),
            "custom_subject":data.get("subject"),
            "custom_property": data.get("property"),
            "description":data.get("description") or data.get("subject"),
        
            "priority":data.get("priority"),
            "status":"Open",
            "role":"Channel Manager User"
        }

        frappe.get_doc(doc).insert(ignore_permissions = True)
    if run_commit:
        frappe.db.commit()




@redis_cache(ttl=60*60)  
def get_sync_max_date():
    max_sync_years = int(
        frappe.get_cached_value("eDoor Setting", None, "maximum_future_years_allowed") or 1
    )
    return add_years(nowdate(), max_sync_years)

def delete_synced_data_log(session_id,request_type,provider="",cm_response=None,xml_body=None,run_commit = True):
    # import xmltodict
    # return xmltodict.parse(xml_body)
    
    # warnings =  cm_response.get("data",{}).get("s:Envelope",{}).get("s:Body",{}).get("OTA_HotelRateAmountNotifRS",{}).get("Warnings",{}).get("Warning")

    # for w in warnings:
    #     return get_value_from_xml_by_tag(xml_body,w.get("@Tag"))

    sql="""
        delete from `tabChannel Manager Sync Data Log`
        where
            ( 
            sync_session_id  =  %(session_id)s and 
            request_type = %(request_type)s and 
            provider = %(provider)s
            ) or 
            date < CURDATE()
            
    """
    frappe.db.sql(sql, {"session_id":session_id,"request_type":request_type,"provider":provider})
    if run_commit:
        frappe.db.commit()


def add_change_data_log(data,run_commit=True):
    doc = frappe.get_doc({
        "doctype":"Change Data Log",
        "property": data.get("property"),
        "rate_type":data.get("rate_type"),
        "room_type":data.get("room_type") or "",
        "transaction_type":data.get("transaction_type"),
        "restriction_type":data.get("restriction_type"),
        "data":frappe.as_json(data)
    })
    doc.insert(ignore_permissions=True)

    if run_commit:
        frappe.db.commit()

@frappe.whitelist(methods="POST")
def mark_channel_data_upload_as_complete(property):
    doc = frappe.get_doc("Channel Manager Integration",property)
    doc.initialized_data_upload = 1
    doc.save(ignore_permissions=True)
    return "Success"    


 
def get_date_range(start_date, end_date):
    start = getdate(start_date)
    end = getdate(end_date)

    dates = []

    while start <= end:
        dates.append(start.strftime("%Y-%m-%d"))
        start = add_days(start, 1)

    return dates

@frappe.whitelist()
@redis_cache(ttl=60*60)
def get_occupancy_code_mapping():
    sql = "select parent as room_type,occupancy_code from `tabRoom Type Occupancy Rate` "
    room_type_occupancy_codes =  frappe.db.sql(sql,as_dict=1)
    return_data = []
    for rt in set([d.get("room_type") for d in room_type_occupancy_codes]):
        sql = "select concat(occupancy_type,'_',occupancy,'_',min_age,'_',max_age) as `key`, name from `tabOccupancy Code` where name in %(occupancy_codes)s"

        data = frappe.db.sql(sql,{"occupancy_codes":[x.get("occupancy_code") for x in room_type_occupancy_codes if x.get("room_type") == rt]},as_dict = 1)
        
        
        return_data.append({
            "room_type":rt,
            "occupancy_codes": {item['key']: item['name'] for item in data}
        })
    return return_data