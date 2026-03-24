import frappe
import random

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
    

