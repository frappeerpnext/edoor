import frappe
def after_migrate():
    frappe.msgprint("Update Complete")