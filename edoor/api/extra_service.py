import frappe


@frappe.whitelist(methods="POST")
def initialized_extra_service_upload(property="ESTC HOTEL 6"):
    frappe.msgprint("Extra service upload is running in the background. You will be notified once it is complete.")
    return "success"
@frappe.whitelist(methods="POST")
def mark_as_first_upload_complete(property):
    doc = frappe.get_doc("Channel Manager Integration",property)
    doc.initialized_service_upload = 1
    doc.save(ignore_permissions=True)
    return "Success"    

