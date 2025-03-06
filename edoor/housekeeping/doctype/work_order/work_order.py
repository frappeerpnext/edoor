# Copyright (c) 2024, Tes Pheakdey and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class WorkOrder(Document):
	def validate(self):
		self.workorder_date = self.workorder_date or self.posting_date
		if not self.due_date:
			self.due_date = self.workorder_date
			
   
	# def after_insert(self):
	# 	to_do_doc = {
	# 		"status":"Open","priority":"Medium",
	# 		"date":self.workorder_date,
	# 		"allocated_to":frappe.session.user,
	# 		"description":"Assignment for Work Order " + self.name,
	# 		"reference_type":"Work Order",
	# 		"reference_name":self.name,
	# 		"assigned_by":frappe.session.user,"doctype":"ToDo"
    #     }

