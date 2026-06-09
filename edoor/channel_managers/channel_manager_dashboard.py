import frappe

@frappe.whitelist()
def get_channel_manager_dashboard_data(property, working_date):
    get_total_today_res_and_rooms = get_today_reservations(property, working_date)
    get_reservation_by_business_source = get_reservation_by_source(property, working_date)


    return {
        "get_today_reservation": get_total_today_res_and_rooms,
        "get_reservation_by_business_source": get_reservation_by_business_source
    }


def get_today_reservations(property, working_date):
    sql = """ 
        SELECT
            r.total_reservations,
            r.total_rooms,
            COALESCE(rs.total_cancelled_reservations, 0) AS total_cancelled_reservations

        FROM
        (
            SELECT
                COUNT(*) AS total_reservations,
                SUM(total_active_reservation_stay) AS total_rooms
            FROM `tabReservation`
            WHERE
                property = %(property)s
                AND reservation_date = %(working_date)s
                AND channel_manager_booking_id IS NOT NULL
                AND channel_manager_booking_id != ''
        ) r

        LEFT JOIN
        (
            SELECT
                COUNT(*) AS total_cancelled_reservations
            FROM `tabReservation Stay` rs
            INNER JOIN `tabReservation` r
                ON r.name = rs.reservation
            WHERE
                rs.property = %(property)s
                AND rs.cancelled_date = %(working_date)s
                AND rs.reservation_status = 'Cancelled'
                AND r.channel_manager_booking_id IS NOT NULL
                AND r.channel_manager_booking_id != ''
        ) rs ON 1=1
    """
    data = frappe.db.sql(sql, {"property": property, "working_date": working_date}, as_dict=1)

    return data[0] if data else {}


def get_reservation_by_source(property, working_date):
    sql = """
        select 
            count(*) as total_booking, 
            business_source 
        from `tabReservation` 
        where 
            property = %(property)s and
            channel_manager_booking_id is not null and
            reservation_date = %(working_date)s
        group by 
            business_source
    """
    
    data = frappe.db.sql(sql, {"property": property, "working_date": working_date}, as_dict=1)

    return data

@frappe.whitelist()
def get_reservation_booking_by_channel(property, start_date, end_date):
    sql = """
        select 
            count(*) as total_booking, 
            coalesce(business_source, 'Unknown') as business_source
        from `tabReservation` 
        where 
            property = %(property)s and
            channel_manager_booking_id is not null and
            reservation_date between %(start_date)s and %(end_date)s 
        group by 
            business_source 
        order by 
            total_booking
    """

    data = frappe.db.sql(sql, {"property": property, "start_date": start_date, "end_date": end_date}, as_dict=1)

    return data