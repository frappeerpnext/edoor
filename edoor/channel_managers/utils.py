import frappe
 
from frappe.utils import getdate, add_days
def get_channal_manager_info(property):
    cached_key = f"{property}_channel_manager_info"
    if cached_value := frappe.cache.get_value(cached_key):
        
        return cached_value

    data = {
        "enable": False
    }
    if frappe.db.exists("Channel Manager Integration",property):
        data = frappe.get_cached_doc("Channel Manager Integration",property)
    
    frappe.cache.set_value(cached_key, data)
    
    return data



def group_date_ranges(dates_data):
    if not dates_data:
        return []

    # Convert and sort dates
    dates = sorted(getdate(d["date"]) for d in dates_data)

    ranges = []

    start = dates[0]
    prev = dates[0]

    for d in dates[1:]:
        if d == add_days(prev, 1):
            prev = d
        else:
            ranges.append({
                "start_date": start,
                "end_date": prev
            })
            start = d
            prev = d

    # Add last range
    ranges.append({
        "start_date": start,
        "end_date": prev
    })

    return ranges

 
def get_occupancy_codes():
    cached_key = "occupancy_codes"
    if cached_value := frappe.cache.get_value(cached_key):
        
        return cached_value


    sql = """
        select 
            name,
            is_base_guest,
            is_child,
            min_age,
            max_age,
            occupancy,
            require_bed,
            occupancy_type
        from `tabOccupancy Code`

    """

    data = frappe.db.sql(sql,as_dict = 1)
    frappe.cache.set_value(cached_key, data)
    return data
