# Copyright (c) 2024, Tes Pheakdey and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class WorkOrder(Document):
	def validate(self):
		self.workorder_date = self.workorder_date or self.posting_date
  
			
