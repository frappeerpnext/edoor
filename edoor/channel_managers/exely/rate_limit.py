import time
import frappe

# this value from exely doc
LIMITS = {
    "sec": (1460, 2),
    "min3": (4380, 180),
    "hour": (13140, 3600),
    "day": (43800, 86400)
}

# LIMITS = {
#     "sec": (2460, 2),
#     "min3": (6380, 180),
#     "hour": (33140, 3600),
#     "day": (63800, 86400)
# }


@frappe.whitelist()
def test_me():
    return update_rate_limit_balance("SR0001",'rt0041',500)

@frappe.whitelist()
def get_limit():
    return get_rate_limit("ESTC HOTEL 6",["RT-0001","RT-0002","RT-0003","RT-0004"])



def update_rate_limit_balance(
    property,
    room_type,
    change_count
):
    cache = frappe.cache()

    now = int(time.time())

    keys = {
        "sec": f"pms_limit:{property}:{room_type}:sec:{now}",
        "min3": f"pms_limit:{property}:{room_type}:min3:{now // 180}",
        "hour": f"pms_limit:{property}:{room_type}:hour:{now // 3600}",
        "day": f"pms_limit:{property}:{room_type}:day:{time.strftime('%Y%m%d')}"
    }

    # 🔎 Step 1 — Check limits
    for window, key in keys.items():

        limit, ttl = LIMITS[window]

        current = cache.get_value(key) or 0

        if int(current) + change_count > limit:

            return False, (
                f"{window} limit exceeded "
                f"for room_type {room_type}"
            )


    # ➕ Step 2 — Update values
    for window, key in keys.items():

        limit, ttl = LIMITS[window]

        current = cache.get_value(key) or 0

        new_value = int(current) + change_count

        cache.set_value(
            key,
            new_value,
            expires_in_sec=ttl
        )
    
    return True, "OK"

@frappe.whitelist()
def check_rate_limit_status_by_room_type(
    property = 'ESTC HOTEL 6',
    room_type = 'RT0001'
):
    cache = frappe.cache()

    now = int(time.time())

    keys = {
        "sec": f"pms_limit:{property}:{room_type}:sec:{now}",
        "min3": f"pms_limit:{property}:{room_type}:min3:{now // 180}",
        "hour": f"pms_limit:{property}:{room_type}:hour:{now // 3600}",
        "day": f"pms_limit:{property}:{room_type}:day:{time.strftime('%Y%m%d')}"
    }

    # 🔎 Step 1 — Check limits
    for window, key in keys.items():

        limit, ttl = LIMITS[window]

        current = cache.get_value(key) or 0

        if int(current) >= limit:

            return {"rate_limit_status":False, "rate_limit_message": (
                f"{window} limit exceeded "
                f"for room_type {room_type}")
            }

 
    return {"rate_limit_status": True, "rate_limit_message":"Ok"}



@frappe.whitelist()
def get_room_limit_balance():
    room_types = frappe.db.sql("select property,name from `tabRoom Type`",as_dict = 1)
    data = {}
    def get_limit_balance(property, room_type="rt0041"):    
        
        cache = frappe.cache()
        now = int(time.time())
        keys = {
            "sec": f"pms_limit:{property}:{room_type}:sec:{now}",
            "min3": f"pms_limit:{property}:{room_type}:min3:{now // 180}",
            "hour": f"pms_limit:{property}:{room_type}:hour:{now // 3600}",
            "day": f"pms_limit:{property}:{room_type}:day:{time.strftime('%Y%m%d')}"
        }

        data = {}
        
        for period, key in keys.items():
            current = cache.get_value(key) or 0
            remaining = LIMITS[period][0] - int(current)
            data[period] = remaining

        return {"keys":keys, "data":data}
            
    for p in set([d.get("property") for d in room_types]):
        data[p] = {}
        room_types = [d.get("name") for d in room_types if d.get("property") == p]
        for rt in room_types:
            data[p][rt] = get_limit_balance(p, rt)

    return  data

@frappe.whitelist()
def get_rate_limit(property=None,room_types=None):
    if not property:
        property="ESTC HOTEL 6"
    if not room_types:
        room_types = ["RT0001","RT0002","RT0003","RT0004"]
    def get_min_value(room_type="rt0041"):    
        
        cache = frappe.cache()
        now = int(time.time())
        keys = {
            "sec": f"pms_limit:{property}:{room_type}:sec:{now}",
            "min3": f"pms_limit:{property}:{room_type}:min3:{now // 180}",
            "hour": f"pms_limit:{property}:{room_type}:hour:{now // 3600}",
            "day": f"pms_limit:{property}:{room_type}:day:{time.strftime('%Y%m%d')}"
        }

        data = {}
        remaining_values = []
        for period, key in keys.items():
            current = cache.get_value(key) or 0
            remaining = LIMITS[period][0] - int(current)
            remaining_values.append(remaining)
     
        return min(remaining_values)
    
    data = {}
    for rt in room_types:
        data[rt] = get_min_value(rt)

    return data
