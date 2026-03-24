import frappe

def get_channal_manager_info(property):
   
    data = {
        "enable": False
    }
    if frappe.db.exists("Channel Manager Integration",property):
        data = frappe.get_cached_doc("Channel Manager Integration",property)
    return data
