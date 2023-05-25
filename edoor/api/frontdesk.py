import frappe
import datetime
import random
from datetime import datetime
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
        "housekeeping_status":housekeeping_status,
        "stay_over":8
        
    }

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
    user = get_logged_user()

    working_day = None 
    if property:
        working_day = get_working_day(property)
    else:
        if len(user["property"])==1:
             working_day = get_working_day(user["property"][0]["name"])

    return {"user":get_logged_user(), "working_day": working_day}
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
    working_day = frappe.db.sql("select  posting_date as date,name from `tabWorking Day` where business_branch = '{0}' order by creation desc limit 1".format(property),as_dict=1)
    data = frappe.db.sql("select creation, shift_name,name from `tabCashier Shift` where business_branch = '{0}' ORDER BY creation desc limit 1".format(property),as_dict=1)
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
            
        """
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
        "id": "z1_vacant_room",
        "title": "Vacant Room",
    })
    
    resources.append({
        "id": "z2_occupany",
        "title": "Occupancy",
    })
  
    resources.append({
        "id": "z3_out_of_order",
        "title": "Out of Order",
    })
    
    resources.append({
        "id": "z4_arrival_departure",
        "title": "Arrival/Departure",
    })
    resources.append({
        "id": "z5_arrival_departure",
        "title": "PAX",
    })


    return resources
 

@frappe.whitelist()
def get_room_chart_calendar_event(start=None,end=None):
    
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
            parent as reservation_stay

        from 
            `tabReservation Stay Room` 
        where 
            show_in_room_chart = 1  


    """
    # and
    #         start_date between cast('{}' as date) and cast('{}' as date)  

    #sql = sql.format(start, end)

    data = frappe.db.sql(sql, as_dict=1)
    
    events = data
    events.append(   {
            "id": "36e6xx8c4236",
            "resourceId": "RT-0001",
            "room_number": "602",
            "start": "2023-05-24T00:00:00.000000",
            "end": "2023-05-24T12:00:00.000000",
            "title": "10",
            "color": "#29CD42",
            "adult": 1,
            "child": 0,
            "pax": 0,
            "reservation": "RS2023-0076"
        })
    events.append(   {
            "id": "36e6xx8c4236",
            "resourceId": "RT-0001",
            "room_number": "602",
            "start": "2023-05-24T12:00:00.000000",
            "end": "2023-05-25T00:00:00.000000",
            "title": "10",
            "color": "red",
            "adult": 1,
            "child": 0,
            "pax": 0,
            "reservation": "RS2023-0076"
        })
    #get event from room block

    return events
    return [ 
        { "id": '1', "resourceId": 'a', "start": '2023-05-01T12:00', "end": '2023-05-20T07:00', "title": 'event 1' },
        { "id": '2', "resourceId": 'b', "start": '2023-05-06T12:00', "end": '2023-05-20T22:00', "title": 'event 2' },
        { "id": '3', "resourceId": 'c', "start": '2023-05-06T12:00', "end": '2023-05-20T18:00', "title": 'event 3' }
    ]
