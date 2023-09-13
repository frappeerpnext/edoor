# Copyright (c) 2023, Tes Pheakdey and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from edoor.api.frontdesk import get_working_day
from edoor.api.utils import update_city_ledger, update_reservation_folio, update_reservation_stay,update_reservation,get_base_rate
from frappe.utils import fmt_money
from frappe.utils.data import now

class FolioTransaction(Document):
	def validate(self):
		if not self.is_new():
			if self.is_auto_post ==1:
				frappe.throw("You cannot edit auto post transaction")
		# when update note
		if hasattr(self,"is_update_note") and self.is_update_note:
			self.note_by = frappe.session.user
			self.note_modified = now()
		if not self.input_amount:
			if not hasattr(self,"valiate_input_amount"):
				frappe.throw("Please enter amount")
 
		if self.require_city_ledger_account==1:
			if self.is_new():
				if not self.city_ledger:
					frappe.throw("Please select city ledger account")
			else:
				frappe.throw("You cannot edit {} transaction.".format(self.account_name))
		#check reservation status if allow to edit
		if frappe.db.get_value("Reservation Status",self.reservation_status, "allow_user_to_edit_information")==0:
			frappe.throw("{} reservation is not allow to change information".format(self.reservation_status) )
		
		if self.require_select_a_folio==1:
			if not self.folio_number:
				frappe.throw("Please select a folio number")
			if self.is_new():
				target_folio_doc = frappe.get_doc("Reservation Folio",self.folio_number)
				if target_folio_doc.status =='Closed':
					frappe.throw("Target Folio Number {} is already closed".format(target_folio_doc.name))
				self.note =   "{} Folio balance transfer to folio # {}, room:{} ".format(self.note or "", target_folio_doc.name, target_folio_doc.rooms),
			else:
				frappe.throw("You cannot edit {} transaction".format(self.account_name))
	
				
		#validate working day  
		if self.is_new():
			
			ref_doc = frappe.get_doc(self.transaction_type, self.transaction_number)
			if self.transaction_type =="Reservation Folio":
				self.property = ref_doc.property
				self.reservation = ref_doc.reservation
				self.reservation_stay = ref_doc.reservation_stay
				self.is_master_folio = ref_doc.is_master
				 

			elif self.transaction_type == "Reservation":
				self.property = ref_doc.property
			

			if not self.property:
				if self.reservation:
					self.property = frappe.db.get_value("Reservation", self.reservation, "property")

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
				if self.reservation_stay:
				 	
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
			self.tax_1_rate = self.tax_1_rate or 0
			self.tax_2_rate = self.tax_2_rate or 0
			self.tax_3_rate = self.tax_3_rate or 0

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
	def after_insert(self):
		update_folio_transaction(self)

		if self.require_city_ledger_account==1 and  self.city_ledger :
			post_to_city_ledger(self)


	def on_update(self):
		if not self.is_new():
			update_folio_transaction(self)
		

	def on_trash(self):
		#if this transaction is auto post 
		if self.is_auto_post:
			if (frappe.db.get_default("allow_user_to_daddelete_auto_post_transaction") or 0)==0:
				frappe.throw("Auto post transaction is not allow to delete.")
		#check reservation status if allow to edit
		if frappe.db.get_value("Reservation Status",self.reservation_status, "allow_user_to_edit_information")==0:
			frappe.throw("{} reservation is not allow to delete this transaction".format(self.reservation_status) )
		
		#validate delete folio transaction that have reference to folio transaction like folio transfer or city ledget
		account_doc = frappe.get_doc("Account Code",self.account_code)
		if account_doc.require_select_a_folio:
			sql = "select name, transaction_number from `tabFolio Transaction` where reference_folio_transaction='{}'".format(self.name)
			
			target_folio_transaction = frappe.db.sql(sql,as_dict=1)

			if target_folio_transaction:
				#validate folio status
				if frappe.get_value("Reservation Folio", target_folio_transaction[0]["transaction_number"], "status")=="Closed":
					frappe.throw("You cannot delete this record. Because reference to Folio number {} and this folio is already closed".format( target_folio_transaction[0]["transaction_number"]))
				
				

		#use for validate record prevent user to delete record

		#frappe.throw("You cannot delete me")
	
	def after_delete(self):
	
		frappe.db.delete("Folio Transaction", filters={"parent_reference":self.name})
		

		if self.transaction_type=='Reservation Folio':
			update_reservation_folio(self.transaction_number, None, False)


		frappe.enqueue("edoor.api.utils.update_reservation_stay", queue='short', name=self.reservation_stay, doc=None, run_commit=False)
		frappe.enqueue("edoor.api.utils.update_reservation", queue='short', name=self.reservation, doc=None, run_commit=False)

		#update reservation stay and reservation of target folio transfer after delete
		sql = "select distinct transaction_type, transaction_number, reservation, reservation_stay from `tabFolio Transaction` where reference_folio_transaction='{}'".format(self.name)
		data = frappe.db.sql(sql,as_dict=1)


		frappe.db.delete("Folio Transaction", filters={"reference_folio_transaction":self.name})
		for d in data:
			if d["transaction_type"] =="Reservation Folio":
				frappe.enqueue("edoor.api.utils.update_reservation_folio", queue='short', name=d["transaction_number"], doc=None, run_commit=False)
			
			frappe.enqueue("edoor.api.utils.update_reservation_stay", queue='short', name=d["reservation_stay"], doc=None, run_commit=False)
			frappe.enqueue("edoor.api.utils.update_reservation", queue='short', name=d["reservation"], doc=None, run_commit=False)
		
		#check if folio transaction is city ledger then update city leder summary
		if self.city_ledger:
			frappe.db.delete("Folio Transaction", filters={"reference_folio_transaction":self.name})
			frappe.enqueue("edoor.api.utils.update_city_ledger", queue='short', name=self.city_ledger, doc=None, run_commit=False)
		

			

		 

def update_folio_transaction(self):
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
	if self.transaction_type=="Reservation Folio":
		update_reservation_folio(self.transaction_number, None, False)
	
	#update to reservation stay and reservation
	if not self.parent_reference:	
		if self.transaction_type=="Reservation Folio": 
			update_reservation_stay(self.reservation_stay,None, False)
			update_reservation(self.reservation,None, False)
		
		# frappe.enqueue("edoor.api.utils.update_reservation_stay", queue='short', name=self.reservation_stay, doc=None, run_commit=False)
		# frappe.enqueue("edoor.api.utils.update_reservation", queue='short', name=self.reservation, doc=None, run_commit=False)
	
	if self.transaction_type =="City Ledger":
		update_city_ledger(self.transaction_number, None, False)

	#check if it is is folio transfer then queue add record to folio transaction
	if self.require_select_a_folio==1: 
			if self.folio_number and  self.is_auto_post==0:
				frappe.enqueue("edoor.edoor.doctype.folio_transaction.folio_transaction.transfer_folio_balance", queue='short', self=self)



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
						'transaction_type':self.transaction_type,
						'transaction_number':self.transaction_number,
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


@frappe.whitelist()
def transfer_folio_balance(self):
	folio_doc = frappe.get_doc("Reservation Folio", self.folio_number)
	doc = frappe.get_doc({
		'doctype': 'Folio Transaction',
		'transaction_type':self.transaction_type,
		'transaction_number':self.folio_number,
		'folio_number':self.transaction_number,
		'reference_number': self.name,
		'property': folio_doc.property,
		'reservation': folio_doc.reservation,
		'reservation_stay': folio_doc.reservation_stay,
		'posting_date': self.posting_date,
		'working_day': self.working_day,
		'cashier_shift': self.cashier_shift,
		'working_date': self.working_date,
		'account_code': self.account_code,
		'type': "Credit" if self.type =='Debit' else 'Debit', 
		"quantity":1,
		'input_amount': self.input_amount,
		"note":"Folio balance transfer from folio # {}, room:{} ".format(self.transaction_number, self.room_number),
		"is_auto_post":1,
		"require_select_a_folio": 0,
		"reference_folio_transaction":self.name
	}).insert()

	
@frappe.whitelist()
def post_to_city_ledger(self):
	doc = frappe.get_doc({
		'doctype': 'Folio Transaction',
		'transaction_type':"City Ledger",
		'transaction_number':self.city_ledger,
		'folio_number':self.transaction_number,
		'reference_number': self.name,
		'property': self.property,
		'posting_date': self.posting_date,
		'working_day': self.working_day,
		'cashier_shift': self.cashier_shift,
		'working_date': self.working_date,
		'account_code': self.account_code,
		'type': "Credit" if self.type =='Debit' else 'Debit', 
		"quantity":1,
		'input_amount': self.input_amount,
		"note":"City Ledger transfer from folio # {}, room:{} ".format(self.transaction_number, self.room_number),
		"is_auto_post":1,
		"require_city_ledger_account": 0,
		"reference_folio_transaction":self.name
	}).insert()


	