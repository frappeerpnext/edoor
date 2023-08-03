# Copyright (c) 2023, Tes Pheakdey and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils.data import now

class FrontdeskNote(Document):
	def validate(self):
		if not self.is_new():
			is_reservation_stay = True
			is_reservation = True
			if not hasattr(self, 'reservation_stay') or not self.reservation_stay:
				is_reservation_stay = False
				self.reservation_stay = ''
				
			if not hasattr(self, 'reservation') or not self.reservation:
				is_reservation = False
				self.reservation = ''
			if(is_reservation == False and is_reservation_stay == False):
				self.reference_name = ''
				self.reference_doctype = ''
			if is_reservation:
				self.reference_doctype = 'Reservation'
				self.reference_name = self.reservation
			if is_reservation_stay:
				self.reference_name = self.reservation_stay
			if is_reservation_stay and not is_reservation:
				doc = frappe.get_doc('Reservation Stay', self.reference_name)
				self.reservation = doc.reservation 
			
		else:
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