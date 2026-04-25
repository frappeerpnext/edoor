import frappe
import json
from frappe.utils import getdate, add_days,get_datetime,now_datetime

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

    if doc.title == "Prices update":
        return_data["data"] = get_price_data()
    
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