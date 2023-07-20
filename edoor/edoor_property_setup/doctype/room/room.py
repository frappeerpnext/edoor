# Copyright (c) 2023, Tes Pheakdey and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class Room(Document):
	def validate(self): 
		if not self.reservation_stay:
			self.guest = None
			self.arrival_date = None
			self.departure_date = None
			self.guest_name = None

		if self.housekeeping_status:
			self.status_color = frappe.db.get_value("Housekeeping Status", self.housekeeping_status, "status_color")
