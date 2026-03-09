import frappe 
import json
@frappe.whitelist(methods="POST")
def get_occupy_list(param):
    # param:{"property":"estc","date":date}
    
    param["keyword"] = param.get("keyword","")
    param["business_source"] = param.get("business_source","")
    param["room_type"] = param.get("room_type","")
    param["reservation_status"] = param.get("reservation_status","")
   
    
    sql = """
        select 
        name,
        reservation,
        reservation_type,
        reference_number,
        reservation_date,
        business_source,
        guest,
        guest_name, 
        business_source, 
        arrival_date, 
        departure_date,
        reservation_status,
        room_type_alias,
        status_color,
        rooms,
        room_nights,
        adr,
        total_amount,
        adult,
        child
    from `tabReservation Stay` 
    where 
        property= %(property)s and 
        
        name in (
            select 
                reservation_stay 
            from `tabRoom Occupy` 
            where 
                property = %(property)s and 
                type='Reservation' and
                is_active = 1 and 
                date = %(date)s
        ) 
            and 
        (%(business_source)s = '' or business_source = %(business_source)s) and 
        (%(room_type)s = '' or room_types = %(room_type)s) and 
        (%(reservation_status)s = '' or reservation_status = %(reservation_status)s) 
 
    """

    data = frappe.db.sql(sql, param,as_dict = 1)
    
    return data