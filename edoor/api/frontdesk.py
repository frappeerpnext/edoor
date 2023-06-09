import secrets
from edoor.api.utils import get_date_range
import frappe
import datetime
import random
from datetime import datetime
from py_linq import Enumerable
from dateutil.relativedelta import relativedelta
# Get the current date

@frappe.whitelist()
def get_dashboard_data(property = None,date = None):
    data = frappe.db.sql("select max(posting_date) as date from `tabWorking Day` limit 1",as_dict=1)
    working_date =  datetime.now()
    if data:
        working_date = data[0]["date"]

    if not date:
        date = working_date 

    # get total_room
    sql = "select count(name) as total from `tabRoom` where property='{}'".format(property)
    data = frappe.db.sql(sql, as_dict=1)
    total_room = 0
    if data:
        total_room = data[0]["total"] or 0

    #get total room occupy
     
    

    return {
        "working_date":working_date,
        "total_room":total_room,
        "total_room_occupy":25,
        "total_room_vacant": 10,
        "arrival":10,
        "arrival_remaining":5,
        "departure":7,
        "departure_remaining":8,
        "pick_up":5,
        "drop_off":5,
         "unassign_room":10,
        "stay_over":8
        
    }

@frappe.whitelist()
def get_house_keeping_status(property):
    #get house keeping status
    hk_data = frappe.db.get_list("Housekeeping Status",fields=["*"],  order_by='sort_order asc')
    housekeeping_status = []
    for d in hk_data:
        total  = frappe.db.sql("select count(name) as total from `tabRoom` where property='{}' and housekeeping_status='{}'".format(property,d.name),as_dict=1)[0]["total"] or 0

        
        housekeeping_status.append({
            "status":d.name,
            "color":d.status_color,
            "icon":d.icon,
            "total":total
        })
    return housekeeping_status

@frappe.whitelist()
def get_mtd_room_occupany(property):

    now = datetime.now()
    start_date = datetime(now.year, now.month, 1)
    
    end_date = now + relativedelta(day=1, months=1, days=-1)
    sql = "select date from `tabDates` where date between cast('{}' as date) and cast('{}' as date)"
    sql = sql.format(start_date, end_date)
    data = frappe.db.sql(sql,as_dict=1)

    for d in data:
        d.occupancy = random.randint(10, 100)
    return data



@frappe.whitelist()
def get_edoor_setting(property = None):
    currency = frappe.db.get_default("currency")
    housekeeping_status = frappe.get_list("Housekeeping Status", fields=['status','status_color','icon','sort_order'],  order_by='sort_order asc')
    reservation_status = frappe.get_list("Reservation Status", fields=['reservation_status','name','color','is_active_reservation','show_in_reservation_list','show_in_room_chart','sort_order'],  order_by='sort_order asc')
    
    
    epos_setting = frappe.get_doc('ePOS Settings')
    
    edoor_setting = {
        "backend_port":epos_setting.backend_port,
        "currency":{
            "name":currency,
            "precision":  frappe.db.get_default("currency_precision")
        },
        "housekeeping_status":housekeeping_status,
        'reservation_status':reservation_status
    }
    
    user = get_logged_user()
    if not frappe.db.exists("Business Branch", property):
        return {"user":user,"property":"Invalid Property", "edoor_setting":edoor_setting}
     

    working_day = None 
    if property:
        working_day = get_working_day(property)
    else:
        if len(user["property"])==1:
             working_day = get_working_day(user["property"][0]["name"])

    property = frappe.get_doc("Business Branch", property)
    
    if  not property.default_pos_profile:
        frappe.throw("Please assign default pos profile to your current property")


    edoor_setting["property"] = {
        "name":property.name,
        "property_code":property.property_code,
        "province":property.province,
        "address_en":property.address_en,
        "address_kh":property.address_kh,
        "phone_number_1":property.phone_number_1,
        "phone_number_2":property.phone_number_1,
        "pos_profile":property.default_pos_profile
    }

    pos_profile = frappe.get_doc("POS Profile",property.default_pos_profile)
    
    edoor_setting["pos_profile"] = {
        "name":pos_profile.name,
        "stock_location":pos_profile.stock_location
    }
    pos_config = frappe.get_doc("POS Config", pos_profile.pos_config)
    edoor_setting["payment_type"] = pos_config.payment_type
    

    return {
        "user":get_logged_user(),
        "working_day": working_day,
        "edoor_setting":edoor_setting
    }

@frappe.whitelist()
def get_logged_user():
    data = frappe.get_doc('User',frappe.session.user)
    property = frappe.get_list("Business Branch",fields=["name","property_code","province","email","phone_number_1","photo"])
    return {
        "name":data.name,
        "full_name":data.full_name,
        "role":data.role_profile_name,
        "phone_number":data.phone,
        "photo":data.user_image,
        "property":property
    }

@frappe.whitelist()
def get_room_chart_data(property,group_by,start_date,end_date):

    


    return []


@frappe.whitelist()
def get_working_day(property = ''):
    working_day = frappe.db.sql("select  posting_date as date,name,pos_profile from `tabWorking Day` where business_branch = '{0}' order by creation desc limit 1".format(property),as_dict=1)
    data = frappe.db.sql("select creation, shift_name,name from `tabCashier Shift` where business_branch = '{}' and working_day='{}' and pos_profile='{}' ORDER BY creation desc limit 1".format(property,working_day[0]["name"],working_day[0]["pos_profile"]),as_dict=1)
    cashier_shift = None
    if data:
        cashier_shift = data[0]
        
    return {
        "date_working_day": working_day[0]["date"],
        "name":working_day[0]["name"],
        "cashier_shift":cashier_shift
    }



    
@frappe.whitelist()
def get_room_chart_resource(property = '', room_type = '', building = '', view_type='room_type'):
    resources = []

    if view_type == 'room_type':
        sql = """
            select 
            name,
            room_type,
            sort_order,
            alias
            from 
                `tabRoom Type` 
            where property='{}'
            
        """
        sql=sql.format(property)
        room_types = frappe.db.sql(sql, as_dict=1)
        for t in room_types:
            rooms = frappe.db.sql("select name as id, room_number as title, sort_order, housekeeping_status,status_color,housekeeping_icon, 'room' as type from `tabRoom` where room_type_id='{}' and disabled = 0 order by room_number".format(t["name"]),as_dict=1)
            resources.append({
                "id":t["name"],
                "title":t["room_type"],
                "sort_order":t["sort_order"],
                "alias":t["alias"],
                "type":"room_type",
                "children": rooms
            })
    else:
        resources = frappe.db.sql("select name as id,room_type,room_type_alias, room_type_id, room_number as title,sort_order, housekeeping_status,status_color,housekeeping_icon, 'room' as type from `tabRoom` where disabled = 0 order by room_number",as_dict=1)
    
    resources.append({
        "id": "vacant_room",
        "title": "Vacant Room",
        "sort_order":1000
    })
    
    resources.append({
        "id": "occupany",
        "title": "Occupancy",
        "sort_order":1001
    })
  
    resources.append({
        "id": "out_of_order",
        "title": "Out of Order",
        "sort_order":1002
    })
    
    resources.append({
        "id": "arrival_departure",
        "title": "Arrival/Departure",
        "sort_order":1003
    })
    resources.append({
        "id": "pax",
        "title": "PAX",
        "sort_order":1004
    })


    return resources
 


@frappe.whitelist()
def get_room_chart_calendar_event(property, start=None,end=None):
    

    events = []
    sql = """
        select 
            name as id, 
            room_id as resourceId,
            room_number,
            concat(start_date,'T',start_time) as start ,
            concat(end_date,'T',end_time) as end,
            guest_name as title,
            status_color as color,
            adult,
            child,
            pax,
            reference_number,
            reservation,
            parent as reservation_stay,
            'stay' as type,
            1 as editable

        from 
            `tabReservation Stay Room` 
        where 
            show_in_room_chart = 1   and 
            name in (
                select distinct stay_room_id from `tabRoom Occupy` where date between '{}' and '{}' 
            ) and 
            property = '{}'

    """
    sql = sql.format(
            datetime.strptime(start, "%Y-%m-%dT%H:%M:%S.%fZ").strftime('%Y-%m-%d'), 
            datetime.strptime(end, "%Y-%m-%dT%H:%M:%S.%fZ").strftime('%Y-%m-%d')
            ,property)
  
    
    data = frappe.db.sql(sql, as_dict=1)
    for d in data:
        d["editable"]  = d["editable"] ==1
    events = data
   

    # check if room chart view is group by room type then add event to room type resource
    room_type_events = get_calendar_event_for_room_type_resource(start=start,end=end,property=property)
    events = events + room_type_events

    #get event from room block
    events = events +  get_room_block_event(start,end,property)
    

    return events


@frappe.whitelist()
def get_room_block_event(start,end,property):
    sql = """
        select 
            name as id, 
            room_id as resourceId,
            room_number,
            concat(start_date,'T00:00:00') as start ,
            concat(end_date,'T23:00:00') as end,
            'Room Block' as title,
            status_color as color,
            reason,
            'room_block' as type,
            0 as editable

        from 
            `tabRoom Block` 
        where 
            docstatus = 1   and 
            name in (
                select distinct stay_room_id from `tabRoom Occupy` where date between '{}' and '{}' 
            ) and 
            property = '{}'

    """
    sql = sql.format(
            datetime.strptime(start, "%Y-%m-%dT%H:%M:%S.%fZ").strftime('%Y-%m-%d'), 
            datetime.strptime(end, "%Y-%m-%dT%H:%M:%S.%fZ").strftime('%Y-%m-%d')
            ,property)
  
    data = frappe.db.sql(sql, as_dict=1)
    
    for d in data:
        d["editable"] = d["editable"]  == 1
    
    return data

@frappe.whitelist()
def get_calendar_event_for_room_type_resource(start,end,property):
    """
        There are 2 place to get room type resource event and other resource event
        1. From temp room occupy for current and future date 
        2. From room type Daily Property Data for past date

    """
    events = []
    working_day = get_working_day(property=property)
    dates = get_date_range( datetime.strptime(start, "%Y-%m-%dT%H:%M:%S.%fZ"),datetime.strptime(end, "%Y-%m-%dT%H:%M:%S.%fZ"),False)
    future_dates =  [d for d in dates if d.date() >= working_day["date_working_day"]]
    past_dates =  [d for d in dates if d.date() < working_day["date_working_day"]]
    
    #1. get date for future date by from temp room occupy
    if future_dates:
        #get all room type with total room
        sql = "select room_type_id, room_type, count(name) as total_room from `tabRoom` where property='{}' and disabled = 0 group by room_type_id, room_type".format(property)
        room_type_data = frappe.db.sql(sql,as_dict=1)
    

         
        sql = """
                select 
                    room_type_id, 
                    date, 
                    sum(if(type='Reservation',1,0)) as total_occupy,
                    sum(if(type='Block',1,0)) as total_block,
                    sum(if(coalesce(room_id,'')='',1,0)) as total_unassign_room,
                    sum(pax) as pax
                from 
                    `tabTemp Room Occupy` 
                where 
                    property='{}' and 
                    date between '{}' and '{}' 
                group by 
                    room_type_id, 
                    date 
            """
        sql = sql.format(
            property,
            future_dates[0].strftime('%Y-%m-%d'),
            future_dates[len(future_dates)-1].strftime('%Y-%m-%d'),
        )
        temp_occupy_data = frappe.db.sql(sql,as_dict=1)
        #get temp room occupy 
        
        for d in room_type_data:
            for x in future_dates:
                events.append(      
                {
                    "resourceId": d["room_type_id"],
                    "start": "{}T00:00:00.000000".format(x.strftime('%Y-%m-%d')),
                    "end": "{}T12:00:00.000000".format(x.strftime('%Y-%m-%d')),
                    "title": d["total_room"] - Enumerable(temp_occupy_data).where(lambda r:r.room_type_id==d["room_type_id"] and r.date.strftime('%Y-%m-%d') == x.strftime('%Y-%m-%d')).sum(lambda r: r.total_occupy or 0),
                    "color": "#29CD42",
                    "type":"available_room"
                })

                #add event for unssign room
                events.append(      
                {
                    "resourceId": d["room_type_id"],
                    "start": "{}T12:00:00.000000".format(x.strftime('%Y-%m-%d')),
                    "end": "{}T0:00:00.000000".format(x.strftime('%Y-%m-%d')),
                    "title":  Enumerable(temp_occupy_data).where(lambda r:r.room_type_id==d["room_type_id"] and r.date.strftime('%Y-%m-%d') == x.strftime('%Y-%m-%d')).sum(lambda r: r.total_unassign_room or 0),
                    "color": "#cccccc",
                    "type":"unassign_room"
                })

        #add event for Vacant Room 
        total_room = Enumerable(room_type_data).sum(lambda r:r.total_room)

        future_arrival_data = get_future_arrival_data(
                                property,
                                future_dates[0].strftime('%Y-%m-%d'),
                                future_dates[len(future_dates)-1].strftime('%Y-%m-%d')
                            )
        
        future_departure_data = get_future_departure_data(
                                property,
                                future_dates[0].strftime('%Y-%m-%d'),
                                future_dates[len(future_dates)-1].strftime('%Y-%m-%d')
                            )
        


        for x in future_dates:
                
                events.append(      
                {
                    "resourceId": "vacant_room",
                    "start": "{}T00:00:00.000000".format(x.strftime('%Y-%m-%d')),
                    "end": "{}T23:59:00.000000".format(x.strftime('%Y-%m-%d')),
                    "title": total_room - Enumerable(temp_occupy_data).where(lambda r:r.date.strftime('%Y-%m-%d') == x.strftime('%Y-%m-%d')).sum(lambda r: r.total_occupy or 0),
                    "color": "#ccce45",
                    "type":"vacant_room"
                })

                #add event for room occupy
                events.append(      
                {
                    "resourceId": "occupany",
                    "start": "{}T00:00:00.000000".format(x.strftime('%Y-%m-%d')),
                    "end": "{}T12:00:00.000000".format(x.strftime('%Y-%m-%d')),
                    "title":  Enumerable(temp_occupy_data).where(lambda r:r.date.strftime('%Y-%m-%d') == x.strftime('%Y-%m-%d')).sum(lambda r: r.total_occupy or 0),
                    "color": "#ccce45",
                    "type":"occupany"
                })
                #add event for room occupy percentage
                events.append(      
                {
                    "resourceId": "occupany",
                    "start": "{}T12:00:00.000000".format(x.strftime('%Y-%m-%d')),
                    "end": "{}T23:59:00.000000".format(x.strftime('%Y-%m-%d')),
                    "title":  str.format("{:.0%}", Enumerable(temp_occupy_data).where(lambda r:r.date.strftime('%Y-%m-%d') == x.strftime('%Y-%m-%d')).sum(lambda r: r.total_occupy or 0) / total_room) ,
                    "color": "#ddce45",
                    "type":"occupany"
                })
                
                #add event for total block
                total_block =Enumerable(temp_occupy_data).where(lambda r:r.date.strftime('%Y-%m-%d') == x.strftime('%Y-%m-%d')).sum(lambda r: r.total_block or 0) 
                events.append(      
                {
                    "resourceId": "out_of_order",
                    "start": "{}T00:00:00.000000".format(x.strftime('%Y-%m-%d')),
                    "end": "{}T23:59:00.000000".format(x.strftime('%Y-%m-%d')),
                    "title": total_block,
                    "color": "red" if total_block>0 else '#ccc',
                    "type":"out_of_order"
                })

                #append arrival data to event for future date
                events.append(      
                {
                    "resourceId": "arrival_departure",
                    "start": "{}T12:00:00.000000".format(x.strftime('%Y-%m-%d')),
                    "end": "{}T23:59:00.000000".format(x.strftime('%Y-%m-%d')),
                    "title": Enumerable(future_arrival_data).where(lambda r:r.date.strftime('%Y-%m-%d') == x.strftime('%Y-%m-%d')).sum(lambda r: r.total_room or 0) ,
                    "color": "blue",
                    "type":"arrival"
                })
                
                #append depareture data to event for future date
                events.append(      
                {
                    "resourceId": "arrival_departure",
                    "start": "{}T00:00:00.000000".format(x.strftime('%Y-%m-%d')),
                    "end": "{}T12:00:00.000000".format(x.strftime('%Y-%m-%d')),
                    "title": Enumerable(future_departure_data).where(lambda r:r.date.strftime('%Y-%m-%d') == x.strftime('%Y-%m-%d')).sum(lambda r: r.total_room or 0) ,
                    "color": "teal",
                    "type":"departure"
                })

                #add event for total pax
                events.append(      
                {
                    "resourceId": "pax",
                    "start": "{}T00:00:00.000000".format(x.strftime('%Y-%m-%d')),
                    "end": "{}T23:59:00.000000".format(x.strftime('%Y-%m-%d')),
                    "title":  Enumerable(temp_occupy_data).where(lambda r:r.date.strftime('%Y-%m-%d') == x.strftime('%Y-%m-%d')).sum(lambda r: r.pax or 0),
                    "color": "green",
                    "type":"pax"
                })
                
      
        


    return events

def get_future_arrival_data(property,start,end):
    #get arrival and departure event
    sql = """
            select 
                arrival_date as date,
                count(name) as total_room
            from `tabReservation Stay` 
            where 
                is_active_reservation = 1 and 
                property = '{}' and 
                arrival_date between '{}' and '{}'  
            group by
                arrival_date

        """
    sql = sql.format(
            property, 
            start,
            end
        )
    
def get_future_departure_data(property,start,end):
    #get arrival and departure event
    sql = """
            select 
                departure_date as date,
                count(name) as total_room
            from `tabReservation Stay` 
            where 
                is_active_reservation = 1 and 
                property = '{}' and 
                departure_date between '{}' and '{}'  
            group by
                departure_date

        """
    sql = sql.format(
            property, 
            start,
            end
        )
    
 

    
    return  frappe.db.sql(sql,as_dict=1)
    

    
    
