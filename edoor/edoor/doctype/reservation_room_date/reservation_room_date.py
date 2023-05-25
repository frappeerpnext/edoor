# Copyright (c) 2023, Tes Pheakdey and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class ReservationRoomDate(Document):
	def validate(self):
		self.rate = self.rate or 0
		self.discount = self.discount or 0
		if self.discount_type=="Percent":
			self.discount_amount = self.rate * self.discount / 100
		else:
			self.discount_amount = self.discount 

		if self.tax_rule:
			tax_rule = frappe.get_doc("Tax Rule",self.tax_rule)
			#tax 1
			self.taxable_amount_1 = self.rate if tax_rule.calculate_tax_1_after_discount == 0 else self.rate - self.discount_amount
			self.tax_1_amount = self.taxable_amount_1 * tax_rule.tax_1_rate
			#tax 2
			self.taxable_amount_2 = self.rate if tax_rule.calculate_tax_2_after_discount == 0 else self.rate - self.discount_amount
			self.taxable_amount_2 = self.taxable_amount_2  if tax_rule.calculate_tax_2_after_after_adding_tax_1 == 0 else self.taxable_amount_2 + self.tax_1_amount
			self.tax_2_amount = self.taxable_amount_2 * tax_rule.tax_2_rate
			#tax 3
			self.taxable_amount_3 = self.rate if tax_rule.calculate_tax_3_after_discount == 0 else self.rate - self.discount_amount
			self.taxable_amount_3 = self.taxable_amount_3  if tax_rule.calculate_tax_3_after_after_adding_tax_1 == 0 else self.taxable_amount_3 + self.tax_1_amount
			self.taxable_amount_3 = self.taxable_amount_3  if tax_rule.calculate_tax_3_after_after_adding_tax_2 == 0 else self.taxable_amount_3 + self.tax_2_amount
			self.tax_3_amount = self.taxable_amount_3 * tax_rule.tax_3_rate
			

		self.total_tax = (self.tax_1_amount or 0 ) + (self.tax_2_amount or 0 ) + (self.tax_3_amount or 0 ) 
		self.total_amount = (self.rate or 0) - (self.discount_amount or 0) + (self.total_tax or 0)

