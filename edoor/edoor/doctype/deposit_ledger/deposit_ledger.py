# Copyright (c) 2023, Tes Pheakdey and contributors
# For license information, please see license.txt

from edoor.api.frontdesk import get_working_day
import frappe
from frappe.model.document import Document
from frappe.utils.data import getdate

from decimal import Decimal, ROUND_HALF_UP

class DepositLedger(Document):
	def validate(self):
		if self.is_new():
			working_day = get_working_day(self.property)
			if not working_day["name"]:
				frappe.throw("Please start working day to add deposit leadger")
			else:
				self.working_day = working_day["name"]
				self.working_date =working_day["date_working_day"]
				
			if not working_day["cashier_shift"]:
				frappe.throw("Please start cashier shift to add deposit leadger")
			else:
				self.cashier_shift = working_day["cashier_shift"]["name"]

		
		currency_precision = frappe.db.get_single_value("System Settings","currency_precision")
		if abs(round(self.balance or 0, int(currency_precision)))<= (Decimal('0.1') ** int(currency_precision)):
			self.balance = 0


		if not self.is_new():
			folio_data = frappe.db.sql("select min(posting_date) as min_date from `tabFolio Transaction` where transaction_type='Deposit Ledger' and transaction_number='{}'".format(self.name))
			
			if len(folio_data)>0:
				if folio_data[0][0]:
					if getdate(self.posting_date)>getdate(folio_data[0][0]):
						frappe.throw("Posting date of deposit ledger must less than or equal to min date of deposit transaction")				
		


	def on_update(self):
		if self.status == "Closed":
			if(self.balance!=0):
				frappe.throw("You cannot close deposit ledger that have balance greater than 0")

		#check if customer or room change then run update to folio transaction
		folio_transaction_data = frappe.db.sql("select max(guest) as guest, max(room_id) as room_id  from `tabFolio Transaction` where transaction_type='Deposit Ledger' and transaction_number='{}'".format(self.name),as_dict=1)
		if len(folio_transaction_data)>0:
			if folio_transaction_data[0]["guest"] !=self.guest or folio_transaction_data[0]["room_id"] !=self.room_id: 
				frappe.db.sql("update  `tabFolio Transaction` set guest=%(guest)s, guest_name= %(guest_name)s, room_id=%(room_id)s, room_number=%(room_number)s, room_type_id=%(room_type_id)s, room_type=%(room_type)s where transaction_type='Deposit Ledger' and transaction_number='{}'".format(self.name),
				  {
					  "guest": self.guest,
					  "guest_name":self.guest_name,
					  "room_id":self.room_id,
					  "room_number":self.room_number,
					  "room_type_id":self.room_type_id,
					  "room_type":self.room_type
				  })
				
	def on_trash(self):
		if frappe.db.exists("Folio Transaction", {"transaction_type": "Deposit Ledger","transaction_number":self.name }):
			frappe.throw("You cannot delete deposit ledger that have transaction")
		
		#TOTO pos delete to audit trail record


	def after_insert(self):
		content = f"New deposit ledger added. Deposit Ledger #:<a data-action='view_deposit_ledger_detail' data-name='{self.name}'>{self.name}</a>, Guest: <a data-action='view_guest_detail' data-name='{self.guest}'> {self.guest} - {self.guest_name}</a>"
		frappe.enqueue("edoor.api.utils.add_audit_trail",queue='short', data =[{
				"comment_type":"Created",
				"custom_audit_trail_type":"Created",
				"custom_icon":"pi pi-dollar",
				"subject":"Add New Deposit Ledger",
				"reference_doctype":"Deposit Ledger",
				"reference_name":self.name,
				"content":content
			}])