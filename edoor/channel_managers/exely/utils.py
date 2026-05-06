import frappe
import random
import re
from datetime import datetime
from frappe.utils import now_datetime,get_datetime
def json_to_xml():
    return {}

def get_exely_property_code(property):
    return frappe.get_cached_doc("Channel Manager Integration",property).property_code

def exely_channel_manager_integration(property_code):
    cache_key = f"exely_channel_manager_integration:{property_code}"
    exely_channel = frappe.cache().get_value(cache_key)

    if not exely_channel:
        exely_channel = frappe.db.get_value(
            "Channel Manager Integration",
            {"property_code": property_code},
            ["name","room_types"],
            as_dict=True
        )
        frappe.cache().set_value(cache_key, exely_channel)
    return exely_channel

def get_room_type_mapping(room_type,property):
    cache_key = f"exely_room_type_mapping:{room_type}{property}"
    mapping = frappe.cache().get_value(cache_key)
    if not mapping:
        mapping = frappe.db.get_value(
            "Room Type Mapping",
            {"room_type_code": room_type, "parent": property},
            ["name", "edoor_room_type","room_type_name"],
            as_dict=True
        )
        frappe.cache().set_value(cache_key, mapping)
    return mapping
def get_service_mapping(service,property):
    cache_key = f"exely_service_mapping:{service}{property}"
    mapping = frappe.cache().get_value(cache_key)
    frappe.cache().delete_value(cache_key)
    if not mapping:
        mapping = frappe.db.get_value(
            "Service Mapping",
            {"services_code": service, "parent": property},
            ["name", "edoor_service_code","service_name"],
            as_dict=True
        )
        frappe.cache().set_value(cache_key, mapping)
        # To clear a specific key
       
        
    return mapping
def get_rate_type_mapping(rate_type,property):
    cache_key = f"exely_rate_type_mapping:{rate_type}{property}"
    mapping = frappe.cache().get_value(cache_key)
    if not mapping:
        mapping = frappe.db.get_value(
            "Rate Plan Mapping",
            {"rate_plan_code": rate_type, "parent": property},
            ["name","edoor_rate_plan"],
            as_dict=True
        )
        frappe.cache().set_value(cache_key, mapping)
    return mapping
def random_color():
    return "#{:06X}".format(random.randint(0, 0xFFFFFF))

def get_exely_room_type_code(edoor_room_type_id):
    
    sql = "select room_type_code from `tabRoom Type Mapping` where edoor_room_type=%(edoor_room_type_id)s and coalesce(room_type_code,'') !=''"
    data = frappe.db.sql(sql,{"edoor_room_type_id":edoor_room_type_id},as_dict =1)
    if data:
        return data[0].get("room_type_code")
    return None



def create_guest(guest_info):
    guest_email = guest_info.get("guest_email")
    guest_name = guest_info.get("guest_name")
    nationality = guest_info.get("nationality") or "Unknown"

    existing_guest = None

    if guest_email:
        existing_guest = frappe.db.exists("Customer", {"email_address": guest_email})

    if existing_guest:
        guest = frappe.get_doc("Customer", existing_guest)
        guest.guest_type = guest_info.get("guest_type") or guest.guest_type
        guest.nationality = nationality or guest.nationality
        guest.guest_phone_number = guest_info.get("guest_phone_number") or guest.guest_phone_number
        guest.customer_name_en = guest_name or guest.customer_name_en
        guest.save(ignore_permissions=True)
        return guest

    guest = frappe.get_doc({
        "doctype": "Customer",
        "guest_type": guest_info.get("guest_type") or "General",
        "nationality": nationality,
        "guest_email": guest_email,
        "guest_phone_number": guest_info.get("guest_phone_number") or "",
        "customer_name_en": guest_name,
        "customer_group": "General",
    })
    guest.insert(ignore_permissions=True)
    return guest

def get_country(country_code):
    cache_key = f"country_mapping:{country_code}"
    country_mapping = frappe.cache().get_value(cache_key)
    if not country_mapping:
        country_mapping = frappe.db.get_value(
            "Country",
            {"custom_country_code": country_code},
            ["name", "code"],
            as_dict=True
        )
        frappe.cache().set_value(cache_key, country_mapping)
    return country_mapping
    


def parse_transfer(text):

    def find(pattern, group=1):
        m = re.search(pattern, text, re.IGNORECASE)
        return m.group(group).strip() if m else None

    text = text.replace("\\r\\n", "\n")

    # Detect transfer type
    transfer_type = "arrival" if "arrival" in text.lower() else \
                    "departure" if "departure" in text.lower() else None

    # Time (support HH:MM:SS)
    time_match = re.search(r'(Arrival|Departure):\s*(\d{2}:\d{2}(?::\d{2})?)', text, re.IGNORECASE)
    service_time = time_match.group(2) if time_match else None

    # Date (optional, not in your sample)
    date_match = re.search(r'(Arrival|Departure) date:\s*(\d{2}-\d{2}-\d{4})', text, re.IGNORECASE)
    service_date = None
    if date_match:
        service_date = datetime.strptime(date_match.group(2), "%d-%m-%Y").strftime("%Y-%m-%d")

    # Flight number (avoid wrong text)
    flight = find(r'Flight number:\s*(.+)')
    if flight and flight.lower() == "flight":
        flight = None

    # Extract vehicle + qty + amount
    vehicle_match = re.search(r'(\w+)\s*-\s*(\d+)pcs\s*X\s*([\d.]+)\s*USD', text, re.IGNORECASE)

    vehicle = None
    qty = 1
    amount = 0

    if vehicle_match:
        vehicle = vehicle_match.group(1)       
        qty = int(vehicle_match.group(2)) 
        amount = float(vehicle_match.group(3))

    route_match = re.search(r'Transference\s*(.*?)\s*→\s*(.*?)\n', text)
    route = None
    if route_match:
        route = route_match.group(1).strip()
        # Remove backslash and quote
        route = route.replace('\\', '').replace('"', '')

    return {
        "service_type": "airport_transfer",
        "transfer_type": transfer_type,
        "route": route,
        "mode": vehicle,
        "service_date": service_date,
        "time": service_time,
        "flight_number": flight,
        "quantity": qty,
        "amount": amount,
        "currency": "USD" if amount else None,
        "posting_date": service_date
    }


def get_package_rule_mapping(package_type,property):
    cache_key = f"exely_package_type_mapping:{package_type}{property}"
    mapping = frappe.cache().get_value(cache_key)
    if not mapping:
        mapping = frappe.db.get_value(
            "Package Rule Mapping",
            {"service_type": package_type, "parent": property},
            ["name","edoor_posting_rule","edoor_charge_rule"],
            as_dict=True
        )
        frappe.cache().set_value(cache_key, mapping)
    return mapping

def get_occupancy_code_mapping(occupancy_type, age_bucket,is_alult = 0,total = 0):
    cache_key = f"exely_occupancy_code_mapping:{occupancy_type}:{age_bucket}"
    mapping = frappe.cache().get_value(cache_key)
    filters = {
    "occupancy_type": occupancy_type,
    "age_bucket": age_bucket,
}   
    frappe.cache().delete_value(cache_key)
    if is_alult:
        filters["occupancy"] = total
    if not mapping:
        mapping = frappe.db.get_all(
            "Occupancy Code",
            filters=filters,
            fields=["name", "occupancy_type", "min_age", "max_age"],
            limit=1
        )

        mapping = mapping[0] if mapping else None

        frappe.cache().set_value(cache_key, mapping)
        
    return mapping




def add_guest_list(group):
    guest_list = []
    for data in group.values(): 
        age_code = data.get("@AgeQualifyingCode")
        ages = data.get("@Age") or []
        if not isinstance(ages, list):
            ages = [ages]
        age_str = ",".join(map(str, ages))
        age_bucket = data.get("@AgeBucket") or 0
        total = int(data.get("@Count", 0))
        is_alult = data.get("is_alult", 0)
        if not isinstance(ages, list):
            ages = [ages]
        mapping = get_occupancy_code_mapping(age_code, age_bucket,is_alult,total)
        if not mapping:
            continue
        else:
            guest_list.append({
                "name": mapping["name"],
                "age": age_str,
                "value": total,
            })
    return guest_list

def ensure_list(data):
    if not data:
        return []
    return data if isinstance(data, list) else [data]
