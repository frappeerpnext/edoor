import frappe

@frappe.whitelist(methods="POST")
def update_housekeeping_status(rooms, status):
    doc = frappe.get_doc("Housekeeping Status", status)
    for r in rooms.split(","):
       frappe.db.set_value("Room", r,"housekeeping_status", status)
       frappe.db.set_value("Room", r,"status_color", doc.status_color)


    frappe.db.commit()
    return "Ok"

@frappe.whitelist(methods="POST")
def update_housekeeper(rooms, housekeeper):
    for r in rooms.split(","):
       frappe.db.set_value("Room", r,"housekeeper", housekeeper)

    frappe.db.commit()
    return "Ok"
