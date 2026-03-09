
from edoor.api.frontdesk import get_working_day
import frappe

@frappe.whitelist()
def reservation_list(property=None, date=None, room_type=None):
    if not date:
        working_date = get_working_day(property)
        date = working_date["date_working_day"]
    
    if not date:
        date = frappe.utils.today()

        
        
    filter = {"property":property, "date":date, "room_type":room_type or ""}
    # arrival
    arrival_guest = frappe.db.sql("""
        select 
            reservation,
            name,
            reference_number,
            adult,
            child,
            reservation_type,
            reservation_date,
            arrival_date,
            departure_date,
            room_nights,
            rooms,
            room_type_alias,
            guest,
            guest_name,
            business_source,
            adr,
            total_amount,
            reservation_status,
            room_rate_discount,
            status_color
        from `tabReservation Stay`
        where
            name in (
                select distinct c.reservation_stay from `tabRoom Occupy` c
                where
                    c.date = %(date)s and 
                    c.property = %(property)s and 
                    c.room_type_id = if(%(room_type)s='',c.room_type_id,%(room_type)s) and 
                    c.is_arrival = 1 and 
                    c.is_active=1 and 
                    c.is_active_reservation = 1
            ) and 
            property = %(property)s
    """,filter, as_dict=1)

    # stay over guest
    stay_over = frappe.db.sql("""
        select 
            reservation,
            name,
            reference_number,
            adult,
            child,
            reservation_type,
            reservation_date,
            arrival_date,
            departure_date,
            room_nights,
            rooms,
            room_type_alias,
            guest,
            guest_name,
            business_source,
            adr,
            total_amount,
            reservation_status,
            status_color,
            room_rate_discount
        from `tabReservation Stay`
        where
            name in (
                select distinct c.reservation_stay from `tabRoom Occupy` c
                where
                    c.date = %(date)s and 
                    c.property = %(property)s and 
                    c.room_type_id = if(%(room_type)s='',c.room_type_id,%(room_type)s) and 
                    c.is_stay_over = 1 and 
                    c.is_active=1 and 
                    c.is_active_reservation = 1
            ) and 
            property = %(property)s
    """,filter, as_dict=1)
    # departure guest
    departure = frappe.db.sql("""
        select 
            reservation,
            name,
            reference_number,
            adult,
            child,
            reservation_type,
            reservation_date,
            arrival_date,
            departure_date,
            room_nights,
            rooms,
            room_type_alias,
            guest,
            guest_name,
            business_source,
            adr,
            total_amount,
            reservation_status,
            status_color,
            room_rate_discount
        from `tabReservation Stay`
        where
            name in (
                select distinct c.reservation_stay from `tabRoom Occupy` c
                where
                    c.date = %(date)s and 
                    c.property = %(property)s and 
                    c.room_type_id = if(%(room_type)s='',c.room_type_id,%(room_type)s) and 
                    c.is_departure = 1 and 
                    c.is_active_reservation = 1
            ) and 
            property = %(property)s
    """,filter, as_dict=1)
    
    return {
        "arrival":arrival_guest,
        "stay_over":stay_over,
        "departure":departure,
    }