# Copyright (c) 2023, Tes Pheakdey and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class BusinessSource(Document):
	def validate(self):
		if self.is_new():
			if self.auto_create_city_ledger_account==1:
				if not self.city_ledger_type:
					frappe.throw("Please select city ledger type")

	def after_insert(self):
		if self.auto_create_city_ledger_account==1:
			doc = frappe.get_doc({
				'doctype': 'City Ledger',
				'property': self.property,
				'phone_number': self.phone_number,
				'email_address': self.email,
				"city_ledger_name":self.business_source,
				"business_source":self.business_source,
				"contact_name":self.contact_name,
				"city_ledger_type":self.city_ledger_type
			})
			doc.insert()