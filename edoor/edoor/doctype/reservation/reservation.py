# Copyright (c) 2023, Tes Pheakdey and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class Reservation(Document):
	def validate(self):
		data = frappe.db.get_list("Reservation Stay",filters={"reservation":self.name})
		for d in data:
			doc = frappe.get_doc("Reservation Stay",d)
			doc.reservation_type=self.reservation_type
			doc.save()

			#frappe.db.set_value("Reservation Stay",d,"reservation_type",)


