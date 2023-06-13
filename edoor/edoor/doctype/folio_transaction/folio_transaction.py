# Copyright (c) 2023, Tes Pheakdey and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class FolioTransaction(Document):
	def validate(self):
		frappe.throw(self.rate_include_tax)
		self.input_amount =float( self.input_amount or 0)
		self.quantity=float( self.quantity or 1)
 
				 
		self.discount = self.discount or 0
		
		if self.discount_type=="Percent":
			self.discount_amount =float( self.input_amount or 0 ) * ((self.discount or 0) / 100.0)
			 
		else:
			self.discount_amount = self.discount or 0 

		if self.tax_rule:

			tax_rule = frappe.get_doc("Tax Rule",self.tax_rule)
			if self.rate_include_tax== "Yes":
				price = calculate_tax_reverse(self.input_amount - self.discount_amount ,tax_rule)
				
				self.amount = price
			else:
				self.amount = self.input_amount

			
			#tax 1
			self.taxable_amount_1 = self.amount * ((tax_rule.percentage_of_price_to_calculate_tax_1 or 100)/100)
			
			self.taxable_amount_1 = self.taxable_amount_1 if tax_rule.calculate_tax_1_after_discount == 0 or  self.rate_include_tax == 'Yes' else self.taxable_amount_1 - self.discount_amount

			self.tax_1_amount = self.taxable_amount_1 * tax_rule.tax_1_rate / 100
			#tax 2
			self.taxable_amount_2 = self.amount * ((tax_rule.percentage_of_price_to_calculate_tax_2 or 100)/100)
			self.taxable_amount_2 = self.taxable_amount_2 if tax_rule.calculate_tax_2_after_discount == 0  or  self.rate_include_tax == 'Yes' else self.taxable_amount_2 - self.discount_amount
			self.taxable_amount_2 = self.taxable_amount_2  if tax_rule.calculate_tax_2_after_adding_tax_1 == 0 else self.taxable_amount_2 + self.tax_1_amount
			self.tax_2_amount = self.taxable_amount_2 * tax_rule.tax_2_rate / 100
			#tax 3
			self.taxable_amount_3 = self.amount * ((tax_rule.percentage_of_price_to_calculate_tax_3 or 100)/100)
			self.taxable_amount_3 = self.taxable_amount_3 if tax_rule.calculate_tax_3_after_discount == 0 or  self.rate_include_tax == 'Yes' else self.taxable_amount_3 - self.discount_amount
			self.taxable_amount_3 = self.taxable_amount_3  if tax_rule.calculate_tax_3_after_adding_tax_1 == 0 else self.taxable_amount_3 + self.tax_1_amount
			self.taxable_amount_3 = self.taxable_amount_3  if tax_rule.calculate_tax_3_after_adding_tax_2 == 0 else self.taxable_amount_3 + self.tax_2_amount
			self.tax_3_amount = self.taxable_amount_3 * tax_rule.tax_3_rate / 100
			self.total_tax = (self.tax_1_amount or 0 ) + (self.tax_2_amount or 0 ) + (self.tax_3_amount or 0 ) 
			

		self.bank_fee = self.bank_fee or 0
		self.bank_fee_amount = self.amount * self.bank_fee / 100
		
		
		self.total_amount = (self.amount or 0) - (self.discount_amount or 0) + (self.total_tax or 0) + self.bank_fee_amount




def calculate_tax_reverse(amount,tax_rule):
		

	t1_r = tax_rule.tax_1_rate / 100
	t2_r = tax_rule.tax_2_rate / 100
	t3_r = tax_rule.tax_3_rate / 100
	#frappe.throw("{}-{}-{}-{}-{}".format(amount,disc,t1_r,t2_r,t3_r))

	tax_1_amount = 0
	tax_2_amount = 0
	tax_3_amount = 0
	price = 0

	t1_af_disc = tax_rule.calculate_tax_1_after_discount
	t2_af_disc = tax_rule.calculate_tax_2_after_discount
	t2_af_add_t1 = tax_rule.calculate_tax_2_after_adding_tax_1
	t3_af_disc	= tax_rule.calculate_tax_3_after_discount
	t3_af_add_t1 =  tax_rule.calculate_tax_3_after_adding_tax_1
	t3_af_add_t2 =   tax_rule.calculate_tax_3_after_adding_tax_2


	tax_rate_con = 0


	tax_rate_con = (1 + t1_r + t2_r 
						+ (t1_r * t2_af_add_t1 * t2_r) 
						+ t3_r + (t1_r * t3_af_add_t1 * t3_r) 
						+ (t2_r * t3_af_add_t2 * t3_r)
						+ (t1_r * t2_af_add_t1 * t2_r * t3_af_add_t2 * t3_r))


 
	tax_rate_con = tax_rate_con or 0


	price = amount /  tax_rate_con


	return  price


