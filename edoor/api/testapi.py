import frappe
@frappe.whitelist()
def test():
    reservation_stay = "ST2024-6693"
    sql = """
        SELECT 
            name,
            account_code,
            parent_reference,
            is_package_breakdown,
            sum(amount * if(type='Debit',1,-1)) as amount
        FROM `tabRevenue Forecast Breakdown` 
        WHERE reservation_stay = '{}'
        GROUP BY account_code
    """.format(reservation_stay)
    data = frappe.db.sql(sql,as_dict=1)
    return data