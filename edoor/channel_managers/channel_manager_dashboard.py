import frappe

@frappe.whitelist()
def get_channel_manager_dashboard_data(property, working_date):
    get_today_reservations(property, working_date)


def get_today_reservations(property, working_date):
    sql = """
        select 
            count(*) as total_reservation
        from `tabReservation` 
        where
            property = %(property)s
            reservation_date = %(working_date)s
    """
    return frappe.db.sql(sql, {"property": property, "working_date": working_date}, as_dict=1)