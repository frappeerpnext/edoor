# Copyright (c) 2023, Tes Pheakdey and contributors
# For license information, please see license.txt

from decimal import Decimal
import frappe
from frappe.model.document import Document
from frappe.utils.data import getdate


class DeskFolio(Document):
	def validate(self):
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

	def on_update(self):
		if self.status == "Closed":
			if(self.balance!=0):
				frappe.throw("You cannot close desk folio that have balance greater than 0")
		
		
		folio_transaction_data = frappe.db.sql("select max(guest) as guest, max(room_id) as room_id  from `tabFolio Transaction` where transaction_type='Desk Folio' and transaction_number='{}'".format(self.name),as_dict=1)
		if len(folio_transaction_data)>0:
			if folio_transaction_data[0]["guest"] !=self.guest or folio_transaction_data[0]["room_id"] !=self.room_id: 
				frappe.db.sql("update  `tabFolio Transaction` set guest=%(guest)s, guest_name= %(guest_name)s, room_id=%(room_id)s, room_number=%(room_number)s, room_type_id=%(room_type_id)s, room_type=%(room_type)s where transaction_type='Desk Folio' and transaction_number='{}'".format(self.name),
				  {
					  "guest": self.guest,
					  "guest_name":self.guest_name,
					  "room_id":self.room_id,
					  "room_number":self.room_number,
					  "room_type_id":self.room_type_id,
					  "room_type":self.room_type
				  })
			
			  
				

	def on_trash(self):
		if frappe.db.exists("Folio Transaction", {"transaction_type": "Desk Folio","transaction_number":self.name }):
			frappe.throw("You cannot delete Desk Folio that have transaction")
					


					