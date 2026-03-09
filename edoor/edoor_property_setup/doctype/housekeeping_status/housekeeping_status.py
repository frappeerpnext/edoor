# Copyright (c) 2023, Tes Pheakdey and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class HousekeepingStatus(Document):
	def validate(self):
		if  frappe.session.user !="Administrator":
			frappe.throw("Please contact your system administrator to update this record")
	
	def on_update(self):
		if self.creation != self.modified:
			if self.has_value_changed("status_color"):
				frappe.db.sql("update `tabRoom Block` set status_color='{}'".format(self.status_color))
    