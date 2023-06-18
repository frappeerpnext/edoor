# Copyright (c) 2023, Tes Pheakdey and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from edoor.api.frontdesk import get_working_day
from edoor.api.utils import update_reservation_stay,update_reservation

class FolioTransaction(Document):
	def validate(self):
		#validate working day 
		if self.is_new():
			working_day = get_working_day(self.property)
			if not working_day["name"]:
				frappe.throw("Please start working")
			
			if not working_day["cashier_shift"]["name"]:
				frappe.throw("Please start cashier shift")
			

			self.working_day = working_day["name"]
			self.working_date = working_day["date_working_day"]
			self.cashier_shift = working_day["cashier_shift"]["name"]
		
		self.discount = self.discount if (self.discount or 0) >0 else 0

		if self.discount_type =="Percent" and self.discount>100:
			frappe.throw("Discount percent cannot greater than 100%")

		self.input_amount =float( self.input_amount or 0)
		self.amount = self.input_amount or 0
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
		else:
			self.rate_include_tax = 'No'
		
		if self.discount_amount> self.input_amount:
			frappe.throw("Discount amount cannot greater than amount")
		
		self.bank_fee = self.bank_fee or 0
		
		self.bank_fee_amount = (self.amount or 0) * (self.bank_fee or 0) / 100

		self.amount = (self.amount or 0) + (self.bank_fee_amount or 0)
		
		
		self.total_amount = (self.amount or 0) - (self.discount_amount or 0) + (self.total_tax or 0)  

	def on_update(self):
		#we use this method add folio transaction breakown
		#1. self is main account transaction
		#2. Discount Account
		#3. Tax 1 Account 
		#4. Tax 2 Account 
		#5. Tax 3 Account 
		#6. Bank Fee Account
		account_doc = frappe.get_doc("Account Code", self.account_code)
		#discount
		add_sub_account_to_folio_transaction(self,account_doc.discount_account, self.discount_amount,"Discount from folio transaction: {}. Date: {}. Room: {}({})".format(self.name,self.posting_date,self.room_number,self.room_type_name ))
		
		#tax 
		if self.tax_rule:
			tax_rule = frappe.get_doc("Tax Rule",self.tax_rule)
			add_sub_account_to_folio_transaction(self,tax_rule.tax_1_account, self.tax_1_amount,"Tax breakdown from folio transaction: {}".format(self.name))
			add_sub_account_to_folio_transaction(self,tax_rule.tax_2_account, self.tax_2_amount,"Tax breakdown from folio transaction: {}".format(self.name))
			add_sub_account_to_folio_transaction(self,tax_rule.tax_3_account, self.tax_3_amount,"Tax breakdown from folio transaction: {}".format(self.name))

		#bank fee
		add_sub_account_to_folio_transaction(self,account_doc.bank_fee_account, self.bank_fee_amount,"Credit card processing fee")

		#update to reservation stay and reservation
		if not self.parent_reference:
			update_reservation_stay(self.reservation_stay,None, False)


	def on_trash(self):
		pass
		#use for validate record prevent user to delete record

		#frappe.throw("You cannot delete me")
	def after_delete(self):
		frappe.db.delete("Folio Transaction", filters={"parent_reference":self.name})

		
def add_sub_account_to_folio_transaction(self, account_code, amount,note):
	if account_code:
		docs = frappe.db.get_list("Folio Transaction",filters={"account_code": account_code,"parent_reference":self.name })
		if docs:
			frappe.db.set_value("Folio Transaction",docs[0].name,"amount",amount or 0)
		else:
			if amount> 0:
				doc = frappe.get_doc({
					'doctype': 'Folio Transaction',
					'reference_number': self.reference_number,
					'naming_series':self.name + '.-.##',
					'folio_number':self.folio_number,
					'property': self.property,
					'reservation': self.reservation,
					'reservation_stay': self.reservation_stay,
					'posting_date': self.posting_date,
					'working_day': self.working_day,
					'cashier_shift': self.cashier_shift,
					'working_date': self.working_date,
					'account_code': account_code,
					'input_amount': amount,
					'amount': amount,
					"note":note,
					"parent_reference":self.name

				}).insert()

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
