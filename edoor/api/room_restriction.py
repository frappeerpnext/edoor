import frappe
from edoor.api.utils import make_hash,generate_unique_dates
from itertools import product
from edoor.channel_managers.utils import get_channal_manager_info,can_save_data
from frappe import _
from frappe.utils import getdate, add_to_date,today
from frappe.rate_limiter import rate_limit


REQUEST_TYPE = "Restriction update"
# we use this prefix to combine unique key of restriction for upsert statemnt bulk insert

RESTRICTION_TYPE_PREFIX = {
        "Stop Sale": 'ss',
        "Cta": 'cta',
        "Ctd": 'ctd',
        "MinLos":"ml",
        "MaxLos":"mxl",
        "MinLosArrival":"mla",
        "MaxLosArrival":"mxla",
        "MinAdvBooking":"mab",
        "MaxAdvBooking":"mxab",
        "FullPatternLos":"fpl",
}


@frappe.whitelist(methods="POST")
def get_room_restriction_data(filters):
    return_data = {

    }
    for rt in filters.get("restriction_types") : 
        
        if rt in ["Closed","Cta","Ctd","MinLos","MaxLos","MinLosArrival","MaxLosArrival","MinAdvBooking","MaxAdvBooking"]:
            return_data[rt] =  get_close_sale_data({**filters,"restriction_type":rt})
        elif rt == "FullPatternLos":
            return_data[rt] = {}

    return return_data


def get_close_sale_data(filters):
    sql = """
        SELECT 
            CONCAT(DATE_FORMAT(rr.date,'%%y%%m%%d')) AS `key`,
            rr.value
        FROM `tabRoom Restriction` rr
        WHERE
            rr.room_type_id IN %(room_types)s AND 
            rr.rate_type = %(rate_type)s AND 
            rr.date BETWEEN %(start_date)s AND %(end_date)s and 
            rr.restriction_type = %(restriction_type)s and 
            not rr.value  in ('0','')
    """
     
    data = frappe.db.sql(sql, filters, as_dict=1)
    return {item['key']: item['value'] for item in data}


@frappe.whitelist()
def testme():
    data = {
        "property":"ESTC Hotel 6",
        "restriction_type":"Closed",
        "rate_type_id":"Daily Rate",
        "date_ranges":[
            {"start_date":"2026-05-01","end_date":"2026-05-30"},
            {"start_date":"2026-07-01","end_date":"2026-07-30"},
        ],
        "room_types":[
            {
                "room_type":"RT-0001",
                "value": 1
            },
            {
                "room_type":"RT-0002",
                "value": 0
            },
        ]

    }

    return bulk_update_room_restriction(data)

@frappe.whitelist(methods="POST")
@rate_limit(limit=5, seconds=60)
def bulk_update_room_restriction(data):

    # date={"property":"","restriction_type":"Stop Sales","date_range":[{"start_date":,"end_date"},"room_types":[
    # {"room_type_id":,"value":1}
    # ]}
    validate_bulk_update_room_restriction(data)

    
    dates = generate_unique_dates(data.get("date_ranges"))
    
    # set value = "" if reset 
    for rt in data.get("room_types"):
        if rt.get("reset_value") == True:
            rt["value"] = ""

    # cross join date and room types to get list dict of room_type,date and value
    
    raw_data = [
        {
            "name": make_hash(f"rs{RESTRICTION_TYPE_PREFIX.get(data.get('restriction_type'))}{data.get('rate_type')}{r.get('room_type_id')}{d}"),
            "date": d,
            "room_type_id": r.get("room_type_id"),
            "value": r.get("value")
        }
        for d, r in product(dates, data.get("room_types"))
    ]

    # prepare bulk upsert statement
    values_sql = ",".join(
        f"('{d.get('name')}','{data.get('property')}','{data.get('restriction_type')}','{d.get('date')}','{data.get('rate_type')}','{d.get('room_type_id')}','{d.get('value')}')"
        for d in raw_data
    )
   

    


    sql = f"""
        INSERT INTO `tabRoom Restriction`
        (`name`,`property`,`restriction_type`, `date`,`rate_type`, `room_type_id`, `value`)
        VALUES
        {values_sql}
        ON DUPLICATE KEY UPDATE
        `old_value`=`value`,
        `value` = VALUES(`value`);
    """
    
    frappe.db.sql(sql)


    prepare_sync_data_to_channel_manager(filters = {
            "property":data.get("property"),
            "start_date":min([getdate(d) for d in dates]),
            "end_date":max([getdate(d) for d in dates]),
            "room_types":[d.get("room_type_id") for d in data.get("room_types")],
            "rate_type":data.get("rate_type"),
            "restriction_type":data.get("restriction_type")
        }, 
        run_comit = False
    )

    # delete record that have value empty
    sql="delete from `tabRoom Restriction` where value = ''"
    frappe.db.sql(sql)

    
            
    frappe.db.commit()
     
    frappe.msgprint(f"Update restriction {data.get('restriction_type')} successfully")

    # check cm info and cm provider and send sync data to cm
    cm_info = get_channal_manager_info(data.get("property"))
    has_cm_rate_plan = len([x for x in  cm_info.rate_plans if x.edoor_rate_plan == data.get("rate_type") and (x.rate_plan_code or "")!=""])>0
    

    if str(cm_info.get("enable")) == "1":
        if str(cm_info.initialized_restrictions_upload) == "1":
            if cm_info.get("provider") == "Exely" and has_cm_rate_plan and cm_info.restrictions  =="Receive from PMS": 
                frappe.enqueue(
                    "edoor.channel_managers.exely.room_restriction.sync_room_restriction",
                    queue="short" if frappe.conf.get("developer_mode") else "channel_manager",
                    property=data.get("property")
                )
    
    return "Success"


def validate_bulk_update_room_restriction(data):
    # validate if integrate channel manager then check sync status 
    if not data.get("room_types"):
        frappe.throw(_("Please enter restriction value"))
    cm_info = get_channal_manager_info(data.get("property"))
    has_cm_rate_plan = len([x for x in  cm_info.rate_plans if x.edoor_rate_plan == data.get("rate_type") and (x.rate_plan_code or "")!=""])>0
    
    if cm_info:
        if cm_info.enable==1 and has_cm_rate_plan: 
            if not  can_save_data(property=data.get("property"), title ="Restriction update",provider=cm_info.provider):
                frappe.throw("Data sync to {0} Channel Manager is temporarily blocked. Please check the sync status.".format(cm_info.provider))
                
    # validate past date
    if not data.get("date_ranges"):
        frappe.throw("Please enter start date and end date")

    maximum_future_years_allowed = int(frappe.get_cached_value("eDoor Setting",None, "maximum_future_years_allowed"))
    max_date = getdate(today())
    max_date = max_date.replace(max_date.year + maximum_future_years_allowed, month=12, day=31)
 
    
    for dt in data.get("date_ranges"):
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



# prepare sync data to channel manager
def prepare_sync_data_to_channel_manager(filters,run_comit=True):
    if not filters.get("property") :
        return
    
    cm_info = get_channal_manager_info(filters.get("property"))
    if not cm_info :
        return

    if cm_info.enable == 0 or   cm_info.restrictions !="Receive from PMS" :
        return
    if cm_info.initialized_restrictions_upload == 0:
        frappe.msgprint("Restriction not synced to the channel manager because the initial update was not performed.", title="Restriction",
            indicator="info")
        return

    has_cm_rate_plan = len([x for x in  cm_info.rate_plans if x.edoor_rate_plan == filters.get("rate_type") and (x.rate_plan_code or "")!=""])>0
    if not has_cm_rate_plan:
        return
    
    if not str(cm_info.get(filters.get("restriction_type").lower()))  == "1" :
        return


 

    sql = """
        insert into `tabChannel Manager Sync Data Log` (
            name,
            provider,
            request_type,
            property,
            rate_type,
            room_type,
            restriction_type,
            `date`,
            `value`
        )
        select 
            name,
            '{provider}' as provider,
            '{request_type}' as request_type,
            property,
            rate_type,
            room_type_id,
            restriction_type,
            `date`,
            `value`
        from `tabRoom Restriction` 
        where
            room_type_id in %(room_types)s and 
            rate_type = %(rate_type)s and 
            `date` between %(start_date)s and %(end_date)s  and 
            coalesce(`value`,'') <> coalesce(old_value,'dummy')
        ON DUPLICATE KEY UPDATE
            sync_session_id = '',
            `value` = VALUES(`value`);

    """.format(provider = cm_info.get("provider"),request_type=REQUEST_TYPE)

   
    # frappe.throw(str(filters))
        
    frappe.db.sql(sql,filters)

    if run_comit:
        frappe.db.commit()


@frappe.whitelist()
def get_restriction_type_list(property_name):

    result = frappe.db.sql("""
        SELECT 
            `closed`,
            `minlos`,
            `maxlos`,
            `cta`,
            `ctd`,
            `minlosarrival`,
            `maxlosarrival`,
            `minadvbooking`,
            `maxadvbooking`,
            `fullpatternlos`
        FROM `tabChannel Manager Integration`
        WHERE property = %s
        LIMIT 1
    """, (property_name,), as_dict=True)

    if not result:
        return []

    doc = result[0]

    map_labels = {
        "closed": "Closed",
        "minlos": "MinLos",
        "minlosarrival": "MinLosArrival",
        "fullpatternlos": "FullPatternLos",
        "maxlos": "MaxLos",
        "maxlosarrival": "MaxLosArrival",
        "minadvbooking": "MinAdvBooking",
        "maxadvbooking": "MaxAdvBooking",
        "cta": "Cta",
        "ctd": "Ctd"
    }

    return [
        map_labels[key]
        for key in doc
        if key in map_labels and doc.get(key) == 1
    ]


@frappe.whitelist(methods="POST")
@rate_limit(limit=3, seconds=60) 
def resync_room_restriction(data=None):

    if not data:
        data = {
            "rate_types": ["Daily Rate"],
            "property": "ESTC Hotel 6",
            "date_ranges": [
                {"start_date": "2026-05-01", "end_date": "2026-05-30"},
                {"start_date": "2026-07-01", "end_date": "2026-07-30"}
            ],
            "room_types": ["RT-0001", "RT-0004"],
            "restriction_types":["Closed","MinLOS","MaxLOS","FullPatternLos"]
        }


    cm_info = get_channal_manager_info(data.get("property"))
    if not cm_info:
        frappe.throw("No Channel Manager Integration")
    if cm_info.enable == 0:
        frappe.throw("Channel manager integration is disabled")
    if cm_info.restrictions =="Manage in CM":
        frappe.throw("Restriction is not allow to manager from PMS")
    
    # validate rate plan has integration
    for rp in data.get("rate_types"):
        if len([x for x in  cm_info.rate_plans if x.edoor_rate_plan == rp and (x.rate_plan_code or "")!=""])==0:
            frappe.throw("No rate plan mapping found for the rate plan '{0}'.".format(rp))

    # validate restriction code allow manage from pms
    for rs in data.get("restriction_types"):
        if str(cm_info.get(rs.lower())) == "0":
            frappe.throw("Restriction type {0} is not allow to manage from PMS".format(rs))

    

    
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
            restriction_type,
            `date`,
            `value`
        )
        select 
            name,
            '{cm_info.provider}' as provider,
            'OTA_HotelAvailNotifRQ' as request_type,
            property,
            rate_type,
            room_type_id,
            restriction_type,
            `date`,
            `value`
        from `tabRoom Restriction` rr
        WHERE
            ({date_filters})
            AND rr.property = %(property)s
            AND rr.rate_type IN %(rate_types)s
            AND rr.room_type_id IN %(room_types)s 
            AND rr.restriction_type IN %(restriction_types)s 
        ON DUPLICATE KEY UPDATE
            sync_session_id = '',
            value = VALUES(value);

    """ 

    filters.update({
        "property": data.get("property"),
        "rate_types": tuple(data.get("rate_types")),
        "room_types": tuple(data.get("room_types")),
        "restriction_types": tuple(data.get("restriction_types"))
    })

    frappe.db.sql(sql, filters, as_dict=1)
    frappe.db.commit()

    if cm_info.get("provider") == "Exely": 
        frappe.enqueue(
            "edoor.channel_managers.exely.room_restriction.sync_room_restriction",
            queue="short" if frappe.conf.get("developer_mode") else "channel_manager",
                property=data.get("property")
        )
            



    frappe.msgprint("Room rate update sent successfully. The sync is running in the background, and you will be notified when it is complete.")

    return "Success"





