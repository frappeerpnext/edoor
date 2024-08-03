
import frappe


@frappe.whitelist()
def get_data():
    return frappe.db.sql("select * from `tabRoom`",as_dict = 1)