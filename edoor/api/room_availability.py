import frappe
from frappe.utils import add_to_date,getdate,today
import json
from lxml import etree
from edoor.api.utils import get_room_type_ids
from frappe.model.document import bulk_insert
from edoor.channel_managers.utils import get_channal_manager_info,get_sync_max_date
import time
from frappe.rate_limiter import rate_limit
from edoor.channel_managers.data_upload import get_data_upload_status

REQUEST_TYPE = 'Availability update'


@frappe.whitelist()
def get_current_working_date():
    sql="select max(posting_date) as date from `tabWorking Day` where is_closed = 0"
    data = frappe.db.sql(sql,as_dict=1)
    if data:
        if data[0].get("date"):
            return data[0].get("date")
    return today

@frappe.whitelist()
def testme():
    
    return update_room_availability(
       {
   "end_date": "2026-04-08",
   "property": "ESTC HOTEL 6",
   "room_type_id": [
    "RT-0001"
   ],
   "start_date": "2026-03-27",
   "sync_room_available_to_channel_manager": True
  }
 
    )

@frappe.whitelist()
def fix_room_availibility():
    properties = frappe.db.sql("select name from `tabBusiness Branch`",as_dict=1)
    for d in properties:
        update_room_availability({
            "property":d.get("name")
        })
    


def update_room_availability(filters=None,run_commit=True):
    # filters = 
    #   "property": frappe.get_cached_value("Reservation Stay",stay_names[0],"property"),
    #     "start_date": min([d["start_date"] for d in affected_data]),
    #     "end_date": max([d["end_date"] for d in affected_data]),
    #     "room_type_id": list(set([d["room_type_id"] for d in affected_data])),

    


    filters["room_type_id"] =  filters.get("room_type_id")  or get_room_type_ids(filters.get("property"))
   
    if not filters.get("room_type_id"):
        return  # or skip query

    filters["start_date"] =  filters.get("start_date")  or today()


    filters["end_date"] =  filters.get("end_date")  or add_to_date(today(),years = 5)
    
    if not "sync_room_available_to_channel_manager" in filters:
        filters["sync_room_available_to_channel_manager"] = True
    
 

    sql="""
        update `tabDaily Property Data` d
        JOIN ( 
            select 
                t.date,
                t.room_type_id,
                sum(t.type = 'Reservation') as total_occupy,
                sum(t.type = 'Block') as total_block
            from `tabTemp Room Occupy` t
            where
                
                t.is_active = 1 and 
                t.date between %(start_date)s and %(end_date)s and 
                t.room_type_id in %(room_type_id)s  and 
                property = %(property)s
            group by 
                t.room_type_id,
                t.date

        ) AS t on d.room_type_id = t.room_type_id and d.date = t.date 
        set 
            d.old_room_available = d.total_room_available,
            d.total_occupy = t.total_occupy, 
            d.total_block = t.total_block, 
            d.total_room_available = d.total_room - (t.total_occupy + t.total_block)
        where
            d.property = %(property)s and 
            d.date between %(start_date)s and %(end_date)s and 
            d.room_type_id in %(room_type_id)s
    """
    frappe.db.sql(sql,filters)
   

 
    # send data to sync sync data log log

    prepare_sync_data_to_channel_manager(filters,run_commit=False)


    

 
    
    cm_info = get_channal_manager_info(filters.get("property"))
    if str(cm_info.get("enable")) == "1":
        
        if filters.get("sync_room_available_to_channel_manager") == True:
            # check if provider is exely
            if cm_info.get("provider") == "Exely" and cm_info.get("rooms_availability") == "Receive from PMS":
                frappe.enqueue(
                    "edoor.channel_managers.exely.availability.sync_room_availability",
                    queue="channel_manager",
                    property=filters.get("property")
                )

    if run_commit:
        frappe.db.commit()

    



# prepare sync data to channel manager
def prepare_sync_data_to_channel_manager(filters,run_commit=True):
    # frappe.throw(str(filters))
    if not filters.get("property"):
        return
        
    cm_info = get_channal_manager_info(filters.get("property"))
    # check can sync data to cm only it enable, price receive from PMS and fist init is done
    if (str(cm_info.get("enable")) == "1" 
        and cm_info.get("rooms_availability") =="Receive from PMS" 
        and str(cm_info.get("initialized_availability_upload")) == "1"): 
        # add changed data to sync data log
        sql = """
            insert into `tabChannel Manager Sync Data Log` (
                name,
                provider,
                request_type,
                property,
                room_type,
                date,
                value
            )
            select 
                name,
                '{provider}' as provider,
                '{request_type}' as request_type,
                property,
                room_type_id,
                date,
                total_room_available as value
            from `tabDaily Property Data` 
            where
                room_type_id in %(room_type_id)s and 
                date between %(start_date)s and %(end_date)s  and 
                coalesce(total_room_available,0) <> coalesce(old_room_available,0)
            ON DUPLICATE KEY UPDATE
                sync_session_id = '',
                value = VALUES(value);

        """.format(provider = cm_info.get("provider"),request_type = REQUEST_TYPE)
        frappe.db.sql(sql,filters)

        # update old value to value 
        sql="""
            update  `tabDaily Property Data` 
            SET old_room_available = total_room_available
            where
                room_type_id in %(room_type_id)s and 
                date between %(start_date)s and %(end_date)s  
        """
        frappe.db.sql(sql,filters)

        if run_commit:
            frappe.db.commit()
 

@frappe.whitelist()
def get_room_availability(property=None,room_types=None, start_date=None,end_date=None):
    if not room_types:
        room_types = frappe.db.get_list(
                'Room Type',
                filters={
                    'property': property,
                    'disabled': 0
                },
                pluck='name'
            )
    sql = """
        select
            CONCAT(DATE_FORMAT(date,'%%y%%m%%d'), room_type_id) AS `key`,
            total_room_available as value,
            coalesce(total_block,0) as total_block ,
            total_occupy
        from `tabDaily Property Data`
        where
            property = %(property)s and 
            date between %(start_date)s and %(end_date)s and 
            room_type_id in %(room_types)s
        
    """
    data = frappe.db.sql(sql,{"property":property, "start_date":start_date, "end_date":end_date,"room_types":room_types},as_dict=1)

    # total data
    sql = """
        select
            CONCAT(DATE_FORMAT(date,'%%y%%m%%d')) AS `key`,
            sum(total_room_available) as value,
            sum(coalesce(total_block,0)) as total_block ,
            sum(total_occupy) as total_occupy,
            sum(total_room) as total_room
        from `tabDaily Property Data`
        where
            property = %(property)s and 
            date between %(start_date)s and %(end_date)s and 
            room_type_id in %(room_types)s
        group by 
            date
        
    """
    total_data = frappe.db.sql(sql,{"property":property, "start_date":start_date, "end_date":end_date,"room_types":room_types},as_dict=1)

 
    # prepare return data
    # sample return data
    # data = {}
    calculate_room_occupancy_include_room_block = frappe.get_cached_value("eDoor Setting",None,"calculate_room_occupancy_include_room_block")
    return {
            **{item['key']: {
                "total_available":item['value'],
                "blocked":item["total_block"],
                "occupy":item["total_occupy"]
                } for item in data}
            ,
            **{item['key']: {
                "total_available":item['value'],
                "blocked":item["total_block"],
                "occupy":item["total_occupy"],
                "occupancy":round( item["total_occupy"] / max(1, item.get("total_room") if calculate_room_occupancy_include_room_block == 1 else item.get("total_room") - item.get("total_block") ) * 100,2)
                } for item in total_data}
            ,
    }
 

@frappe.whitelist()
def get_group_room_availability(filters=None):

    # filter have property, room_types=[], start_date, end_date
    if not filters:
        filters = {
            'property':"ESTC HOTEL 6",
            "room_types":["RT-0001","RT-0002","RT-0003","RT-0004"],
            "start_date":"2026-05-09",
            "end_date":frappe.utils.add_years(frappe.utils.today(), 1)
        }
    total_room_fields = list(range(1,32))
    sql_total_room_fields = ",".join(
        f"MAX(CASE WHEN DAY(d.date) = {day} THEN d.total_room_available END) AS `{day}`"
        for day in total_room_fields
    )
   
    sql = """
        select
            room_type_id,
            date_format(date,'%%b-%%Y') as month_name,
            {total_fields}
        from `tabDaily Property Data` d
        where
            d.property = %(property)s and 
            d.room_type_id in %(room_types)s and 
            d.date between %(start_date)s and %(end_date)s

    """.format(total_fields = sql_total_room_fields)
    return sql
    data = frappe.db.sql(sql,filters,as_dict =1)


    return data
    


@frappe.whitelist()
def resync_differentcial_availability_data(run_commit=True):
    properties = frappe.db.sql("select property   from `tabChannel Manager Integration` where enable = 1",as_dict = 1)
    for p in properties:
        cm_info = get_channal_manager_info(p.get("property"))
        # check can sync data to cm only it enable, price receive from PMS and fist init is done
        if ( cm_info.get("rooms_availability") =="Receive from PMS" 
            and str(cm_info.get("initialized_availability_upload")) == "1"): 
            # add changed data to sync data log
            sql = """
                insert into `tabChannel Manager Sync Data Log` (
                    name,
                    provider,
                    request_type,
                    property,
                    room_type,
                    date,
                    value
                )
                select 
                    name,
                    '{provider}' as provider,
                    '{request_type}' as request_type,
                    property,
                    room_type_id,
                    date,
                    total_room_available as value
                from `tabDaily Property Data` 
                where
                    date >= curdate()  and 
                    coalesce(total_room_available,0) <> coalesce(old_room_available,0)
                ON DUPLICATE KEY UPDATE
                    sync_session_id = '',
                    value = VALUES(value);
            """.format(provider = cm_info.get("provider"),request_type = REQUEST_TYPE)
            frappe.db.sql(sql)
            


            # update old value to value 
            sql="""
                update  `tabDaily Property Data` 
                SET old_room_available = total_room_available
                where
                    date >= CURDATE() and 
                    coalesce(total_room_available,0) <> coalesce(old_room_available,0)
            """
            frappe.db.sql(sql)

    if run_commit:
        frappe.db.commit()

@frappe.whitelist()
def runme():
    resync_availability(recalculate_occupy_data = True)

@frappe.whitelist(methods="POST")
@rate_limit(limit=3, seconds=60)
def resync_availability(data=None,recalculate_occupy_data=False,show_message = True):

    if not data:
        data = {
            "property": "ESTC Hotel 6",
            "date_ranges": [
                {"start_date": "2026-07-01", "end_date": "2026-07-30"}
            ],
            "room_types": ["RT-0001", "RT-0004"],
        }


    cm_info = get_channal_manager_info(data.get("property"))
    if not cm_info:
        frappe.throw("No Channel Manager Integration")
    if cm_info.enable == 0:
        frappe.throw("Channel manager integration is disabled")
    if cm_info.prices_for_accommodation !="Receive from PMS":
        frappe.throw("Availability is not allow to manager in PMS")
     
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
        "property": data.get("property"),
        "room_types":data.get("room_types")
    })

    # check if user want to recalculate occupancy data 
    # then sum occupy and block from temp room occupy and sum to daily property data
    if recalculate_occupy_data:
        force_update_occupy_to_daily_property_data()

    sql = f"""
        insert into `tabChannel Manager Sync Data Log` (
            name,
            provider,
            request_type,
            property,
            room_type,
            date,
            value
        )
        select 
            name,
            '{cm_info.provider}' as provider,
            '{REQUEST_TYPE}' as request_type,
            property,
            room_type_id,
            date,
            if(total_room_available<0,0,total_room_available) as value
        FROM `tabDaily Property Data` rr
        WHERE
            ({date_filters})
            AND rr.property = %(property)s
            AND rr.room_type_id in %(room_types)s 
        ON DUPLICATE KEY UPDATE
            sync_session_id = '',
            value = VALUES(value);

    """ 
 

    frappe.db.sql(sql, filters, as_dict=1)

 
    
    frappe.db.commit()

    if cm_info.get("provider") == "Exely": 
        frappe.enqueue(
            "edoor.channel_managers.exely.availability.sync_room_availability",
            queue="short" if frappe.conf.get("developer_mode") else "channel_manager",
            property=data.get("property")
        )


    if show_message:  
        frappe.msgprint("Room availability update sent successfully. The sync is running in the background, and you will be notified when it is complete.")
    return "Success"

@frappe.whitelist(methods="POST")
@rate_limit(limit=5, seconds=60)
def initialized_availability_upload(property):
    cm_info = get_channal_manager_info(property)
    if not cm_info:
        frappe.throw("No channel manager integration for this property")
    if cm_info.enable == 0:
        frappe.throw("Channel Manager is disable")
    
    if cm_info.initialized_availability_upload == 1:
        frappe.throw("Room availability is already synced with the channel manager. Please use the 'Re-upload' option in the dashboard.")
    

    
    resync_availability({
        "property":property,
        "room_types":[d.get("edoor_room_type") for d in  cm_info.get("room_types") if d.get("edoor_room_type") and d.get("room_type_code")],
        "date_ranges":[
            {"start_date":today(),"end_date": frappe.utils.add_years(today(),1) }
        ]
    },show_message=False)


    frappe.msgprint("We are currently processing your room availability data in the background. Please wait until the upload to the channel manager is completed.")

    # update sync status to cached storage
    for rt in cm_info.room_types:
        cached_key = f"data_initialize_availability_{rt.edoor_room_type}"
        frappe.cache().set_value(cached_key,"In Progress")
        
    # update room availablity sync status in background
    frappe.enqueue("edoor.api.room_availability.update_availability_upload_status",
            queue="long",
            property=property
        )

    return "Room availability is being upload to channel manager"


# this method is use to update availability sync status 
# when first upload data to channel manger
@frappe.whitelist()
def update_availability_upload_status(property = "ESTC HOTEL 6"):   
    from epos_restaurant_2023.custom_socket_client import emit_event
    # we delay 5 second to wait data upload complete to cm
    time.sleep(5)

    cm_info = get_channal_manager_info(property)
    for rt in cm_info.room_types:
        cached_key = f"data_initialize_availability_{rt.edoor_room_type}"
        filter = {
            "property":property,
            "room_type":rt.edoor_room_type,
            "request_type":"Availability update"
        }
        if frappe.db.exists("Channel Manager Sync Data Log",filter):
            frappe.cache().set_value(cached_key,"In Progress")
        else:
            frappe.cache().set_value(cached_key,"Complete")

    if not frappe.db.exists("Channel Manager Sync Data Log",{"property":property,"request_type":"Availability update"}):
        frappe.db.set_value("Channel Manager Integration",cm_info.name,"initialized_availability_upload",1)
        frappe.db.commit()
        # emit socket to client to data upload complete
        emit_event("ChannelManagerUpdate",{
                            "action":"alert_cm_sync_message",
                            "property": property,
                            "status":"Success",
                            "title":"Upload Room Availability",
                            "message": "Upload room availability to channel manager successuflly",
        })

                        
    else:
        frappe.enqueue("edoor.api.room_availability.update_availability_upload_status",
            queue="long",
            property=property
        )


    # socket client listent at 
    # \frontdesk\src\views\channel_managers\channel_manager\components\cm_initialize_step\ComCMInit.vue
    
    emit_event("ChannelManagerUpdate",{
                "action":"update_channel_manager_data_upload_status",
                "property": property,
                "upload_status":get_data_upload_status(property)
    })



def force_update_occupy_to_daily_property_data():
    # update total room 
    sql = """
       UPDATE `tabDaily Property Data` t
        JOIN (
            SELECT
                room_type_id,
                COUNT(*) AS total
            FROM `tabRoom`
            WHERE disabled = 0
            GROUP BY room_type_id
        ) b ON b.room_type_id = t.room_type_id
        SET t.total_room = b.total, 
            old_room_available = total_room_available
        WHERE t.date >= CURDATE()
    """
    frappe.db.sql(sql)
    frappe.db.commit()
  
    # auto fix occupancy and block
    sql = """
       UPDATE `tabDaily Property Data` t
        JOIN (
            select 
                room_type_id,
                date,
                sum(type='Reservation') as occupy,
                sum(type='Block') as block
            from `tabTemp Room Occupy` 
            where 
                date>CURDATE() and 
                is_active = 1
            group by room_type_id,date 
        ) b ON b.room_type_id = t.room_type_id and t.date = b.date
        SET t.total_occupy = b.occupy, 
            t.total_block = b.block,
            t.total_room_available = t.total_room - (b.occupy + b.block)
        WHERE t.date >= CURDATE()
    """
    frappe.db.sql(sql)
    frappe.db.commit()

   
    return ("Success",frappe.utils.now())
    