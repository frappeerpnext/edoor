import frappe
def after_migrate():
    comment_doc = [{
        "subject": "Change Value",
        "custom_audit_trail_type":"Updated",
        "custom_icon":"pi pi-file-edit",
        "reference_doctype":"Customer",
        "reference_name":"0001",
        "content":"this is from after update"
        }]
    frappe.enqueue("edoor.api.utils.add_audit_trail", queue='short', data=comment_doc)
