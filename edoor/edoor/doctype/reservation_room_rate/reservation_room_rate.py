# Copyright (c) 2023, Tes Pheakdey and contributors
# For license information, please see license.txt


from edoor.api.reservation import get_room_rate
import frappe
from frappe.model.document import Document

class ReservationRoomRate(Document):
	def validate(self):
		
		self.rate =float( self.rate or 0)
		if not self.is_manual_rate:
			#get_room_rate(property, rate_type, room_type, business_source, date):
			if hasattr(self,"regenerate_rate") and  self.regenerate_rate:
				self.rate = get_room_rate(self.property, self.rate_type, self.room_type,self.business_source,self.date)	

		self.discount = self.discount or 0
		
		if self.discount_type=="Percent":
 
			self.discount_amount =float( self.rate) * (self.discount / 100.0)
			 
		else:
			self.discount_amount = self.discount 

		if self.tax_rule:
			tax_rule = frappe.get_doc("Tax Rule",self.tax_rule)
			#tax 1
			self.taxable_amount_1 = self.rate if tax_rule.calculate_tax_1_after_discount == 0 else self.rate - self.discount_amount
			self.tax_1_amount = self.taxable_amount_1 * tax_rule.tax_1_rate / 100
			#tax 2
			self.taxable_amount_2 = self.rate if tax_rule.calculate_tax_2_after_discount == 0 else self.rate - self.discount_amount
			self.taxable_amount_2 = self.taxable_amount_2  if tax_rule.calculate_tax_2_after_adding_tax_1 == 0 else self.taxable_amount_2 + self.tax_1_amount
			self.tax_2_amount = self.taxable_amount_2 * tax_rule.tax_2_rate / 100
			#tax 3
			self.taxable_amount_3 = self.rate if tax_rule.calculate_tax_3_after_discount == 0 else self.rate - self.discount_amount
			self.taxable_amount_3 = self.taxable_amount_3  if tax_rule.calculate_tax_3_after_adding_tax_1 == 0 else self.taxable_amount_3 + self.tax_1_amount
			self.taxable_amount_3 = self.taxable_amount_3  if tax_rule.calculate_tax_3_after_adding_tax_2 == 0 else self.taxable_amount_3 + self.tax_2_amount
			self.tax_3_amount = self.taxable_amount_3 * tax_rule.tax_3_rate / 100
			

		self.total_tax = (self.tax_1_amount or 0 ) + (self.tax_2_amount or 0 ) + (self.tax_3_amount or 0 ) 
		self.total_amount = (self.rate or 0) - (self.discount_amount or 0) + (self.total_tax or 0)


