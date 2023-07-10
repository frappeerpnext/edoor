# Copyright (c) 2023, Tes Pheakdey and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from edoor.api.frontdesk import get_working_day
from edoor.api.utils import update_reservation_folio, update_reservation_stay,update_reservation,get_base_rate
from frappe.utils import fmt_money
from frappe.utils.data import now

class FolioTransaction(Document):
	def validate(self):
		
		# when update note
		if hasattr(self,"is_update_note") and self.is_update_note:
			self.note_by = frappe.session.user
			self.note_modified = now()
		if not self.input_amount:
			frappe.throw("Please enter amount")

		if self.require_city_ledger_account==1:
			if not self.city_ledger:
				frappe.throw("Please select city ledger account")

		#check reservation status if allow to edit
		if frappe.db.get_value("Reservation Status",self.reservation_status, "allow_user_to_edit_information")==0:
			frappe.throw("{} reservation is not allow to change information".format(self.reservation_status) )
		
		#validate working day  
		if self.is_new():
			working_day = get_working_day(self.property)
			 
			if not working_day["name"]:
				frappe.throw("Please start working day")
			
			if not working_day["cashier_shift"]["name"]:
				frappe.throw("Please start cashier shift")
			

			self.working_day = working_day["name"]
			self.working_date = working_day["date_working_day"]
			self.cashier_shift = working_day["cashier_shift"]["name"]

			if not self.room_id:
				#get room info
				#1 get room from reservation room rate
				room_rate_data = frappe.get_list("Reservation Room Rate", fields=["room_type_id","room_id","room_type","room_number"],filters={"reservation_stay":self.reservation_stay,"date":self.posting_date})
			
				if room_rate_data:
					self.room_type_id =room_rate_data[0].room_type_id
					self.room_id =room_rate_data[0].room_id 
					self.room_number =room_rate_data[0].room_number 
					self.room_type =room_rate_data[0].room_type
				else:
					#get first row of room rate
					room_rate_data = frappe.get_list("Reservation Room Rate", fields=["room_type_id","room_id","room_type","room_number"],filters={"reservation_stay":self.reservation_stay}, limit_page_length=1)
					if room_rate_data:
						self.room_type_id =room_rate_data[0].room_type_id
						self.room_id =room_rate_data[0].room_id 
						self.room_number =room_rate_data[0].room_number 
						self.room_type =room_rate_data[0].room_type
				#end update room type and room number
		

		self.discount = self.discount if (self.discount or 0) >0 else 0

		if self.discount_type =="Percent" and self.discount>100:
			frappe.throw("Discount percent cannot greater than 100%")

		self.input_amount =float( self.input_amount or 0)

		self.price = self.input_amount
		self.quantity=float( self.quantity or 1)
		self.amount = (self.price or 0)  * self.quantity
	
 
				 
		self.discount = self.discount or 0
		
		if self.discount_type=="Percent":
			self.discount_amount =(float( self.price or 0 ) * self.quantity) * ((self.discount or 0) / 100.0)
			 
		else:
			self.discount_amount = self.discount or 0 

		#update discount account code and bank fee account
		account_doc = frappe.get_doc("Account Code", self.account_code)
		self.discount_account = account_doc.discount_account
		self.bank_fee_account = account_doc.bank_fee_account

		if self.tax_rule:
			tax_rule = frappe.get_doc("Tax Rule",self.tax_rule)
			self.tax_1_account = tax_rule.tax_1_account
			self.tax_2_account = tax_rule.tax_2_account
			self.tax_3_account = tax_rule.tax_3_account

			if self.rate_include_tax== "Yes":
				price = get_base_rate((self.input_amount )- (self.discount_amount/ self.quantity) ,tax_rule,self.tax_1_rate, self.tax_2_rate, self.tax_3_rate)
				self.price = price + self.discount_amount
				self.amount = (self.price * self.quantity ) 
			else:
				self.amount = ( self.price * self.quantity)  
			
			#tax 1
			self.taxable_amount_1 = self.amount * ((tax_rule.percentage_of_price_to_calculate_tax_1 or 100)/100)
			
			self.taxable_amount_1 = self.taxable_amount_1 if tax_rule.calculate_tax_1_after_discount == 0 and self.rate_include_tax =='No'  else self.taxable_amount_1 - self.discount_amount
		 
			self.tax_1_amount = self.taxable_amount_1 * self.tax_1_rate / 100
			#tax 2
			self.taxable_amount_2 = self.amount * ((tax_rule.percentage_of_price_to_calculate_tax_2 or 100)/100)
			self.taxable_amount_2 = self.taxable_amount_2 if tax_rule.calculate_tax_2_after_discount == 0  and self.rate_include_tax =='No'  else self.taxable_amount_2 - self.discount_amount
			self.taxable_amount_2 = self.taxable_amount_2  if tax_rule.calculate_tax_2_after_adding_tax_1 == 0 else self.taxable_amount_2 + self.tax_1_amount
			self.tax_2_amount = self.taxable_amount_2 * self.tax_2_rate / 100
			#tax 3
			self.taxable_amount_3 = self.amount * ((tax_rule.percentage_of_price_to_calculate_tax_3 or 100)/100)
			self.taxable_amount_3 = self.taxable_amount_3 if tax_rule.calculate_tax_3_after_discount == 0  and self.rate_include_tax =='No'  else self.taxable_amount_3 - self.discount_amount
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
		
		if self.discount_amount> self.input_amount:
			frappe.throw("Discount amount cannot greater than amount")
		
		self.bank_fee = self.bank_fee or 0
		
		self.bank_fee_amount = (self.amount or 0) * (self.bank_fee or 0) / 100

		self.amount = (self.amount or 0) + (self.bank_fee_amount or 0)
		
		
		self.total_amount = (self.amount or 0) - (self.discount_amount or 0) + (self.total_tax or 0)  
	
		if not self.parent_reference:
			update_sub_account_description(self)

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
		add_sub_account_to_folio_transaction(self,account_doc.discount_account, self.discount_amount,"Discount from folio transaction: {}. Date: {}. Room: {}({})".format(self.name,self.posting_date,self.room_number,self.room_type ))
		if account_doc.discount_account:
			self.discount_account = account_doc.discount_account
			if self.discount_amount == 0:
				self.discount_description = ""
			else:
				account_name = frappe.db.get_value("Account Code", account_doc.discount_account,"account_name")
				if self.discount_type=="Percent":
					self.discount_description = '{} - {}%'.format(account_name, self.discount)
				else:
					self.discount_description = '{}'.format(account_name)
		
		#tax 
		if self.tax_rule:
			tax_rule = frappe.get_doc("Tax Rule",self.tax_rule)
			add_sub_account_to_folio_transaction(self,tax_rule.tax_1_account, self.tax_1_amount,"Tax breakdown from folio transaction: {}".format(self.name))
			add_sub_account_to_folio_transaction(self,tax_rule.tax_2_account, self.tax_2_amount,"Tax breakdown from folio transaction: {}".format(self.name))
			add_sub_account_to_folio_transaction(self,tax_rule.tax_3_account, self.tax_3_amount,"Tax breakdown from folio transaction: {}".format(self.name))
			 		
		add_sub_account_to_folio_transaction(self,account_doc.bank_fee_account, self.bank_fee_amount,"Credit card processing fee")
		
		

		#update folio transaction to reservation folio
		update_reservation_folio(self.folio_number, None, False)
		
		#update to reservation stay and reservation
		if not self.parent_reference:	 
			update_reservation_stay(self.reservation_stay,None, False)
			
			update_reservation(self.reservation,None, False)
			
			# frappe.enqueue("edoor.api.utils.update_reservation_stay", queue='short', name=self.reservation_stay, doc=None, run_commit=False)
			# frappe.enqueue("edoor.api.utils.update_reservation", queue='short', name=self.reservation, doc=None, run_commit=False)
	
		

	def on_trash(self):
		#check reservation status if allow to edit
		if frappe.db.get_value("Reservation Status",self.reservation_status, "allow_user_to_edit_information")==0:
			frappe.throw("{} reservation is not allow to delete this transaction".format(self.reservation_status) )
		

		#use for validate record prevent user to delete record

		#frappe.throw("You cannot delete me")
	def after_delete(self):
	
		frappe.db.delete("Folio Transaction", filters={"parent_reference":self.name})
		update_reservation_folio(self.folio_number, None, False)
		frappe.enqueue("edoor.api.utils.update_reservation_stay", queue='short', name=self.reservation_stay, doc=None, run_commit=False)
		frappe.enqueue("edoor.api.utils.update_reservation", queue='short', name=self.reservation, doc=None, run_commit=False)

def update_sub_account_description(self):
	if self.discount_account:
		if self.discount_amount == 0:
			self.discount_description = ""
		else:
			account_name = frappe.db.get_value("Account Code", self.discount_account,"account_name")
			if self.discount_type=="Percent":
				self.discount_description = '{} - {}%'.format(account_name, self.discount)
			else:
				self.discount_description = '{}'.format(account_name)
	
		
	if self.tax_1_account:
		if self.tax_1_rate == 0:
			self.tax_1_description = ""
		else:
			account_name = frappe.db.get_value("Account Code", self.tax_1_account,"account_name")
			self.tax_1_description = '{} - {}%'.format(account_name, self.tax_1_rate)
	
	if self.tax_2_account:
		if self.tax_2_rate == 0:
			self.tax_2_description = ""
		else:
			account_name = frappe.db.get_value("Account Code", self.tax_2_account,"account_name")
			self.tax_2_description = '{} - {}%'.format(account_name, self.tax_2_rate)
	
	if self.tax_3_account:
		if self.tax_3_rate == 0:
			self.tax_3_description = ""
		else:
			account_name = frappe.db.get_value("Account Code", self.tax_3_account,"account_name")
			self.tax_3_description = '{} - {}%'.format(account_name, self.tax_3_rate)

	if self.bank_fee_account:
	 
		if self.bank_fee == 0:
			self.bank_fee_description = ""
		else:
			account_name = frappe.db.get_value("Account Code", self.bank_fee_account,"account_name")
			self.bank_fee_description = '{} - {}% of {}'.format(account_name, self.bank_fee, fmt_money(amount=self.input_amount, currency=frappe.db.get_default("currency")))
		

def add_sub_account_to_folio_transaction(self, account_code, amount,note):
	if account_code:
		docs = frappe.db.get_list("Folio Transaction",filters={"account_code": account_code,"parent_reference":self.name })
		if docs:
			frappe.db.set_value("Folio Transaction",docs[0].name,
			{
				"quantity":1,
				"amount":amount or 0,
				"input_amount":amount or 0,
				"posting_date": self.posting_date,
				"note":note
			}
			)
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
					"quantity":1,
					'input_amount': amount,
					'amount': amount,
					"note":note,
					"parent_reference":self.name,
					"is_auto_post":self.is_auto_post

				}).insert()
