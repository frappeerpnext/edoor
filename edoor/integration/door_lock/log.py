import frappe
def create_log(data):
    doc =frappe.get_doc( {
        "doctype":"Door Lock Log",
        **data
    })

    doc.insert()
    
    frappe.db.commit()
    return doc
    

    
def add_issue_card(data):
    doc =frappe.get_doc( {
        "doctype":"Door Lock Issue Card",
        **data
    })

    doc.insert()
    return doc

@frappe.whitelist()
def get_reservation_stay_for_group_write_card(property,reservation):
    sql ="select name, guest,guest_name, arrival_date,departure_date, departure_time,reservation_status,status_color from `tabReservation Stay` where reservation = %(reservation)s and property = %(property)s and reservation_status in ('Reserved','In-house')"  
    data = frappe.db.sql(sql,{"property":property, "reservation":reservation},as_dict = 1)
    stay_room_data = frappe.db.sql(
        "select parent, room_id,room_number from `tabReservation Stay Room` where parent in %(names)s",
        {"names":[d.get("name") for d in data]},
        as_dict = 1
    )
    # issue card_data
    issue_card_data = frappe.db.sql(
        "select a.reservation_stay, a.room, b.card_type,a.expire,a.status from `tabDoor Lock Issue Card` a inner join `tabDoor Lock Card Type` b on b.name = a.card_type where a.reservation_stay in %(names)s order by a.creation desc",
        {"names":[d.get("name") for d in data]},
        as_dict = 1
    )

    for stay in data:
        stay["stays"] = [d for d in stay_room_data if d.get("parent") == stay["name"] ]
        issue_card = next((r for r in issue_card_data if r.get("reservation_stay") ==  stay.get("name")), None)
        stay["issue_card"] = issue_card
    
    # 
    return data
