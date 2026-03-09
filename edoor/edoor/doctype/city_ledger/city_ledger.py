# Copyright (c) 2023, Tes Pheakdey and contributors
# For license information, please see license.txt

from decimal import Decimal
import frappe
from frappe.model.document import Document

class CityLedger(Document):
	def validate(self):
		self.balance = (self.total_debit or 0) - (self.total_credit or 0)
		currency_precision = frappe.db.get_single_value("System Settings","currency_precision")
		if abs(round(self.balance, int(currency_precision)))<= (Decimal('0.1') ** int(currency_precision)):
			self.balance = 0
   
	def  on_update(self):
		if self.has_value_changed("status") and self.status =='Closed':
			sql = "select sum(total_amount * if(type='Debit',1,-1)) as total from `tabFolio Transaction` where property = %(property)s and transaction_type = 'City Ledger' and transaction_number =%(transaction_number)s"
			data = frappe.db.sql(sql, {"property":self.property,"transaction_number":self.name},as_dict=1)
		 
			if data:
				if data[0].get("total")!=0:
					frappe.throw("You can not close this city ledger account, because balance is not zero")
					
   
   