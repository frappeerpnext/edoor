# Copyright (c) 2023, Tes Pheakdey and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class ReservationStay(Document):
	def  validate(self):
		for d in self.stays:
			d.reservation_type = self.reservation_type
			d.guest = self.guest
			
