import frappe

def get_door_lock_setting(property):
    key = f"{property}_integration.door_lock.utils.get_door_lock_setting"

    if not frappe.conf.developer_mode:
        if cached_value := frappe.cache.get_value(key):
            return cached_value

    doc = frappe.get_cached_doc("Business Branch", property)
    data ={"ip": doc.door_lock_server_ip_address, "port":doc.door_log_port}
    frappe.cache.set_value(key, data)
    return data