# Copyright (c) 2023, Tes Pheakdey and contributors
# For license information, please see license.txt


from edoor.api.reservation import get_room_rate
import frappe
from frappe.model.document import Document
from edoor.api.utils import  update_reservation_stay,update_reservation,get_base_rate
import json
class ReservationRoomRate(Document):
	def validate(self):
		self.input_rate =float( self.input_rate or 0)
		if not self.is_manual_rate:
			#get_room_rate(property, rate_type, room_type, business_source, date):
			if hasattr(self,"regenerate_rate") and  self.regenerate_rate:
				self.input_rate = get_room_rate(self.property, self.rate_type, self.room_type,self.business_source,self.date)	
		
		self.rate = self.input_rate or 0		 
		self.discount = self.discount or 0
		
		if self.discount_type=="Percent":
			self.discount_amount =float( self.input_rate or 0 ) * ((self.discount or 0) / 100.0)
		else:
			self.discount_amount = self.discount or 0 
		self.discount = self.discount or 0

		if (self.discount_amount or 0) > (self.input_rate or 0):
			frappe.throw("Discount amount cannot greater than amount")


		if self.tax_rule:
			tax_rule = frappe.get_doc("Tax Rule",self.tax_rule)
			self.tax_1_account = tax_rule.tax_1_account
			self.tax_2_account = tax_rule.tax_2_account
			self.tax_3_account = tax_rule.tax_3_account
			if self.rate_include_tax== "Yes" and (self.tax_1_rate + self.tax_2_rate + self.tax_3_rate) > 0:
				
				price = get_base_rate((self.input_rate or 0) - (self.discount_amount or 0),tax_rule,self.tax_1_rate, self.tax_2_rate, self.tax_3_rate)

				self.rate = price + (self.discount_amount or 0)
 
			else:
				self.rate = self.rate
			
			#tax 1
			self.taxable_amount_1 = self.rate * ((tax_rule.percentage_of_price_to_calculate_tax_1 or 100)/100)
			
			self.taxable_amount_1 = self.taxable_amount_1 if tax_rule.calculate_tax_1_after_discount == 0 and self.rate_include_tax== "No"   else self.taxable_amount_1 - self.discount_amount

			self.tax_1_amount = self.taxable_amount_1 * self.tax_1_rate / 100
			#tax 2
			self.taxable_amount_2 = self.rate * ((tax_rule.percentage_of_price_to_calculate_tax_2 or 100)/100)
			self.taxable_amount_2 = self.taxable_amount_2 if tax_rule.calculate_tax_2_after_discount == 0  and self.rate_include_tax== "No"  else self.taxable_amount_2 - self.discount_amount
			self.taxable_amount_2 = self.taxable_amount_2  if tax_rule.calculate_tax_2_after_adding_tax_1 == 0 else self.taxable_amount_2 + self.tax_1_amount
			self.tax_2_amount = self.taxable_amount_2 * self.tax_2_rate / 100
			#tax 3
			self.taxable_amount_3 = self.rate * ((tax_rule.percentage_of_price_to_calculate_tax_3 or 100)/100)
			self.taxable_amount_3 = self.taxable_amount_3 if tax_rule.calculate_tax_3_after_discount == 0 and  self.rate_include_tax== "No"  else self.taxable_amount_3 - self.discount_amount
			self.taxable_amount_3 = self.taxable_amount_3  if tax_rule.calculate_tax_3_after_adding_tax_1 == 0 else self.taxable_amount_3 + self.tax_1_amount
			self.taxable_amount_3 = self.taxable_amount_3  if tax_rule.calculate_tax_3_after_adding_tax_2 == 0 else self.taxable_amount_3 + self.tax_2_amount
			self.tax_3_amount = self.taxable_amount_3 * self.tax_3_rate / 100
			self.total_tax = (self.tax_1_amount or 0 ) + (self.tax_2_amount or 0 ) + (self.tax_3_amount or 0 ) 
		else:
			 
			self.rate_include_tax = 'No'
			self.tax_1_rate = 0
			self.tax_2_rate = 0
			self.tax_3_rate = 0
			self.tax_1_amount = 0
			self.tax_2_amount = 0
			self.tax_3_amount = 0
			self.taxable_amount_1 = 0
			self.taxable_amount_2 = 0
			self.taxable_amount_3 = 0
			self.total_tax = 0

		self.total_tax = (self.tax_1_amount or 0 ) + (self.tax_2_amount or 0 ) + (self.tax_3_amount or 0 ) 
		self.total_rate = (self.rate or 0) - (self.discount_amount or 0) + self.total_tax



