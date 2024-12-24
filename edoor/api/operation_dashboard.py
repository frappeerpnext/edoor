import frappe 


@frappe.whitelist()
def get_summary(property,date):
    from edoor.api.frontdesk import get_dashboard_data
    data = get_dashboard_data(property=property, date =date)
    return data

@frappe.whitelist(methods="POST")
def get_all_guest(filter):
    sql = """
        select
            rs.name,
            rs.reservation,
            rs.arrival_date,
            rs.departure_date,
            rs.guest,
            rs.guest_name,
            rs.reservation_color,
            rs.reservation_color_code,
            coalesce(c.photo, '') as photo,
            rs.guest_email,
            rs.guest_phone_number,
            rs.room_type_alias,
            rs.room_types,
            rs.arrival_date,
            rs.departure_date,
            rs.room_nights,
            rs.adult,
            rs.child,
            rs.status_color,
            rs.business_source,
            rs.reservation_status,
            rs.reservation_type,
            rs.reference_number
        from `tabReservation Stay` rs
        inner join `tabCustomer` c on c.name = rs.guest
        where
            rs.property = %(property)s and
            rs.name in (
                select 
                    distinct ro.reservation_stay
                from `tabRoom Occupy` ro
                where 
                    ro.property = %(property)s and 
                    ro.date = %(date)s and 
                    ro.is_active = 1 and 
                    ro.is_active_reservation = 1 and 
                    ro.type = 'Reservation'
            ) 
    """
    data = frappe.db.sql(sql,filter,as_dict=1)
    
    return data

@frappe.whitelist(methods="POST")
def get_arrival_guest(filter):
    sql = """
        select
            name,
            reservation,
            arrival_date,
            departure_date,
            guest,
            guest_name
            
        from `tabReservation Stay`
        where
            property = %(property)s and
            name in (
                select 
                    distinct reservation_stay
                from `tabRoom Occupy`
                where 
                    property = %(property)s and 
                    date = %(date)s and 
                    is_active = 1 and 
                    is_active_reservation = 1 and 
                    type = 'Reservation' and 
                    is_arrival = 1
            ) 

    """
    data = frappe.db.sql(sql,filter,as_dict=1)
    
    return data