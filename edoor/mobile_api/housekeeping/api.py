import frappe
from edoor.api import frontdesk
from frappe.desk import reportview

@frappe.whitelist()
def get_dashboard_data(property=None,working_date=None):
    if not property:
        property = "ESTC  & HOTEL's"
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
    fields = ["name","owner","creation","modified","modified_by","_assign","posting_date","description","photo","work_order_type","work_order_status"]
    order_by = "modified desc"
    limit_page_length = 20
    result = frappe.db.get_list("Work Order", fields = fields,  filters = filters, limit_page_length =  limit_page_length, order_by=order_by)
    return result

@frappe.whitelist()
def get_user_work_order(property):
 
    filters = [["property", "=", property],["_assign","like","%{}%".format(frappe.session.user)]]
    fields = ["name","owner","creation","modified","modified_by","_assign","posting_date","description","photo","work_order_type","work_order_status"]
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