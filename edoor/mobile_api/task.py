import frappe

@frappe.whitelist()
def get_user_task_summary(property,user,date):
    sql = """
        SELECT
            b.status_category,
            COUNT(a.name) AS total
        FROM `tabWork Order` a
        INNER JOIN `tabWork Order Status` b ON b.name = a.work_order_status
        WHERE
            a.property = %(property)s
            AND a.workorder_date >= %(date)s
            AND a.due_date <= %(date)s
            AND EXISTS (
                SELECT 1
                FROM `tabToDo` t
                WHERE
                    t.reference_name = a.name
                    AND t.reference_type = 'Work Order'
                    AND t.allocated_to = %(user)s
            )
        GROUP BY b.status_category;

            
    """
    data = frappe.db.sql(sql,{"property":property,"date":date,"user":user},as_dict = 1)
    
    return {
        "ongoing":max((d.get("total") for d in data if d.get("status_category") == "Ongoing"), default=0),
        "complete":max((d.get("total") for d in data if d.get("status_category") == "Complete"), default=0),
        "in_progress":max((d.get("total") for d in data if d.get("status_category") == "In Progress"), default=0),
        "cancelled":max((d.get("total") for d in data if d.get("status_category") == "Cancelled"), default=0)
    }
    