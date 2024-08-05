import frappe

@frappe.whitelist()
def test_update_time():
    doc = frappe.get_doc("Reservation Stay","ST2024-5500")
    doc.arrival_time ='10:55:56'
    doc.save()
    frappe.db.commit()
    
    