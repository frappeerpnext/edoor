# Copyright (c) 2023, Tes Pheakdey and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class RateType(Document):
	def validate(self):
		if self.is_complimentary==1 and self.is_house_use==1:
			frappe.throw("Please uncheck Is Complimetary or uncheck Is house use")
			
	def on_update(self):
		frappe.clear_document_cache("Rate Type", self.name)
