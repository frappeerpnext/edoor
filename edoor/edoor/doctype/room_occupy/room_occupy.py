# Copyright (c) 2023, Tes Pheakdey and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class RoomOccupy(Document):
	def validate(self):
		# udpate link field field
		if self.guest:
			guest_name, guest_type,nationality = frappe.db.get_value("Customer",self.guest,["customer_name_en","customer_group","country"])
			self.guest_name = guest_name
			self.guest_type = guest_type
			self.nationality = nationality
		else:
			self.guest_name = ""
			self.guest_type = ""
			self.nationality = ""
