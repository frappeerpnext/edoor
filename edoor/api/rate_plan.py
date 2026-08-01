import frappe 
from edoor.channel_managers.utils import get_channal_manager_info,can_save_data,add_change_data_log
from frappe.rate_limiter import rate_limit

from edoor.channel_managers.exely.rate_limit import check_rate_limit_status_by_room_type
from frappe.utils import getdate, add_to_date,today
from edoor.api.utils import make_hash,generate_unique_dates
from edoor.channel_managers.data_upload import get_data_upload_status
from epos_restaurant_2023.custom_socket_client import emit_event
import time


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
        "provider": cm_info.get("provider"),
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
                    run_commit = False
                )
    
        # save change data log
        data["room_type"] =  ", ".join([d.get("room_type_name") for d in data.get("room_types") or []])
        data["traction_type"] =  "Prices update"
        add_change_data_log(data,run_commit=False)
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

            # validate data manage in CM
            if cm_info.get("prices_for_accommodation") == "Deliver to PMS":
                frappe.throw("Cannot manage room rate because it is managed in the Channel Manager.")
                
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
def prepare_sync_data_to_channel_manager(filters,run_commit=True):
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

        # update old value to value 
        sql="""
            update  `tabRoom Rates` 
            SET old_rate = rate
            where
                room_type_id in %(room_types)s and 
                rate_type = %(rate_type)s and 
                date between %(start_date)s and %(end_date)s  
        """
        frappe.db.sql(sql,filters)

        if run_commit:
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
    rate_type_doc = frappe.get_cached_doc("Rate Type",rate_type)
    room_type_ids = set([d.get("room_type") for d in rate_type_doc.room_types])
    room_types=None
    if  room_type_ids:
        room_types = frappe.db.sql("select name,alias,room_type,sort_order from `tabRoom Type` where name in %(names)s order by sort_order",{"names":room_type_ids},as_dict = 1)
        
    # occupancy code
    occupancy_code = set([d.get("occ") for d in data])
    occupancy_code_data=None
    if  occupancy_code:
        occupancy_code_data = frappe.db.sql("select name,title,sort_order from `tabOccupancy Code` where name in %(names)s order by sort_order",{"names":occupancy_code},as_dict=1)

    # get restriction
    sql = """
        select restriction_type,room_type_id, value from `tabRoom Restriction`
        where
            property = %(property)s and 
            date = %(date)s and 
            rate_type = %(rate_type)s
        order by 
            case 
                when restriction_type = 'Closed' then 1 
                when restriction_type = 'Cta' then 2
                when restriction_type = 'Ctd' then 3 
                when restriction_type = 'MinLos' then 4 
                when restriction_type = 'MaxLos' then 5 
                when restriction_type = 'MinLosArrival' then 6 
                when restriction_type = 'MaxLosArrival' then 7 
                when restriction_type = 'MinAdvBooking' then 8 
                when restriction_type = 'MaxAdvBooking' then 9 
                when restriction_type = 'FullPatternLos' then 10 
            end 
    """
    restriction_data = frappe.db.sql(sql, {"property":property,"rate_type":rate_type,"date":date},as_dict = 1)

    return {
        "room_types":room_types or [],
        "room_rate":data,
        "occupancy_codes":occupancy_code_data or [],
        "restriction":restriction_data
    }

@frappe.whitelist(methods="POST")
@rate_limit(limit=3, seconds=60)
def resync_room_rate(data=None, auto_sync_to_cm=True,validate_initialized_upload = True):

    if not data:
        data = {
            "rate_types": [
                {
                    "rate_type": "Daily Rate",
                    "room_types": [
                    {
                        "room_type": "RT-0004",
                        "occupancy_codes": [
                        "G1",
                        "G2",
                        "G3",
                        "C3",
                        "C4",
                        "EA1",
                        "EC1",
                        "EC2",
                        "EC3",
                        "EC4",
                        "CWB1"
                        ]
                    }
                    ]
                }
                        ],
            "property": "ESTC Hotel 6",
            "date_ranges": [
                {"start_date": "2026-05-01", "end_date": "2026-05-30"},
                {"start_date": "2026-07-01", "end_date": "2026-07-30"}
            ],
        }

    cm_info = get_channal_manager_info(data.get("property"))
    
    if not cm_info:
        frappe.throw("No Channel Manager Integration")
    if cm_info.enable == 0:
        frappe.throw("Channel manager integration is disabled")
    if cm_info.prices_for_accommodation !="Receive from PMS":
        frappe.throw("Prices update is not allow to manager in PMS")
        
    if validate_initialized_upload and cm_info.initialized_prices_upload ==0:
        frappe.throw("Room rates are not initialized yet. Please upload them to the channel manager first.")
    

    
    # validate rate plan has integration
    if not data.get("rate_types"):
        frappe.throw("Please select room types and occupancy codes to synchronize to channel manager")
    for rp in data.get("rate_types"):
        
        if len([x for x in  cm_info.rate_plans if x.edoor_rate_plan == rp.get("rate_type") and (x.rate_plan_code or "")!=""])==0:
            frappe.throw("No rate plan mapping found for the rate plan '{0}'.".format(rp.get("rate_type")))


    

    
    conditions = []
    filters = {}

    for i, r in enumerate(data.get("date_ranges")):
        conditions.append(
            f"(rr.date between %(start_{i})s and %(end_{i})s)"
        )
        filters[f"start_{i}"] = r.get("start_date")
        filters[f"end_{i}"] = r.get("end_date")

    date_filters = " OR ".join(conditions)
    filters.update({
        "property": data.get("property")
    })


    
    def save_data_sync_data_log(rate_type,room_type, occupancy_codes):

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
                AND rr.rate_type = %(rate_type)s
                AND rr.room_type_id = %(room_type)s and 
                rr.occupancy_code in %(occupancy_codes)s
            ON DUPLICATE KEY UPDATE
                sync_session_id = '',
                value = VALUES(value);

        """ 

        filters.update({
            "rate_type": rate_type,
            "room_type":room_type,
            "occupancy_codes":occupancy_codes
        })

        frappe.db.sql(sql, filters, as_dict=1)

    for rp in data.get("rate_types"):
        
        for rt in rp.get("room_types"):
            if rt.get("occupancy_codes"):
                save_data_sync_data_log(rate_type =rp.get("rate_type"), room_type = rt.get("room_type"), 
                occupancy_codes =  rt.get("occupancy_codes"))
        
    frappe.db.commit()
    if auto_sync_to_cm:
        if cm_info.get("provider") == "Exely": 
            frappe.enqueue(
                "edoor.channel_managers.exely.price_manager.sync_room_rate",
                queue="short" if frappe.conf.get("developer_mode") else "channel_manager",
                    property=data.get("property")
            )
            

    frappe.msgprint("Room rate update sent successfully. The sync is running in the background, and you will be notified when it is complete.")

    return "Success"





@frappe.whitelist(methods="POST")
@rate_limit(limit=5, seconds=60)
def initialized_room_rate_upload(property = "ESTC HOTEL 6"):
    
    cm_info = get_channal_manager_info(property)
    if not cm_info:
        frappe.throw("No channel manager integration for this property")
    if cm_info.enable == 0:
        frappe.throw("Channel Manager is disable")
    
    if cm_info.initialized_prices_upload == 1:
        frappe.throw("Room rate is already synced with the channel manager. Please use the 'Re-upload' option in the dashboard.")
    
    if not cm_info.prices_for_accommodation == "Receive from PMS":
        frappe.throw("Room rate is not manage from PMS")
    
    
    room_types = [d.get("edoor_room_type") for d in  cm_info.get("room_types") if d.get("edoor_room_type") and d.get("room_type_code")]

    rate_types =  [{"rate_type": d.get("edoor_rate_plan"),"room_types":[]} for d in  cm_info.get("rate_plans") if d.get("edoor_rate_plan") and d.get("rate_plan_code")]

    for rp in rate_types:
        rate_type_doc = frappe.get_cached_doc("Rate Type",rp.get("rate_type"))
        for rt in rate_type_doc.room_types:
            if rt.get("room_type") in room_types:
                room_type_doc = frappe.get_cached_doc("Room Type",rt.get("room_type"))
                occupancy_codes = [
                    x.get("occupancy_code") 
                    for x in room_type_doc.rates
                ]

                rp["room_types"].append({
                    "room_type":rt.get("room_type"),
                    "occupancy_codes": occupancy_codes
                })



    
    # 
    if not room_types or len(room_types) == 0:
        frappe.throw("No room type mapping to channel manager room type")
        
    if not rate_types or len(rate_types) == 0:
        frappe.throw("No rate plan mapping to channel manager rate plan")
    
    # validate min rate


    filter = {
            "rate_types": rate_types,
            "property": property,
            "date_ranges": [
                {"start_date": today(), "end_date": frappe.utils.add_years(today(),1)},
            ],
            "room_types": room_types,
    }
     

    resync_room_rate(data=filter, 
        auto_sync_to_cm=False,
        validate_initialized_upload=False
    )
    

    # run equeue job to update data to cm
    
    frappe.msgprint("We are currently processing upload your room rate data to channel manager in the background. Please wait until the upload to the channel manager is completed.")

    frappe.enqueue(
        "edoor.api.rate_plan.update_room_rate_to_channel_manager",
        queue="long",
        property= property
    )
    


    return "Room rate is being upload to channel manager now"

@frappe.whitelist()
def update_room_rate_to_channel_manager(property="ESTC HOTEL 6"):
    # first init room rate 
    # do task here until data from Sync Data Log clear
    # stop resync cm data from schedult job
    # we use this in 
    # edoor\channel_managers\resync_data.py

    frappe.cache.set_value(f"{property}_channel_manager_stop_resync_fail_job", "1", expires_in_sec=60*10)
    cm_info = get_channal_manager_info(property)

    filter = {
        "property": property,
        "request_type":"Prices update",
        "provider":cm_info.provider
    }

    sql="select distinct room_type from `tabChannel Manager Sync Data Log` where property=%(property)s and request_type = 'Prices update' and provider=%(provider)s"
    room_type_data = frappe.db.sql(sql,filter,as_dict=1) or []
    for rt in room_type_data:
        if cm_info.provider == "Exely":
            rate_limit_status = check_rate_limit_status_by_room_type(property, rt.get("room_type"))
            rt["rate_limit_status"] = rate_limit_status.get("rate_limit_status")
            # alert user about some room type reach rate limit


    
 

    if len(room_type_data)>0:
        update_sync_status_to_cached(property, [d.get("room_type") for d in room_type_data],"In Progress")

        if len([x for x in room_type_data if x.get("rate_limit_status") == True])>0:
            if cm_info.provider == "Exely":
                from edoor.channel_managers.exely.price_manager import sync_room_rate
                sync_room_rate(
                    property = property,
                    retry_sync = False
                )
                
                time.sleep(15)
            else:
                pass
                # for other channel manager integration
        else:
            # synch data is reach rate limit for value change
            time.sleep(45)


        # enqueue update sync status to redish cache to make it run after db commit
        # cause we need to count record in db
        frappe.enqueue(
            "edoor.api.rate_plan.update_sync_status_to_cached",
            queue="long",
            property= property
        )

        # send send resync pending data
        
        frappe.enqueue(
            "edoor.api.rate_plan.update_room_rate_to_channel_manager",
            queue="long",
            property= property
        )

    

@frappe.whitelist()   
def update_sync_status_to_cached(property=None,room_types=None,status=None):
    cm_info = get_channal_manager_info(property)
    if not room_types:
        
        room_types = [d.get("edoor_room_type") for d in cm_info.room_types if d.get("edoor_room_type")]
    for rt in room_types:
        if not rt:
            continue

        cached_key = f"data_initialize_room_rate_{rt}"
        if status:
            frappe.cache().set_value(cached_key, status)
        else:
            filter = {"property":property,"room_type":rt,"request_type":"Prices update"}
            if frappe.db.exists("Channel Manager Sync Data Log",filter):
               frappe.cache().set_value(cached_key, "In Progress")
            else:
                frappe.cache().set_value(cached_key, "Complete")

    # update to channel manager integration set state we already upload room rate to cm
    
    if not frappe.db.exists("Channel Manager Sync Data Log",{
        "property":property,
        "request_type":"Prices update"
    }):
        
        frappe.db.set_value("Channel Manager Integration",property,"initialized_prices_upload",1)
        frappe.cache.delete_value(f"{property}_channel_manager_info") 
        # remove stop sync state
        frappe.cache.delete_value(f"{property}_channel_manager_stop_resync_fail_job")



    
    # emit event to socket client
    emit_event("ChannelManagerUpdate",{
                "action":"update_channel_manager_data_upload_status",
                "property": property,
                "upload_status":get_data_upload_status(property)
    })


 
@frappe.whitelist()
def runme():
    return get_room_rate_from_channel_manager()

@frappe.whitelist(methods="POST")
def get_room_rate_from_channel_manager(property="ESTC HOTEL 6"):
    # validate
    # check provider
    # send soap request base on provider
    # get xml data conver to dict
    # mapping occupanyc code
    # bulk update to Room Rate base on rate type
    cm_info = get_channal_manager_info(property)
    
    if not cm_info:
        frappe.throw("No channel manager integration")
    if cm_info.initialized_prices_upload == 0:
        frappe.throw("Room rate first update to Channel Manager not run yet. Please do it first before sync rate.")

    if cm_info.prices_for_accommodation != "Deliver to PMS":
        frappe.throw("In order to get room rates from Channel Manager, please set the room rate sync mode to “Deliver to PMS” in your Channel Manager backend and PMS–Channel Manager integration settings.")
    
    

    # check provider and get data relevant to cm provider
    if cm_info.provider == "Exely":
        from edoor.channel_managers.exely.price_manager import get_room_rate_from_channel_manager as get_room_rate_from_exely
        return get_room_rate_from_exely( property = property, cm_hotel_code = cm_info.property_code)
    return cm_info



@frappe.whitelist()
def get_restriction_codes(property,rate_type=None):
    cm_info = get_channal_manager_info(property) 
    if not cm_info:
        return get_property_restriction_codes(property)
    else:
        if rate_type:
            if [x for x in cm_info.rate_plans if x.get("edoor_rate_plan") == rate_type and x.get("rate_plan_code")]:
                return get_cm_restriction(property)

    return get_property_restriction_codes(property)

def get_property_restriction_codes(property):
    doc = frappe.get_cached_doc("Business Branch", property)
    return {
        "closed":doc.closed,
            "minlos":doc.minlos,
            "minlosarrival":doc.minlosarrival,
            "fullpatternlos":doc.fullpatternlos,
            "maxlos":doc.maxlos,
            "maxlosarrival":doc.maxlosarrival,
            "minadvbooking":doc.minadvbooking,
            "maxadvbooking":doc.maxadvbooking,
            "cta":doc.cta,
            "ctd":doc.ctd
    }

@frappe.whitelist()
def get_cm_restriction(property):
    sql = """
        select
            closed,
            minlos,
            minlosarrival,
            fullpatternlos,
            maxlos,
            maxlosarrival,
            minadvbooking,
            maxadvbooking,
            cta,
            ctd
        FROM `tabChannel Manager Integration`
        WHERE
            name = %(property)s
            AND restrictions in  ('Receive from PMS','Deliver to PMS')
    """
    data = frappe.db.sql(sql, {"property":property}, as_dict=1)
    return data[0]
