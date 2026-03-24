import frappe
from frappe.utils import add_to_date,getdate,today
import json
from lxml import etree
from edoor.api.utils import get_room_type_ids
from frappe.model.document import bulk_insert
from edoor.channel_managers.utils import get_channal_manager_info
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
    
    return update_room_availability({'property': 'ESTC HOTEL 6'})

@frappe.whitelist()
def fix_room_availibility():
    properties = frappe.db.sql("select name from `tabBusiness Branch`",as_dict=1)
    for d in properties:
        update_room_availability({
            "property":d.get("name")
        })
    


def update_room_availability(filters=None,run_commit=True):
    filters["room_type_id"] =  filters.get("room_type_id")  or get_room_type_ids(filters.get("property"))

    if not filters.get("room_type_id"):
        return  # or skip query

    filters["start_date"] =  filters.get("start_date")  or today()


    filters["end_date"] =  filters.get("end_date")  or add_to_date(today(),years = 5)
    
    if not "sync_room_available_to_channel_manager" in filters:
        filters["sync_room_available_to_channel_manager"] = True
    
    
    # backup old  value
    backup_room_availability(filters,run_commit=False)

    # sql="""
    #     select 
    #             t.date,
    #             t.room_type_id,
    #             sum(t.type = 'Reservation') as total_occupy,
    #             sum(t.type = 'Block') as total_block
    #         from `tabTemp Room Occupy` t
    #         where
                
    #             t.is_active = 1 and 
    #             t.date between %(start_date)s and %(end_date)s and 
    #             t.room_type_id in %(room_type_id)s  and 
    #             property = %(property)s
    #         group by 
    #             t.room_type_id,
    #             t.date
    # """
    # return frappe.db.sql(sql,filters,as_dict = 1)

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
            d.total_occupy = t.total_occupy, 
            d.total_block = t.total_block, 
            d.total_room_available = d.total_room - (t.total_occupy + t.total_block)
        where
            d.property = %(property)s and 
            d.date between %(start_date)s and %(end_date)s and 
            d.room_type_id in %(room_type_id)s
    """
    frappe.db.sql(sql,filters)
    
 
    

    # get room available change change data save to sync log then sync data to channel manager
    
    cm_info = get_channal_manager_info(filters.get("property"))
    if str(cm_info.get("enable")) == "1":
        room_available_data_changed =  get_room_availabilty_changed_data(filters)
        
        if filters.get("sync_room_available_to_channel_manager") == True and room_available_data_changed:
            # check if provider is exely
            if cm_info.get("provider") == "Exely" and cm_info.get("rooms_availability") == "Receive from PMS":
                frappe.enqueue(
                    "edoor.channel_managers.exely.availability.update_room_availability",
                    queue="channel_manager",
                    property=filters.get("property")
                )

    if run_commit:
        frappe.db.commit()

    



def backup_room_availability(filters=None,run_commit = True):
    filters["room_type_id"] =  filters.get("room_type_id")  or get_room_type_ids(filters.get("property"))
    filters["start_date"] =  filters.get("start_date")  or get_current_working_date()
    filters["end_date"] =  filters.get("end_date")  or add_to_date(today(),years = 5)
    # we run backup and room available and reset room block and occupuy
    sql = """
        update `tabDaily Property Data` 
        set
            total_occupy = 0,
            total_block= 0,
            old_room_available = total_room_available 
        where
            room_type_id in %(room_type_id)s and 
            property = %(property)s and 
            date between %(start_date)s and %(end_date)s  
    """
    frappe.db.sql(sql, filters)
    if run_commit:
        frappe.db.commit()

def get_room_availabilty_changed_data(filters,run_commit=True):
    sql="""
        select 
            property,
            room_type_id,
            date,
            total_room_available
        from `tabDaily Property Data` 
        where
            old_room_available <> total_room_available and 
            room_type_id in %(room_type_id)s and
            property = %(property)s and 
            date between %(start_date)s and %(end_date)s  and 
            date>= CURDATE()
    """
    data = frappe.db.sql(sql, filters,as_dict=1)
    # frappe.throw(str(data))
  
    
    if data:
        add_data_to_log(data)
      

        if run_commit:
            frappe.db.commit()

    return data

def add_data_to_log(data):
    # clean old data queue 
    sql = "delete from `tabChannel Manager Sync Data Log` where date in %(date)s and room_type in %(room_type_id)s and request_type='OTA_HotelAvailNotifRQ'"
    frappe.db.sql(sql, {
        "room_type_id": set([d.get("room_type_id") for d in data]),
        "date": set([d.get("date") for d in data])
    })

    def get_data():

        for d in data:
            doc = doc = frappe.new_doc("Channel Manager Sync Data Log")
            doc.name = frappe.generate_hash(length=10)
            doc.property = d.get("property")
            doc.provider = "Exely"
            doc.request_type = "OTA_HotelAvailNotifRQ"
            doc.room_type = d.get("room_type_id")
            doc.date = d.get("date")
            doc.value =   d.get("total_room_available")


            yield doc

    
    

    bulk_insert("Channel Manager Sync Data Log",get_data() , chunk_size=10000)





    


@frappe.whitelist()
def get_room_availability(property, start_date,end_date):
    sql = """
        select
            room_type_id,
            date,
            total_room_available as value,
            stop_sale
        from `tabDaily Property Data`
        where
            property = %(property)s and 
            date between %(start_date)s and %(end_date)s
        
    """
    data = frappe.db.sql(sql,{"property":property, "start_date":start_date, "end_date":end_date},as_dict=1)

    # check if date not exist in daily property data then add future date to data get room total from room_type
    return data

@frappe.whitelist(methods="POST")
def update_room_availability_restriction(property,stop_sale,data):
    # status = 1 (Stop Sale), 0 open sale
    # step 
    #1 backup old stop sale
    # 2 update stop sale
    # 3 get change data and add to sync data log
    # 4 run schedule task update availability restriction

    filters = {
        "property":property,
        "stop_sale": stop_sale,
        "start_date": min([getdate(d.get("date") for d in data)]),
        "end_date": max([getdate(d.get("date") for d in data)]),
        "room_type_id": set([d.get("room_type") for d in data]),
        "dates": set([d.get("date") for d in data])
    }
     

    # backup old current stop sale update to old stop sale field
    sql="""update `tabDaily Property Data` set old_stop_sale = stop_sale 
         where
                property = %(property)s and 
                room_type_id in %(room_type_id)s and 
                date in %(dates)s 
        """
    frappe.db.sql(sql,filters)

    # update stop sale value
    sql = """update `tabDaily Property Data`
             set stop_sale=%(stop_sale)s
             where
                property = %(property)s and 
                room_type_id in %(room_type_id)s and 
                date in %(dates)s
    """
    frappe.db.sql(sql,filters)

    # check if any data change then 
    
    frappe.db.commit()

    return "Success"

@frappe.whitelist(methods="POST")
def toggle_update_availability_restriction(data):
    import time
    time.sleep(.5)
    sql="update `tabDaily Property Data` set stop_sale=%(stop_sale)s, old_stop_sale =%(stop_sale)s where property = %(property)s and room_type_id= %(room_type_id)s and date=%(date)s"
    frappe.db.sql(sql,data)
    
    # add data to sync queue

    
    frappe.db.commit()

    return "Success"





 

