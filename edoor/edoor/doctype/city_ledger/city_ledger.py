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
