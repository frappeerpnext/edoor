import frappe
@frappe.whitelist()
def test():
    return "hello"