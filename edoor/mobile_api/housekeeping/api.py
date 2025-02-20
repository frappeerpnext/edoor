import frappe
from edoor.api import frontdesk
from frappe.desk import reportview
import time
@frappe.whitelist()
def get_dashboard_data(property=None,working_date=None):
    
    if not property:
        property = "ESTC Hotel"
    if not working_date:
        working_date = '2024-10-28'


    data = frontdesk.get_dashboard_data(
        property=property,
        date=working_date
    )
    current_working_day = frontdesk.get_working_day(property)

    room_status = frontdesk.get_house_keeping_status(property=property, working_day=current_working_day.get("date_working_day"))
    my_task = get_user_work_order(property)

    if my_task:
        user_info = get_users_info( merge_assign_values([d.get("_assign") for d in my_task if d.get("_assign")]))
    return {
        "summary":data,
        "room_status":room_status,
        "my_tasks":my_task,
        "all_tasks": get_recent_work_order(property)
    }

@frappe.whitelist()
def get_recent_work_order(property):

    filters = [["property", "=", property]]
    fields = ["name","owner","creation","modified","modified_by","_assign","posting_date","description","photo","work_order_type","work_order_status","location"]
    order_by = "modified desc"
    limit_page_length = 20
    result = frappe.db.get_list("Work Order", fields = fields,  filters = filters, limit_page_length =  limit_page_length, order_by=order_by)
    return result

@frappe.whitelist()
def get_user_work_order(property):
 
    filters = [["property", "=", property],["_assign","like","%{}%".format(frappe.session.user)]]
    fields = ["name","owner","creation","modified","modified_by","_assign","posting_date","description","photo","work_order_type","work_order_status","location"]
    order_by = "modified desc"
    limit_page_length = 20
    result = frappe.db.get_list("Work Order", fields = fields,  filters = filters, limit_page_length =  limit_page_length, order_by=order_by)
 
    return result


def get_users_info(users):
    sql = "select name, full_name, user_image as photo from `tabUser` where name in %(users)s"
    return frappe.db.sql(sql,{"users":users},as_dict=1)

def merge_assign_values(data):
    import ast
    # Initialize an empty set to hold unique values
    merged_assign = set()

    # Iterate through each dictionary in the list
    for item in data:
        # Parse the _assign string as a Python list (it's stored as a string representation of a list)
        assign_values = ast.literal_eval(item)

        # Add the parsed values to the set (sets automatically handle uniqueness)
        merged_assign.update(assign_values)
    
    # Return the list of unique assign values
    return list(merged_assign)


@frappe.whitelist()
def test_get_room():
    return get_room_list(
        property="ESTC Hotel",
        date='2025-01-27'
    )

   
@frappe.whitelist(methods="POST")
def get_room_list(property,
                  date,room_type=None
                  ,room_status=None, 
                  floor=None,
                  building=None):
    
  

    sql= """
        select 
            r.name,
            r.room_number,
            r.room_type_id,
            r.room_type,
            r.floor,
            f.alias as floor_alias,
            r.building,
            r.room_status,
            r.housekeeping_status_code,
            r.housekeeping_icon,
            r.status_color
        from `tabRoom` r 
        inner join `tabFloor` as f on f.name = r.floor
        where
            r.disabled = 0 and 
            r.property = %(property)s 
            
            
    """
    if room_type:
        if isinstance(room_type, list):
            sql = sql + " and room_type_id in %(room_type)s"
        else:
            sql = sql + " and room_type_id = %(room_type)s"
    if floor:
        if isinstance(floor, list):
            sql = sql + " and floor in %(floor)s"
        else:
            sql = sql + " and floor = %(floor)s"
            
    if building:
        if isinstance(building, list):
            sql = sql + " and building in %(building)s"
        else:
            sql = sql + " and building = %(building)s"
    
    if room_status:
        if isinstance(room_status, list):
            sql = sql + " and room_status in %(room_status)s"
        else:
            sql = sql + " and room_status = %(room_status)s"
            
    # house keeper

    
    sql = sql  + " order by r.sort_order,r.room_number"
    
    
    room_data = frappe.db.sql(sql,{"property":property},as_dict = 1)

    # get occupy and update to room
    occopy_data = get_occupy_data([d.get("name") for d in room_data],date)

    work_order_employee = get_room_assign_user(property=property,date = date)
   
    room_has_work_order = get_room_has_work_order(property,date)
    room_block_data =[]
    
    
    if [d.get("name") for d in room_data if d.get("room_status") == "Room Block"]:
        room_block_data = get_room_block_date(property=property,rooms= set([d.get("name") for d in room_data if d.get("room_status") == "Room Block"]))
    for r in room_data:
        # has work order 
        r["has_work_order"] = len([d for d in room_has_work_order if d.get("room") == r.get("name")])>0
        # employee 
        r["employee"] = [d for d in work_order_employee if d.get("room") == r.get("name")]
        stays =  [d for d in occopy_data if d.get("room_id") == r["name"]]
        
        # update block start date and end_date
        if room_block_data:
            room_block = [d for d in room_block_data if d.get("room_id") == r.get("name")]
            if room_block:
                room_block = room_block[0]
                r["block_start_date"] = room_block.get("start_date")
                r["block_end_date"] = room_block.get("end_date")
        
        r["is_arrival"] = len([d for d in stays if d.get("is_arrival")==1])>0
        r["is_stay_over"] = len([d for d in stays if d.get("is_stay_over")==1])>0
        r["is_departure"] = len([d for d in stays if d.get("is_departure")==1])>0
        # show in house guest as priority
        stay = [d for d in stays if d.get("reservation_status") == "In-house"]
        if not stay:
            stay  = [d for d in stays if d.get("reservation_status") == "Reserved"]

        if stay:
            stay = stay[0]
            r["reservation_status_color"] = stay.get("reservation_status_color")
            r["reservation_color_code"] = stay.get("reservation_color_code")
            r["reservation_color"] = stay.get("reservation_color")
            r["group_color"] = stay.get("group_color")
            r["adult"] = stay.get("adult")
            r["child"] = stay.get("child")
            r["guest_name"] = stay.get("guest_name")
            
 
    return room_data

def get_room_block_date(property,rooms):
    sql = """
        select 
            room_id,
            start_date,
            end_date
        from `tabRoom Block` 
        where
            property = %(property)s and 
            room_id in %(rooms)s and 
            is_unblock = 0
            
    """
    return frappe.db.sql(sql,{"property":property,"rooms":rooms},as_dict = 1)

def get_occupy_data(room_ids,date):
    sql = """
        select 
            a.room_id,
            a.is_arrival,
            a.is_departure,
            a.is_stay_over,
            a.adult,
            a.child,
            a.reservation_status,
            st.reservation_color_code,
            st.reservation_color,
            st.status_color as reservation_status_color,
            st.group_color,
            a.guest_name
        from `tabRoom Occupy` a
        inner join `tabReservation Stay`  st on st.name = a.reservation_stay
        where
            a.room_id in %(room_ids)s and 
            a.is_active_reservation = 1 and
            a.date = %(date)s and 
            a.reservation_status in ('In-house','Reserved')
    """
    

    data = frappe.db.sql(sql,{"room_ids":room_ids,"date":date},as_dict = 1)

    return data



def get_room_has_work_order(property,date):
    sql = "select distinct room from `tabWork Order` where property=%(property)s and workorder_date=%(date)s and coalesce(room,'')!='' and work_order_status not in ('Closed','Cancelled')" 
    return frappe.db.sql(sql,{"property":property,"date":date},as_dict =1)

def get_room_assign_user(property,date):
  
    sql = """
        select 
            b.room,
            a.employee, 
            a.employee_name
        from `tabWork Order Employee` a 
            inner join `tabWork Order` b on b.name = a.parent
        where 
            b.property=%(property)s and 
            b.workorder_date=%(date)s and 
            b.work_order_status not in ('Closed','Cancelled') and 
            coalesce(b.room,'') !=''
    """
    work_order_data = frappe.db.sql(sql,{
        "property":property,
        "date":date
    },as_dict = 1)
    
    return work_order_data

    
    