import frappe
import json
from frappe.utils import getdate, add_days,get_datetime,now_datetime,today
from itertools import groupby

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
def get_sync_action_status(title,property,provider=None):
    titles = []
    if isinstance(title, str):
        titles = [title]
    else:
        titles = title

    cm_info = get_channal_manager_info(property)
    if not cm_info:
        return None

    if not provider:
        provider = cm_info.provider
        
    sql="select is_retry_sync, name, sync_action,title, sync_until,response_text,property,provider,creation from `tabChannel Manager Sync Log` where title in %(titles)s and provider=%(provider)s and property = %(property)s order by creation desc limit 1"

    data = frappe.db.sql(sql,{"titles":titles,"property":property,"provider":provider},as_dict = 1)
     
    data = [d for d in data if d.get("is_retry_sync") ==0]
    if data:
        data = data[0]
        if data.get("sync_action") == "Delay Sync":
            sync_until = get_datetime(data.get("sync_until") )
            if now_datetime()<sync_until:
                return data
        else:
            return data


    return None
   
    

@frappe.whitelist()
def can_sync_data(title,property,provider):
    sql="select  sync_action, sync_until from `tabChannel Manager Sync Log` where title = %(title)s and provider=%(provider)s and property = %(property)s and is_retry_sync = 0 order by creation desc limit 1"

    data = frappe.db.sql(sql,{"title":title,"property":property,"provider":provider},as_dict = 1)
    
    if not data:
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
    return_data = {
        "title":doc.title,
        "provider":doc.provider,
        "property":doc.property,
        "status":doc.status,
        "response_text":doc.response_text,
        "sync_action":doc.sync_action,
        "sync_until":doc.sync_until,
        "creation":doc.creation,
        "is_retry_sync":doc.is_retry_sync
    }
    def get_price_data():
        data =  json.loads(doc.data)
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

    if doc.title == "Prices update":
        return_data["data"] = get_price_data()
    if doc.title == "Restriction update":
        return_data["data"] = get_restriction_data()

    
    
    return return_data

@frappe.whitelist()  
def get_all_cm_sync_status(property):
    methods =["Get Reservation","Prices update","Restriction update","Availabilty update"]
    data = []
    for m in methods:
        _data = {
            "title":m
        }
        sql = "select name,sync_action,provider, sync_until, is_retry_sync, response_text,status,creation  from `tabChannel Manager Sync Log` where property=%(property)s and title = %(title)s order by creation desc limit 1 "
        log = frappe.db.sql(sql,{"property":property,"title":m},as_dict = 1)
        if log:
            log = log[0]
            _data = {**_data,**log}
        data.append(_data)

    return data

@frappe.whitelist()
def get_pending_sync_data(property):
    rate_types = frappe.db.sql("select distinct rate_type from `tabChannel Manager Sync Data Log` where property=%(property)s",{"property":property}, as_dict = 1)
    room_rates = []
    restrictions = []
    
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

    return {"room_rates": room_rates,"restrictions":restrictions}

    
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
                a.request_type = 'OTA_HotelRateAmountNotifRQ'  and 
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
                a.request_type = 'OTA_HotelRateAmountNotifRQ' and 
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
                a.request_type = 'OTA_HotelRateAmountNotifRQ' and 
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
            request_type = 'OTA_HotelAvailNotifRQ'
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