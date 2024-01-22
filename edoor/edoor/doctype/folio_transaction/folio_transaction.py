# Copyright (c) 2023, Tes Pheakdey and contributors
# For license information, please see license.txt\

import frappe
from frappe.model.document import Document
from edoor.api.frontdesk import get_working_day
from edoor.api.utils import add_audit_trail, check_user_permission, update_city_ledger, update_deposit_ledger, update_desk_folio, update_payable_ledger, update_reservation_folio, get_base_rate
from frappe.utils import fmt_money
from frappe.utils.data import add_to_date, getdate,now
from epos_restaurant_2023.inventory.inventory import add_to_inventory_transaction, check_uom_conversion, get_product_cost, get_stock_location_product, get_uom_conversion, update_product_quantity
from frappe import _

class FolioTransaction(Document):
	def validate(self):
		 
		if not self.account_code:
			frappe.throw("Please select an account code")

		if not self.is_new():
				if self.is_auto_post ==1:
					self.is_night_audit_posting = 1
					if not hasattr(self,"ignore_validate_auto_post"):
						frappe.throw("You cannot edit auto post transaction")
		
 
		if self.required_select_product and not self.product:
			frappe.throw("Please select product code.")
			
		 
		#validate folio status
		 
		if not  self.flags.ignore_validate_close_folio:
			if self.transaction_type =='Reservation Folio' :
				if frappe.db.get_value("Reservation Folio", self.transaction_number, "status") =='Closed':
					frappe.throw(f"This folio {self.transaction_number} is already closed")
				
		# when update note
		if hasattr(self,"is_update_note") and self.is_update_note:
			self.note_by = frappe.session.user
			self.note_modified = now()
		if not self.input_amount:
			if not hasattr(self,"valiate_input_amount"):
				frappe.throw("Please enter amount")
		
		#pheakdey
		if self.target_transaction_type:
			if self.is_new():
				if not self.target_transaction_number:
					frappe.throw("Please select " + self.target_transaction_type)
				target_doc = frappe.get_doc(self.target_transaction_type,self.target_transaction_number)
				if not self.target_account_code:
					frappe.throw("This account code does not have target account code. Please config target account in account code setting.")
					
				#check target document status
				
				if target_doc.status =='Closed':
					frappe.throw(f"Target {self.target_transaction_type} Number {self.target_transaction_number} is already closed")

				if self.target_transaction_type=="Reservation Folio":
					self.note =   "{} Folio balance transfer to folio # {}, room:{} ".format(self.note or "", target_doc.name, target_doc.rooms),
	
			else:
				frappe.throw("You cannot edit {} transaction.".format(self.account_name))

			#chekc if target transaction type is city ledger then get city ledger name and city ledger type and update to table
			if self.target_transaction_type=="City Ledger":
				city_ledger_doc = frappe.get_doc("City Ledger", self.target_transaction_number)

				self.city_ledger_name = city_ledger_doc.city_ledger_name
				self.city_ledger_type= city_ledger_doc.city_ledger_type
			else:
				self.city_ledger_name =""
				self.city_ledger_type= ""
		else:
			self.city_ledger_name = ""
			self.city_ledger_type= ""

		#check if doc have source transaction then then mean that this transaction is transfer from 
		if self.source_transaction_type:
				self.note = f"{_(self.transaction_type)} transfer from {_(self.source_transaction_type)} #: {self.source_transaction_number}, Reference Source Transaction Number: {self.reference_folio_transaction}"

		#check reservation status if allow to edit
		if self.reservation_status:
			if frappe.db.get_value("Reservation Status",self.reservation_status, "allow_user_to_edit_information")==0:
				frappe.throw("{} reservation is not allow to change information".format(self.reservation_status) )

		
		
		
	
				
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
			elif self.transaction_type == "Deposit Ledger":
				#set default guest and room to folio transaction when we add deposit ledger transaction
				#validate if deposit ledger is still open
				deposit_ledger_doc = frappe.get_doc("Deposit Ledger",self.transaction_number)
				if deposit_ledger_doc.status =="Closed":
					frappe.throw("You cannot post transaction to the close deposit ledger")

				
				self.guest = deposit_ledger_doc.guest
				self.guest_name =  deposit_ledger_doc.guest_name
				self.room_id =  deposit_ledger_doc.room_id
				self.room_number =  deposit_ledger_doc.room_number


			if not self.property:
				if self.reservation:
					self.property = frappe.db.get_value("Reservation", self.reservation, "property")

			working_day = get_working_day(self.property)
			 
			if not working_day["name"]:
				frappe.throw("Please start working day")
			
			if not working_day["cashier_shift"]["name"]:
				frappe.throw("Please start cashier shift")

			#validate record for back date trasaction

			if getdate(working_day["date_working_day"])> getdate(self.posting_date):
				check_user_permission("role_for_back_date_transaction","Sorry you don't have permission to perform back date transaction")


			

			self.working_day = working_day["name"]
			self.working_date = working_day["date_working_day"]
			self.cashier_shift = working_day["cashier_shift"]["name"]

			#check if not guest selected then add reservation folio guest to this folio transaction
			if self.transaction_type == "Reservation Folio":

				if not self.guest:
					guest, guest_name = frappe.db.get_value('Reservation Folio',self.transaction_number , ['guest', 'guest_name'])
					self.guest = guest
					self.guest_name = guest_name



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
			else:
				#room id is manually set so we need to get room type id set to this folio transaction
				room = frappe.get_doc("Room", self.room_id)
				self.room_type_id = room.room_type_id
				self.room_type = room.room_type



			 
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

		if account_doc.show_quantity_in_report:
			self.report_quantity = self.quantity

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
			self.taxable_amount_2 = self.amount or 0 * ((tax_rule.percentage_of_price_to_calculate_tax_2 or 100)/100)
			self.taxable_amount_2 = self.taxable_amount_2 if tax_rule.calculate_tax_2_after_discount == 0  and self.rate_include_tax =='No'  else self.taxable_amount_2 - self.discount_amount
			self.taxable_amount_2 = self.taxable_amount_2  if tax_rule.calculate_tax_2_after_adding_tax_1 == 0 else self.taxable_amount_2 + self.tax_1_amount
			

			self.tax_2_amount = self.taxable_amount_2 * self.tax_2_rate / 100
			#tax 3
			self.taxable_amount_3 = self.amount or 0
			
			self.taxable_amount_3 = self.taxable_amount_3 if tax_rule.calculate_tax_3_after_discount == 0  and self.rate_include_tax =='No'  else self.taxable_amount_3 - self.discount_amount
			self.taxable_amount_3 = self.taxable_amount_3  if tax_rule.calculate_tax_3_after_adding_tax_1 == 0 else self.taxable_amount_3 + self.tax_1_amount
			self.taxable_amount_3 = self.taxable_amount_3  if tax_rule.calculate_tax_3_after_adding_tax_2 == 0 else self.taxable_amount_3 + self.tax_2_amount
			self.tax_3_amount = self.taxable_amount_3 * self.tax_3_rate / 100
			
			self.taxable_amount_3 = self.taxable_amount_3 * ((tax_rule.percentage_of_price_to_calculate_tax_3 or 100)/100)

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

		#auto set room_type_alias
		if self.room_id and not self.room_type_id:
			room_type_id, room_type,room_type_alias = frappe.db.get_value("Room", self.room_id, ["room_type_id","room_type","room_type_alias"])
			self.room_type_id = room_type_id
			self.room_type = room_type
			self.room_type_alias = room_type_alias

		if self.room_type_id:
			
			if not self.room_type_alias:
				
				self.room_type_alias = frappe.db.get_value("Room Type",self.room_type_id,"alias")

		else:
			self.room_type=""
			self.room_type_alias=""

		
		#udpate fetche from field
		update_fetch_from_field(self)
		#validate update report descript
		update_report_description_field(self)


	

		

	def after_insert(self):
		 
		if self.target_transaction_type and  self.target_transaction_number:
			note = ""
			# if self.target_transaction_type:
			# 	note = f"{_(self.transaction_type)} transfer to {_(self.target_transaction_type)} #: {self.target_transaction_number}, room: {self.room_number}"	
	 

			post_transaction_to_target_transaction_type(self)
			
 
		#add audit trail
		 
		if not self.parent_reference:
			content =f"Post {self.account_group_name} to {self.transaction_type}. {self.transaction_type} #: {self.transaction_number}"
			if self.transaction_type=="Reservation Folio":
				if self.target_transaction_type:
					content = content +  f", {'To folio: ' + self.target_transaction_number + ',' if self.target_transaction_number else '' } Reservation Stay: {self.reservation_stay}, Reservation: {self.reservation}, Account: {self.account_code}-{self.account_name}, Amount: {frappe.format(self.amount,{'fieldtype':'Currency'})}"

				if self.source_transaction_type:
					content = content +  f", From Folio: {self.source_transaction_number} , Reservation Stay: {self.reservation_stay}, Reservation: {self.reservation}, Account: {self.account_code}-{self.account_name}, Amount: {frappe.format(self.amount,{'fieldtype':'Currency'})}"
			
			elif self.transaction_type=="Deposit Ledger":
				content = content + f", Account: {self.account_code}-{self.account_name}, Amount: {frappe.format(self.amount,{'fieldtype':'Currency'})}"
			else:
				content = content + f", Account: {self.account_code}-{self.account_name}, Amount: {frappe.format(self.amount,{'fieldtype':'Currency'})}"

			# frappe.enqueue("edoor.api.utils.add_audit_trail",queue='short', data =[{
			# 	"comment_type":"Created",
			# 	"custom_audit_trail_type":"Created",
			# 	"custom_icon":"pi pi-dollar",
			# 	"subject":"Post " + self.account_group_name,
			# 	"reference_doctype":"Folio Transaction",
			# 	"reference_name":self.name,
			# 	"content":content
			# }])

			add_audit_trail([{
				"comment_type":"Created",
				"custom_audit_trail_type":"Created",
				"custom_icon":"pi pi-dollar",
				"subject":"Post " + self.account_group_name,
				"reference_doctype":"Folio Transaction",
				"reference_name":self.name,
				"content":content
			}])
	

		#update to inventory
		if self.product:
			update_inventory(self)



	def on_update(self):
		if not hasattr(self,"ignore_update_folio_transaction"):
			 
			update_folio_transaction(self)

		
		
		 
	def on_trash(self):
		#if this transaction is auto post 

		if self.is_auto_post:
			if (frappe.db.get_default("allow_user_to_daddelete_auto_post_transaction") or 0)==0:
				frappe.throw("Auto post transaction is not allow to delete.")
		
		#check reservation status if allow to edit
		if self.reservation_status:
			if frappe.db.get_value("Reservation Status",self.reservation_status, "allow_user_to_edit_information")==0:
				frappe.throw("{} reservation is not allow to delete this transaction".format(self.reservation_status) )
			
		#validate record for back date trasaction
		working_day = get_working_day(self.property)
		if getdate(working_day["date_working_day"])> getdate(self.posting_date):
			check_user_permission("role_for_back_date_transaction","Sorry you don't have permission to perform back date transaction")


		#validate delete folio transaction that have reference to folio transaction like folio transfer or city ledget
		
		account_doc = frappe.get_doc("Account Code",self.account_code)
		if self.target_transaction_number:
			sql = "select name, transaction_number from `tabFolio Transaction` where reference_folio_transaction='{}'".format(self.name)
			
			target_folio_transaction = frappe.db.sql(sql,as_dict=1)

			if target_folio_transaction:
				#validate folio status
				if frappe.get_value(self.target_transaction_type, target_folio_transaction[0]["transaction_number"], "status")=="Closed":
					frappe.throw("You cannot delete this record. Because reference to Folio number {} and this folio is already closed".format( target_folio_transaction[0]["transaction_number"]))
				
				

		#use for validate record prevent user to delete record

		#frappe.throw("You cannot delete me")
	
	def after_delete(self):
		reservation_names=[]
		reservation_stay_names=[]
	
		frappe.db.delete("Folio Transaction", filters={"parent_reference":self.name})
		

		if self.transaction_type=='Reservation Folio':
			update_reservation_folio(self.transaction_number, None, False)
		elif self.transaction_type=='Deposit Ledger':
			update_deposit_ledger(self.transaction_number, None, False)
		elif self.transaction_type=='Desk Folio':
			update_desk_folio(self.transaction_number, None, False)	
		elif self.transaction_type=='Payable Ledger':
			update_payable_ledger(self.transaction_number, None, False)

		
		
		reservation_names.append(self.reservation)
		reservation_stay_names.append(self.reservation_stay)

		# frappe.enqueue("edoor.api.utils.update_reservation_stay_and_reservation", queue='short', reservation_stay=self.reservation_stay,reservation=self.reservation)

		#update reservation stay and reservation of target folio transfer after delete
		sql = "select distinct transaction_type, transaction_number, reservation, reservation_stay from `tabFolio Transaction` where reference_folio_transaction='{}'".format(self.name)
		data = frappe.db.sql(sql,as_dict=1)


		frappe.db.delete("Folio Transaction", filters={"reference_folio_transaction":self.name})
		for d in data:
			if d["transaction_type"] =="Reservation Folio":
				frappe.enqueue("edoor.api.utils.update_reservation_folio", queue='short', name=d["transaction_number"], doc=None, run_commit=False)
			
			reservation_names.append(d["reservation"])
			reservation_stay_names.append(d["reservation_stay"])
			# frappe.enqueue("edoor.api.utils.update_reservation_stay_and_reservation", queue='short', reservation_stay=d["reservation_stay"],reservation=d["reservation"])

		
		#check if folio transaction is city ledger then update city leder summary
		if self.target_transaction_type == "City Ledger" and  self.target_transaction_number :
			frappe.db.delete("Folio Transaction", filters={"reference_folio_transaction":self.name})
			frappe.enqueue("edoor.api.utils.update_city_ledger", queue='short', name=self.target_transaction_number, doc=None, run_commit=False)
		

		#add to audit trail
		working_day = get_working_day(self.property)
		comment = {
			"comment_type":"Deleted",
			"subject":"Delete Folio Transaction",
			"reference_doctype":self.transaction_type,
			"reference_name":self.transaction_number,
			"custom_property":self.property,
			"custom_audit_trail_type":"Delete",
			"custom_icon":"pi pi-trash",
			"custom_posting_date": working_day["date_working_day"]
		}
		if self.transaction_type =="Reservation Folio":
			comment["content"] = f"Folio Transaction #: {self.name} has been deleted, Folio #:<a data-action='view_folio_detail' data-name='{self.transaction_number}'>{self.transaction_number}</a>, Reservation Stay #: <a  data-action='view_reservation_stay_detail' data-name='{self.reservation_stay}'>{self.reservation_stay}</a>,  Reservation # <a data-action='view_reservation_detail' data-name='{self.reservation}'>{self.reservation}'</a>, Guest: <a data-action='view_guest_detail' data-name='{self.guest}'> {self.guest} - {self.guest_name}</a>"
		else:
			comment["content"] = f"Folio Transaction #: {self.name} has been deleted, "
			if self.reservation_stay:
				comment["content"] = comment["content"] +  f"Reservation Stay #: <a  data-action='view_reservation_stay_detail' data-name='{self.reservation_stay}'>{self.reservation_stay}</a>, "
			if self.reservation:
				comment["content"] = comment["content"] +  f"Reservation # <a data-action='view_reservation_detail' data-name='{self.reservation}'>{self.reservation}'</a>, " 
				
			if self.guest:
				comment["content"] = comment["content"] +  f"Guest: <a data-action='view_guest_detail' data-name='{self.guest}'> {self.guest} - {self.guest_name}</a>"
				
			
		if (self.deleted_note):
			comment["content"] = comment["content"] + "<br /> Note: " + self.deleted_note

		if len(reservation_names)> 0 or len(reservation_stay_names)> 0:
			frappe.enqueue("edoor.api.utils.update_reservation_stay_and_reservation", queue='short', reservation_stay=reservation_stay_names,reservation=reservation_names)

		frappe.enqueue("edoor.api.utils.add_audit_trail",queue='long', data =[comment])
	 
def update_fetch_from_field(self):
	if self.guest:
		guest_name, guest_type,nationality = frappe.db.get_value("Customer",self.guest,["customer_name_en","customer_group","country"])
		self.guest_name = guest_name
		self.guest_type = guest_type
		self.nationality = nationality
	else:
		self.guest_name = ""
		self.guest_type = ""
		self.nationality = ""

	if self.business_source:
		self.business_source_type = frappe.db.get_value("Business Source", self.business_source,"business_source_type")
	else:
		self.business_source_type = ""
	

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
	elif self.transaction_type =="City Ledger":
		update_city_ledger(self.transaction_number, None, False)
	elif self.transaction_type =="Deposit Ledger":
		update_deposit_ledger(self.transaction_number, None, False)
	elif self.transaction_type=='Desk Folio':		
		update_desk_folio(self.transaction_number, None, False)
	elif self.transaction_type=='Payable Ledger':
		update_payable_ledger(self.transaction_number, None, False)
	
	
	#update to reservation stay and reservation

	if not self.parent_reference:	
		if self.transaction_type=="Reservation Folio": 
			if not self.flags.ignore_update_reservation:
				frappe.enqueue("edoor.api.utils.update_reservation_stay_and_reservation", queue='short', reservation_stay=self.reservation_stay,reservation=self.reservation)


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
						'property': self.property,
						'room_type_id':self.room_type_id,
						'room_type':self.room_type,
						'room_number':self.room_number,
						'room_id':self.room_id,
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
						"is_auto_post":self.is_auto_post,
						"is_night_audit_posting":self.is_night_audit_posting,
						"reservation_room_rate": self.reservation_room_rate
					}).insert()
					



@frappe.whitelist()
def post_transaction_to_target_transaction_type(self,):
	doc = frappe.get_doc({
		'doctype': 'Folio Transaction',
		'transaction_type': self.target_transaction_type,
		'transaction_number':self.target_transaction_number,
		'reference_number': self.name,
		'property': self.property,
		'posting_date': self.posting_date,
		'working_day': self.working_day,
		'cashier_shift': self.cashier_shift,
		'working_date': self.working_date,
		'account_code': self.target_account_code,
		'account_group_name': self.account_group_name,
		'account_group': self.account_group,
		'type': self.target_account_type,
		"quantity":self.quantity,
		'input_amount': self.input_amount,
		"is_auto_post":1,
		"guest":self.guest,
		"guest_name":self.guest_name,
		"room_number":self.room_number,
		"room_type":self.room_type,
		"room_id":self.room_id,
		"room_type_id":self.room_type_id,
		"reservation_stay":self.reservation_stay,
		"reservation":self.reservation,
		"reference_folio_transaction":self.name,
		"source_transaction_number": self.transaction_number,
		"source_transaction_type": self.transaction_type
	}).insert()

def update_report_description_field(self):
	self.report_description = self.account_name
	if self.target_transaction_type:
		if self.target_transaction_type=='City Ledger':
			self.report_description = "{} (to {})".format(self.report_description, self.city_ledger_name)
		else:
			self.report_description = "{} (to {})".format(self.report_description, self.target_transaction_number)
	elif self.source_transaction_type:
		if self.source_transaction_number:
			self.report_description = "{} (from {})".format(self.report_description, self.source_transaction_number)
	elif self.product:
		self.report_description = "{} ({})".format(self.report_description, self.product_name)


def update_inventory(self):
	product_doc = frappe.get_doc("Product",self.product)
	if product_doc.is_inventory_product==1:
		working_day = get_working_day(self.property)
		cost = get_product_cost(working_day["stock_location"], self.product)
		add_to_inventory_transaction({
			'doctype': 'Inventory Transaction',
			'transaction_type':"Folio Transaction",
			'transaction_date':self.posting_date,
			'transaction_number':self.name,
			'product_code': self.product,
			'portion':"",
			'unit':self.unit,
			'stock_location':working_day["stock_location"],
			'out_quantity': self.quantity if self.type=='Debit' else self.quantity * -1,
			"uom_conversion":1,
			'note': f'Item charge adding to folio. Account Code: {self.account_code}-{self.account_name}',
			'action': 'Submit'
		})

			
 