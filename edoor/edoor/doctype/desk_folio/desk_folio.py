# Copyright (c) 2023, Tes Pheakdey and contributors
# For license information, please see license.txt

from decimal import Decimal
import frappe
from frappe.model.document import Document
from frappe.utils.data import getdate
from edoor.edoor.doctype.desk_folio.utils import update_fetch_from_fields

class DeskFolio(Document):
	def validate(self):
		if self.flags.ignore_validate:
			return

		self.balance = (self.total_debit or 0) - (self.total_credit or 0)
		currency_precision = frappe.db.get_single_value("System Settings","currency_precision")
		if abs(round(self.balance, int(currency_precision)))<= (Decimal('0.1') ** int(currency_precision)):
			self.balance = 0
			

		if not self.is_new():
			folio_data = frappe.db.sql("select min(posting_date) as min_date from `tabFolio Transaction` where transaction_type='Desk Folio' and transaction_number='{}'".format(self.name))
			if len(folio_data)>0:
				if folio_data[0][0]:
					if getdate(self.posting_date)>getdate(folio_data[0][0]):
						frappe.throw("Posting date of desk folio must less than or equal to min date of desk transaction transaction")	
		if not self.room_id:
			self.room_number = ''
			self.room_type = ''
			self.room_type_id = ''
	def on_update(self):
		if self.flags.ignore_on_update:
			return

		if self.status == "Closed":
			if(self.balance!=0):
				frappe.throw("You cannot close desk folio that have balance greater than 0")
		
		if self.creation != self.modified:
			update_fetch_from_fields(self)
	def on_trash(self):
		if frappe.db.exists("Folio Transaction", {"transaction_type": "Desk Folio","transaction_number":self.name }):
			frappe.throw("You cannot delete Desk Folio that have transaction")
					


					