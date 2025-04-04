# Copyright (c) 2025, Tes Pheakdey and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
import json

class AppListViewSetting(Document):
	pass

@frappe.whitelist(methods="POST")
def  SaveListViewSetting(data):
    if frappe.db.exists("App List View Setting", data.get("name")):
        doc = frappe.get_doc("App List View Setting",data.get("name"))
        doc.fields = json.dumps(data.get("fields"))
        doc.filter_options = json.dumps(data.get("filter_options"))
        doc.save()
    else:
        doc = frappe.new_doc('App List View Setting')
        doc.list_view_name = data.get("name")
        doc.fields =  json.dumps(data.get("fields"))
        doc.filter_options = json.dumps(data.get("filter_options")) or "[]"
        doc.insert()
    frappe.db.commit()
    
    
    frappe.msgprint("Save list view successfully")
    return doc
        
