import frappe
@frappe.whitelist()
def update_assigner_to_work_order_after_insert(doc, method=None, *args, **kwargs):
    if doc.reference_type =="Work Order":
        sql = "delete from `tabWork Order Employee` where parent=%(parent)s and user=%(user)s"
        frappe.db.sql(sql,{"parent":doc.reference_name,"user":doc.allocated_to})
        
        work_order_doc = frappe.get_doc("Work Order",doc.reference_name)
        employee_id = frappe.db.exists("Employee",{"user_id":doc.allocated_to})
        if employee_id:
            if not [d for d in work_order_doc.assign_employee if d.user == doc.allocated_to]:
                work_order_doc.append("assign_employee", {
                    "user":doc.allocated_to,
                    "employee":employee_id ,
                    "note":doc.description
                })
                
                work_order_doc.save()
                
@frappe.whitelist()
def update_assigner_to_work_order_on_update(doc, method=None, *args, **kwargs):
    if doc.reference_type =="Work Order":
        if doc.status == 'Cancelled':
             
            sql = "delete from `tabWork Order Employee` where parent=%(parent)s and user=%(user)s"
            frappe.db.sql(sql,{"parent":doc.reference_name,"user":doc.allocated_to})
            frappe.db.commit()
            
        