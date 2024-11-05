import frappe
@frappe.whitelist(allow_guest=True)
def check_api_url(property_code):
    sql = "select  * from `tabBusiness Branch` where property_code = '{}'".format(property_code)
    data = frappe.db.sql(sql,as_dict =1)
    if data:
        data =data[0]
        return {
            "property_code":property_code,
            "property_name":data.get("name"), 
            "photo":data.get("photo") 
        }

    frappe.throw("Property {} does not exist".format(property_code))

