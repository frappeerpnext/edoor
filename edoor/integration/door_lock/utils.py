import frappe
import socket
def get_door_lock_setting(property):
    key = f"{property}_integration.door_lock.utils.get_door_lock_setting"

    if not frappe.conf.developer_mode:
        if cached_value := frappe.cache.get_value(key):
            return cached_value

    doc = frappe.get_cached_doc("Business Branch", property)
    data ={"ip": doc.door_lock_server_ip_address, "port":doc.door_log_port}
    frappe.cache.set_value(key, data)
    return data

@frappe.whitelist()
def get_employee_info(property, employee):
    emp_doc = frappe.get_cached_doc("Employee", employee)
    card_holdings = [
        {"card_type": "Master Card","expire":"2026-10-09 15:50","status":"Issue"},
        {"card_type": "Floor Card", "floor":"01", "buiding":"01","expire":"2027-10-09 15:50","status":"Issue"}
    ]
    return {
        "name":emp_doc.name,
        "employee_code":emp_doc.employee_code,
        "employee_name":emp_doc.employee_name,
        "photo":emp_doc.photo,
        "gender":emp_doc.gender,
        "position":emp_doc.position,
        "current_card_holding":card_holdings
    }

@frappe.whitelist()
def get_reservation_stay_card_issue(property, reservation_stay):
    total = -1
    if  frappe.get_cached_value("Business Branch",property,"door_lock_server_ip_address" ):
       
        total = frappe.db.sql(
            "select count(*) as total from `tabDoor Lock Issue Card` where reservation_stay =%(reservation_stay)s",
            {"reservation_stay":reservation_stay},
            as_dict = 1
        )[0].get("total")    
    return {"total":total}


@frappe.whitelist()
def test_connection(IP,PORT):
    """
    Test TCP connection to encoder.
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(5)

    try:
        sock.connect((IP, PORT))
     
        return {
            "success": True,
            "message": "Connected successfully"
        }

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Card Encoder Connection Error")

        return {
            "success": False,
            "message": str(e)
        }

    finally:
        sock.close()


@frappe.whitelist()
def check_door_lock_connection(property):
    setting = get_door_lock_setting(property)
    if not setting.get("ip") or not setting.get("port"):
        return {
            "ip":"",
            "status":"Disconnected"
        }
    
    # test connection
    resp = test_connection(setting.get("ip"), int(setting.get("port") or 10086))
    
    if resp.get("success") == False:
        return {"ip": setting.get("ip"),"status":"Disconnected"}

    return {
        "ip":setting.get("ip"),
        "status":"Connected"
    }