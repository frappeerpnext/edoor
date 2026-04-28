import frappe 
from edoor.channel_managers.utils import get_channal_manager_info,can_save_data

from frappe.rate_limiter import rate_limit

from frappe.utils import getdate, add_to_date,today
from edoor.api.utils import make_hash,generate_unique_dates


# constant variable
REQUEST_TYPE = "Prices update"


        
@frappe.whitelist()
def get_rate_plan_info(property,rate_type):
    room_types = get_room_types(property,rate_type)
    rate_type_doc = frappe.get_cached_doc("Rate Type", rate_type)
    room_rates_min_max_date = get_room_rates_min_max_dates(property)
    cm_rate_plan_list = get_cm_rate_plan_list(property)

    maximum_future_years_allowed = int(frappe.get_cached_value("eDoor Setting",None, "maximum_future_years_allowed"))
    current_year = getdate(today()).year
    visible_years = [current_year-1, current_year]
    for n in range(1,maximum_future_years_allowed+1):
        visible_years.append(current_year+n)
    return {
        "room_types":room_types,
        "visible_years": visible_years,
        "occupancy_codes": get_available_occupancy_codes(property),
        "rate_type": rate_type_doc,
        "cm_rate_plan_list": cm_rate_plan_list,
        "room_rates_min_max_date": room_rates_min_max_date,
        "cm_info": get_channal_manager_info(property)
    }


def get_room_rates_min_max_dates(property):
    
    sql = """
        SELECT 
            rate_type,
            MIN(date) AS start_date,
            MAX(date) AS end_date
        FROM `tabRoom Rates`
        WHERE  
            property = %(property)s
        group by rate_type
    """

    data = frappe.db.sql(sql, {
        "property": property 
    }, as_dict=1)

    return data 


def get_available_occupancy_codes(property):
    cached_key = f"{property}_occupancy_codes"
    if cached_value := frappe.cache.get_value(cached_key):
        return cached_value

    sql = """
        select
            distinct
            a.occupancy_code,
            b.title

        from `tabRoom Type Occupancy Rate` a
        join `tabRoom Type` rt on rt.name = a.parent
        join `tabOccupancy Code` b on b.name = a.occupancy_code
        where
            rt.property = %(property)s 
        order by b.sort_order
    """
    data =  frappe.db.sql(sql,{"property":property},as_dict =1)
    frappe.cache.set_value(cached_key, data)
    return data

def get_room_restriction_by_rate_type(property):

    sql = """
        SELECT  
            rate_type,
            GROUP_CONCAT(distinct restriction_type SEPARATOR ', ') AS group_restriction_type,
            MIN(date) AS start_date,
            MAX(date) AS end_date
        FROM `tabRoom Restriction`
        WHERE 
            property = %(property)s
        group by rate_type
    """
    data = frappe.db.sql(sql,{"property":property},as_dict = 1)

    return data 
 
@frappe.whitelist()
def get_rate_type_list(property):
    room_rates_max_min_date = get_room_rates_min_max_dates(property)
    room_restriction = get_room_restriction_by_rate_type(property)
    cm_info = get_channal_manager_info(property) 

    sql = """
        select
            name
        from `tabRate Type`
        where
            property = %(property)s and
            is_complimentary = 0 and
            is_house_use = 0 and 
            disabled = 0
    """

    data = frappe.db.sql(sql, {"property": property}, as_dict=1)

    rate_list = []

    for d in data:
        rate_item = {
            "rate_type_name": d["name"],
            "room_rates_max_min_date": [item for item in room_rates_max_min_date if item["rate_type"] == d["name"]], 
            "room_restriction": next((item for item in room_restriction if item["rate_type"] == d["name"]),{}),
            "status": "Connected" if any(item.edoor_rate_plan == d["name"] for item in cm_info.rate_plans) else "Not Connected"
        }

        rate_list.append(rate_item)
 
    result = {
        "cm_logo": cm_info.get("provider_logo"),
        "prodiver": cm_info.get("provider"),
        "rate_type_list": rate_list
    }

    return result

@frappe.whitelist()
def get_cm_rate_plan_list(property):
    
    cm_info = get_channal_manager_info(property)
    rate_plans = [] 
    
    for r in cm_info.rate_plans:
        rate_plans.append(
            {
                "cm_rate_plan": r.rate_plan_code,
                "edoor_rate_plan": r.edoor_rate_plan,
                "rate_plan_name":r.rate_plan_name,
                "availability_block":r.availability_block,
            }
        )

    # update set rate date 
    # update restiction status to the future

    return rate_plans

@frappe.whitelist(methods="POST")
def get_room_rate_data(filters):
    # filter has key room_types[string], rate_type,start_date,end_date
    sql = """
        SELECT 
            CONCAT(DATE_FORMAT(rr.date,'%%y%%m%%d'), rr.room_type_id, rr.occupancy_code) AS `key`,
            rr.rate
        FROM `tabRoom Rates` rr
        WHERE
            rr.room_type_id IN %(room_types)s
            AND rr.rate_type = %(rate_type)s
            AND rr.date BETWEEN %(start_date)s AND %(end_date)s
    """
    data = frappe.db.sql(sql, filters, as_dict=1)
    # prepare return data
    # sample return data
    # data = {}
    return {item['key']: item['rate'] for item in data}

@frappe.whitelist()
def get_room_types(property,rate_type):
    cm_info = get_channal_manager_info(property)
    rate_type_doc = frappe.get_cached_doc("Rate Type", rate_type)
    rate_type_room_types = [d.get("room_type") for d in rate_type_doc.get("room_types")]
    room_types = []

    occupancy_codes = get_room_type_occopancy_codes()
    for r in [d for d in cm_info.room_types if d.edoor_room_type and d.edoor_room_type in rate_type_room_types]:
        room_type_alias,enable_min_rate,min_rate= frappe.get_cached_value("Room Type", r.edoor_room_type,["alias","enable_min_rate","min_rate"])
        room_types.append(
            {
                "cm_room_type": r.room_type_code,
                "edoor_room_type": r.edoor_room_type,
                "room_type_name":r.room_type_name,
                "room_type_data": r.data,
                "room_type_alias":room_type_alias,
                "enable_min_rate":enable_min_rate,
                "min_rate":min_rate,
                "occupancy_codes":[d for d in occupancy_codes if d.get("room_type_id") == r.get("edoor_room_type")]
            }
        )

    # update set rate date 
    # update restiction status to the future

    return room_types


def get_room_type_occopancy_codes():
    sql = """
        select
            a.parent as room_type_id, 
            a.occupancy_code,
            b.title
        from `tabRoom Type Occupancy Rate` a 
        inner join `tabOccupancy Code` b on b.name = a.occupancy_code
        order by a.idx
    """
    return frappe.db.sql(sql,as_dict=1)



@frappe.whitelist(methods="POST")
@rate_limit(limit=10, seconds=60)
def bulk_update_room_rate(data):
    
    validate_bulk_update_room_rate(data)


    dates = generate_unique_dates(data.get("date_range"))
    values = []
    for dt in dates:
        for rt in data.get("room_types"):
            # only occupancy codes marked for update
            for occ in [x for x in rt.get("occupancy_codes") if x.get("rate") !=None]:
                # generate hash key
                # hash_prefix p_=prices(room rate), a_=availablity, r_=restriction
                has_text = f"p_{occ.get('room_type_id')}_{data.get('rate_type')}_{occ.get('occupancy_code')}_{dt}"
                row_name = make_hash(has_text)
                
                # handle rate_type nullable
                rate_type = data.get("rate_type")
                
                # handle rate nullable
                rate = occ.get("rate") or 0

                # append as SQL value string
                values.append(
                    f"('{row_name}', '{data.get('property')}', '{occ.get('room_type_id')}', '{rate_type}', '{occ.get('occupancy_code')}','{dt}', {rate})"
                )

    if values:
        # join all values into a single SQL query
        values_str = ", ".join(values)
        # build UPSERT SQL
        sql = f"""
        INSERT INTO `tabRoom Rates` (`name`, `property`, `room_type_id`, `rate_type`, `occupancy_code`,`date`, `rate`)
        VALUES {values_str}
        ON DUPLICATE KEY UPDATE
        old_rate = rate,
        rate = VALUES(rate)
        """

        # execute and commit in Frappe
        frappe.db.sql(sql)

        # enqueue job for check change data and add to sync que log

        cm_info = get_channal_manager_info(data.get("property"))
        has_cm_rate_plan = len([x for x in  cm_info.rate_plans if x.edoor_rate_plan == data.get("rate_type") and (x.rate_plan_code or "")!=""])>0
        
        if cm_info and cm_info.prices_for_accommodation =="Receive from PMS":
            # check if rate plan has cm rate plan mapping
            if has_cm_rate_plan:
                prepare_sync_data_to_channel_manager(filters = {
                        "property":data.get("property"),
                        "start_date":min([getdate(d) for d in dates]),
                        "end_date":max([getdate(d) for d in dates]),
                        "room_types":[d.get("edoor_room_type") for d in data.get("room_types")],
                        "rate_type":data.get("rate_type")
                    }, 
                    run_comit = False
                )
    


        frappe.db.commit()

        
        frappe.msgprint("Bulk update room rate successfully")
        
        
        if str(cm_info.get("enable")) == "1":
            # if room rate plance mapping to cm rate plance 
            if cm_info.get("provider") == "Exely" and has_cm_rate_plan and cm_info.prices_for_accommodation =="Receive from PMS": 
                
                frappe.enqueue(
                    "edoor.channel_managers.exely.price_manager.sync_room_rate",
                    queue="short" if frappe.conf.get("developer_mode") else "channel_manager",
                        property=data.get("property")
                )
            

        return "Success"
         


def validate_bulk_update_room_rate(data):
    # validate if integrate channel manager then check sync status 
    cm_info = get_channal_manager_info(data.get("property"))
    has_cm_rate_plan = len([x for x in  cm_info.rate_plans if x.edoor_rate_plan == data.get("rate_type") and (x.rate_plan_code or "")!=""])>0
    if cm_info:
        if cm_info.enable==1 and has_cm_rate_plan: 
            if not  can_save_data(property=data.get("property"), title ="Prices update",provider=cm_info.provider):
                frappe.throw("Data sync to {0} Channel Manager is temporarily blocked. Please check the sync status.".format(cm_info.provider))
                
    # validate past date
    if not data.get("date_range"):
        frappe.throw("Please enter start date and end date")

    maximum_future_years_allowed = int(frappe.get_cached_value("eDoor Setting",None, "maximum_future_years_allowed"))
    max_date = getdate(today())
    max_date = max_date.replace(max_date.year + maximum_future_years_allowed, month=12, day=31)
 
    
    for dt in data.get("date_range"):
        start_date = getdate(dt.get("start_date"))
        if start_date< getdate(today()):
            frappe.throw("Start date cannot be earlier than the current date.")

        end_date = getdate(dt.get("end_date"))
        if end_date<start_date:
            frappe.throw("Start date cannot be earlier than the end date.")

        if end_date< getdate(today()):
            frappe.throw("End date cannot be earlier than the current date.")
        

        # validate end_date if it bigger then max date allow
        if end_date>max_date:
            frappe.throw("End date cannot be greater than the max date allowed ({}).".format(frappe.format_value(max_date,"Date")))

    # validate occupancy code
    
    has_change_data = False
    for dt in data.get("room_types"):
        change_data = [d for d in dt.get("occupancy_codes") if d.get("rate") !=None]
       
        # validate occupancy code required
        room_type_doc = frappe.get_cached_doc("Room Type",dt.get("edoor_room_type"))
        occupancy_codes = {d.get("occupancy_code"):d.get("required") for d in room_type_doc.rates}
         

        for d in change_data:
            if  d.get("rate") == None:
                frappe.throw(f"Please enter {d.get('title')} rate for room type {frappe.get_cached_value('Room Type',d.get('room_type_id'),'room_type')} ")
            else:
                if d.get("rate") == 0:
                    if occupancy_codes.get(d.get("occupancy_code")) == 1 :
                        frappe.throw(f"Please enter room rate for {d.get('title')} in room type {room_type_doc.room_type}")

                # validate min_rate
                
                if dt.get("enable_min_rate") ==1 and d.get("rate") < dt.get("min_rate"):
                    if frappe.get_cached_value("Occupancy Code",d.get("occupancy_code"),"occupancy_type") == "AdultBed":
                        frappe.throw(f"Room rate for room type “{dt.get('room_type_name')}”: the rate for {d.get('title')} cannot be lower than the minimum rate of {dt.get('min_rate')}.")
                has_change_data = True
            



    if not has_change_data:
        frappe.throw("There is no data to update room rates. Please enter the room rate you want to change.")





@frappe.whitelist(methods="POST")
def check_room_rate_on_update(data):
    def get_date_fitler():
        date_ranges = data.get("dates")

        date_conditions = []

        for r in date_ranges:
            date_conditions.append(
                "date between '{}' and '{}' ".format(
                    r.get("start_date"),
                    r.get("end_date")
                )
            )

    

        return " OR ".join(date_conditions)
    
    sql = """
    select
            room_type_id,
            occupancy_code,
            max(rate) as rate
        from `tabRoom Rates`
        where
            rate > 0 and
            rate_type = %(rate_type)s and 
            property = %(property)s and 
            room_type_id in %(room_types)s and 
            (
                {date_conditions}
            )
        group by
            room_type_id,
            occupancy_code
        having
            MIN(rate) = MAX(rate);
    """.format(date_conditions = get_date_fitler())
  
    data =  frappe.db.sql(sql, {"rate_type":data.get("rate_type"),"property":data.get("property"),"room_types":data.get("room_types")},as_dict = 1)
    return  {
        f"{item['room_type_id']}_{item['occupancy_code']}": item["rate"]
        for item in data
    }




# prepare sync data to channel manager
def prepare_sync_data_to_channel_manager(filters,run_comit=True):
    # frappe.throw(str(filters))
    if not filters.get("property"):
        return
        
    cm_info = get_channal_manager_info(filters.get("property"))
    # check can sync data to cm only it enable, price receive from PMS and fist init is done
    if (str(cm_info.get("enable")) == "1" 
        and cm_info.get("prices_for_accommodation") =="Receive from PMS" 
        and str(cm_info.get("initialized_prices_upload")) == "1"): 
        # add changed data to sync data log
        sql = """
            insert into `tabChannel Manager Sync Data Log` (
                name,
                provider,
                request_type,
                property,
                rate_type,
                room_type,
                occupancy_code,
                date,
                value
            )
            select 
                name,
                '{provider}' as provider,
                '{request_type}' as request_type,
                property,
                rate_type,
                room_type_id,
                occupancy_code,
                date,
                rate as value
            from `tabRoom Rates` 
            where
                room_type_id in %(room_types)s and 
                rate_type = %(rate_type)s and 
                date between %(start_date)s and %(end_date)s  and 
                rate <> old_rate
            ON DUPLICATE KEY UPDATE
                sync_session_id = '',
                value = VALUES(value);

        """.format(provider = cm_info.get("provider"),request_type = REQUEST_TYPE)
        frappe.db.sql(sql,filters)

        if run_comit:
            frappe.db.commit()



@frappe.whitelist()
def get_room_rate_detail(property,rate_type,date):
    sql = """
        select 
            rr.room_type_id as rt,
            rr.occupancy_code as occ,
            rr.rate
        from `tabRoom Rates` rr
        where
            property = %(property)s and 
            date = %(date)s and 
            rate_type = %(rate_type)s
    """

    data = frappe.db.sql(sql,{"property":property,"rate_type":rate_type,"date":date},as_dict =1)
    room_type_ids = set([d.get("rt") for d in data])
    room_types=None
    if  room_type_ids:
        room_types = frappe.db.sql("select name,alias,room_type,sort_order from `tabRoom Type` where name in %(names)s order by sort_order",{"names":room_type_ids},as_dict = 1)
    # occupancy code
    occupancy_code = set([d.get("occ") for d in data])
    occupancy_code_data=None
    if  occupancy_code:
        occupancy_code_data = frappe.db.sql("select name,title,sort_order from `tabOccupancy Code` where name in %(names)s order by sort_order",{"names":occupancy_code},as_dict=1)

    return {
        "room_types":room_types,
        "room_rate":data,
        "occupancy_codes":occupancy_code_data
    }

@frappe.whitelist(methods="POST")
@rate_limit(limit=3, seconds=60)
def resync_room_rate(data=None):

    if not data:
        data = {
            "rate_types": ["Daily Rate"],
            "property": "ESTC Hotel 6",
            "date_ranges": [
                {"start_date": "2026-05-01", "end_date": "2026-05-30"},
                {"start_date": "2026-07-01", "end_date": "2026-07-30"}
            ],
            "room_types": ["RT-0001", "RT-0004"],
        }

    cm_info = get_channal_manager_info(data.get("property"))
    if not cm_info:
        frappe.throw("No Channel Manager Integration")
    if cm_info.enable == 0:
        frappe.throw("Channel manager integration is disabled")
    if cm_info.prices_for_accommodation =="Manage in CM":
        frappe.throw("Prices update is not allow to manager in PMS")
    
    # validate rate plan has integration
    for rp in data.get("rate_types"):
        if len([x for x in  cm_info.rate_plans if x.edoor_rate_plan == rp and (x.rate_plan_code or "")!=""])==0:
            frappe.throw("No rate plan mapping found for the rate plan '{0}'.".format(rp))

    

    
    conditions = []
    filters = {}

    for i, r in enumerate(data.get("date_ranges")):
        conditions.append(
            f"(rr.date between %(start_{i})s and %(end_{i})s)"
        )
        filters[f"start_{i}"] = r.get("start_date")
        filters[f"end_{i}"] = r.get("end_date")

    date_filters = " OR ".join(conditions)

    sql = f"""
         insert into `tabChannel Manager Sync Data Log` (
            name,
            provider,
            request_type,
            property,
            rate_type,
            room_type,
            occupancy_code,
            date,
            value
        )
        select 
            name,
            '{cm_info.provider}' as provider,
            '{REQUEST_TYPE}' as request_type,
            property,
            rate_type,
            room_type_id,
            occupancy_code,
            date,
            rate as value
        FROM `tabRoom Rates` rr
        WHERE
            ({date_filters})
            AND rr.property = %(property)s
            AND rr.rate_type IN %(rate_types)s
            AND rr.room_type_id IN %(room_types)s
        ON DUPLICATE KEY UPDATE
            sync_session_id = '',
            value = VALUES(value);

    """ 

    filters.update({
        "property": data.get("property"),
        "rate_types": tuple(data.get("rate_types")),
        "room_types": tuple(data.get("room_types"))
    })

    frappe.db.sql(sql, filters, as_dict=1)
    frappe.db.commit()

    if cm_info.get("provider") == "Exely": 
        frappe.enqueue(
            "edoor.channel_managers.exely.price_manager.sync_room_rate",
            queue="short" if frappe.conf.get("developer_mode") else "channel_manager",
                property=data.get("property")
        )
            



    frappe.msgprint("Room rate update sent successfully. The sync is running in the background, and you will be notified when it is complete.")

    return "Success"




