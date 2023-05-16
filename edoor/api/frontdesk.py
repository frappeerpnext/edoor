import frappe
import datetime

# Get the current date

@frappe.whitelist()
def get_dashboard_data(property = None,date = None):
    
    data = frappe.db.sql("select max(posting_date) as date from `tabWorking Day` limit 1",as_dict=1)

    working_date =  datetime.date.today()
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
        "arrival":10,
        "arrival_remaining":5,
        "departure":7,
        "departure_remaining":8,
        "pick_up":5,
        "drop_off":5,
        "housekeeping_status":[
            {
                "status":"Vacant Clean",
                "total":5,
                "icon":"",
                "color":""
            }
        ]
    }


@frappe.whitelist()
def get_logged_user():
    data = frappe.get_doc('User',frappe.session.user)
    return {
        "name":data.name,
        "full_name":data.full_name,
        "role":data.role_profile_name,
        "phone_number":data.phone,
        "photo":data.user_image
    }

@frappe.whitelist()
def get_room_chart_data(property,group_by,start_date,end_date):

    


    return []
