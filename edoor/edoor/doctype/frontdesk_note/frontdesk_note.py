# Copyright (c) 2023, Tes Pheakdey and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils.data import now

class FrontdeskNote(Document):
	def validate(self):
		

		if self.is_new():
			
			if not hasattr(self, 'note_date') and self.note_date:
				self.note_date = now()
			if self.reference_doctype == 'Reservation Stay' or not self.reservation_stay:
				self.reservation_stay = self.reference_name
			elif self.reference_doctype == 'Reservation' and not self.reservation:
				self.reservation = self.reference_name 
			
			if self.reservation_stay:
				self.reference_doctype = 'Reservation Stay'
				self.reference_name = self.reservation_stay
				doc = frappe.get_doc('Reservation Stay', self.reference_name)
				self.reservation = doc.reservation
			else:
				self.reference_doctype = 'Reservation'
				self.reference_name = self.reservation
				self.reservation_stay = ''

 