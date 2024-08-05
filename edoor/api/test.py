
import frappe


@frappe.whitelist()
def get_data():
    data = frappe.db.sql("select name, custom_flag_url from `tabCountry`",as_dict=1)
    for d in data:
        doc = frappe.get_doc("Country", d["name"])
        doc.custom_flag_url = d["custom_flag_url"]
        doc.save()
        frappe.clear_document_cache('Country', d["name"])
    frappe.db.commit()
    