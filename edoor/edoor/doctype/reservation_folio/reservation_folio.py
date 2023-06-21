# Copyright (c) 2023, Tes Pheakdey and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document

class ReservationFolio(Document):
	def validate(self):
		self.balance = (self.total_debit or 0) -( self.total_credit or 0)
