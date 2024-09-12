# Copyright (c) 2023, Tes Pheakdey and contributors
# For license information, please see license.txt


from edoor.api.folio_transaction import update_reservation_folio
import frappe
from frappe.model.document import Document
from edoor.api.frontdesk import get_working_day
from edoor.api.utils import add_audit_trail, check_user_permission, update_city_ledger, update_deposit_ledger, update_desk_folio, update_payable_ledger, get_base_rate,update_reservation_stay_and_reservation
from frappe.utils import fmt_money
from frappe.utils.data import add_to_date, getdate,now
from epos_restaurant_2023.inventory.inventory import add_to_inventory_transaction, check_uom_conversion, get_product_cost, get_stock_location_product, get_uom_conversion, update_product_quantity
from frappe import _

class FolioTransaction(Document):
	def validate(self):
		
		if self.is_new():
			if self.transaction_type =="Reservation Folio":
				
				self.folio_type = frappe.get_cached_value("Reservation Folio", self.transaction_number,"folio_type")  
				self.is_master_folio =  frappe.get_cached_value("Reservation Folio", self.transaction_number,"is_master")
			if not self.working_day or not self.cashier_shift:
				if self.property:
					working_day = get_working_day(self.property)
					if not  working_day["cashier_shift"]:
						frappe.throw(_("Please start eDoor cashier shift first"))
					self.working_day = working_day["name"]
					self.cashier_shift = working_day["cashier_shift"]["name"]
					self.working_date = working_day["date_working_day"]
			if not self.amount:
				self.amount = self.input_amount
			if not self.price:
				self.price = self.input_amount
			
			
			
			if not self.report_description:
				self.report_description = self.account_name
	
			if self.transaction_type == "Reservation Folio":
				validate_reservation_folio_posting(self)
			elif self.transaction_type =="City Ledger":
				validate_city_ledger_posting(self)
			elif self.transaction_type =="Desk Folio":
				validate_desk_folio_posting(self)
			update_sub_account_description(self)

		
		
	def after_insert(self):
		 
	 
		#add audit trail
		if not self.flags.ignore_post_audit_trail:
			if not self.parent_reference and not self.flags.old_doc:
				content =f"Post {self.account_group_name} to {self.transaction_type}. {self.transaction_type} #: {self.transaction_number}, Account: {self.account_code} - {self.report_description}, Amount: {frappe.format(self.total_amount,{'fieldtype':'Currency'})}"
				if self.transaction_type=="Reservation Folio":
					if self.target_transaction_type:
						content = content +  f", {'To folio: ' + self.target_transaction_number + ',' if self.target_transaction_number else '' } Reservation Stay: {self.reservation_stay}, Reservation: {self.reservation}, Account: {self.account_code}-{self.account_name}, Amount: {frappe.format(self.amount,{'fieldtype':'Currency'})}"

					if self.source_transaction_type:
						content = content +  f", From Folio: {self.source_transaction_number} , Reservation Stay: {self.reservation_stay}, Reservation: {self.reservation}, Account: {self.account_code}-{self.account_name}, Amount: {frappe.format(self.amount,{'fieldtype':'Currency'})}"
				
				elif self.transaction_type=="Deposit Ledger":
					content = content + f", Account: {self.account_code}-{self.account_name}, Amount: {frappe.format(self.amount,{'fieldtype':'Currency'})}"
				else:
					content = content + f", Account: {self.account_code}-{self.account_name}, Amount: {frappe.format(self.amount,{'fieldtype':'Currency'})}"

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
		if self.items:
			update_inventory(self)

	def on_update(self):
		if self.flags.ingore_on_update:
			return 
		
	def autoname(self):
		if self.flags.doc_name:
			self.name = self.flags.doc_name
		 
	def on_trash(self):
		frappe.throw("x")
		#if this transaction is auto post 
		if self.is_auto_post and frappe.session.user !="Administrator":
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

		#update reservation stay and reservation of target folio transfer after delete
		sql = "select distinct transaction_type, transaction_number, reservation, reservation_stay from `tabFolio Transaction` where reference_folio_transaction='{}'".format(self.name)
		data = frappe.db.sql(sql,as_dict=1)


		frappe.db.delete("Folio Transaction", filters={"reference_folio_transaction":self.name})
		for d in data:
			if d["transaction_type"] =="Reservation Folio":
				frappe.enqueue("edoor.api.folio_transaction.update_reservation_folio", queue='short', name=d["transaction_number"], doc=None, run_commit=False)
			
			reservation_names.append(d["reservation"])
			reservation_stay_names.append(d["reservation_stay"])
			
		
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
			comment["content"] = f"Folio Transaction #: {self.name} has been deleted, Folio #:<a data-action='view_folio_detail' data-name='{self.transaction_number}'>{self.transaction_number}</a>, Reservation Stay #: <a  data-action='view_reservation_stay_detail' data-name='{self.reservation_stay}'>{self.reservation_stay}</a>,  Reservation # <a data-action='view_reservation_detail' data-name='{self.reservation}'>{self.reservation}'</a>, Guest: <a data-action='view_guest_detail' data-name='{self.guest}'> {self.guest} - {self.guest_name}</a>, Account: <a> {self.account_code} - {self.account_name}</a>, Amount: {frappe.format(self.total_amount,{'fieldtype':'Currency'})}"
		else:
			comment["content"] = f"Folio Transaction #: {self.name} has been deleted, "
			if self.reservation_stay:
				comment["content"] = comment["content"] +  f"Reservation Stay #: <a  data-action='view_reservation_stay_detail' data-name='{self.reservation_stay}'>{self.reservation_stay}</a>, "
			if self.reservation:
				comment["content"] = comment["content"] +  f"Reservation # <a data-action='view_reservation_detail' data-name='{self.reservation}'>{self.reservation}'</a>, " 
				
			if self.guest:
				comment["content"] = comment["content"] +  f"Guest: <a data-action='view_guest_detail' data-name='{self.guest}'> {self.guest} - {self.guest_name}</a>"
			if self.account_code:
				comment["content"] = comment["content"] +  f"Account Code: <a> {self.account_code} - {self.account_name}</a>, "
				comment["content"] = comment["content"] +  f"Amount: {frappe.format(self.total_amount,{'fieldtype':'Currency'})}"
				
			
		if (self.deleted_note):
			comment["content"] = comment["content"] + "<br /> Note: " + self.deleted_note

		if len(reservation_names)> 0 or len(reservation_stay_names)> 0:
			update_reservation_stay_and_reservation(reservation_stay=reservation_stay_names,reservation=reservation_names)

		frappe.enqueue("edoor.api.utils.add_audit_trail",queue='long', data =[comment])

	@frappe.whitelist()
	def get_package_data(self):
		# if self.is_package:
		sql ="""
			select 
				name,
				account_code,
				account_name,
				quantity,
				input_amount,
				price,
				amount,
				note,
				type
			from `tabFolio Transaction`
			where
				name = %(name)s  or 
				parent_reference = %(name)s
		"""
		

		transaction_list = frappe.db.sql(sql,{"name":self.name},as_dict=1)
		# get sub parent reference 
		
		summary_list =frappe.db.sql( "select account_code,account_name, sum(amount*if(type='Debit',1,-1)) as amount from `tabFolio Transaction` where parent_reference in %(parent_references)s group by account_code,account_name order by account_category_sort_order",
							{"parent_references":[d["name"] for d in transaction_list]},as_dict=1)

		return {
			"transaction_list":[d for d in transaction_list if d["name"]==self.name],
			"summary":summary_list
		}
	
def validate_reservation_folio_posting(self):
	if not self.reservation_stay:
		self.reservation_stay = frappe.get_cached_value("Reservation Folio",self.transaction_number, "reservation_stay")		
		self.source_reservation_stay = self.reservation_stay 
		self.reservation = frappe.get_cached_value("Reservation Folio",self.transaction_number, "reservation")		
		self.reservation_type = frappe.get_cached_value("Reservation",self.reservation,"reservation_type")
		self.reservation_status = frappe.get_cached_value("Reservation",self.reservation,"reservation_status")
		if self.reservation_status:
			self.reservation_status_color = frappe.get_cached_value("Reservation Status",self.reservation_status,"color")
	validate_room_id(self)

def validate_room_id(self):
    # room info
	if not self.room_id:
		room_info = frappe.db.sql( "select room_id,room_number,room_type,room_type_id, room_type_alias from `tabRoom Occupy` where reservation_stay=%(reservation_stay)s and property=%(property)s and date=%(date)s limit 1",{"property":self.property,"reservation_stay":self.reservation_stay,"date": self.posting_date},as_dict=1)
		if room_info:
			room_info = room_info[0]
			self.room_id = room_info["room_id"]
			self.room_number = room_info["room_number"]
			self.room_type_id = room_info["room_type_id"]
			self.room_type = room_info["room_type"]
			self.room_type_alias = room_info["room_type_alias"]
		else:
			# get froom from `tabReservation Room`
			room_info = frappe.db.sql( "select room_id,room_number,room_type,room_type_id, room_type_alias from `tabReservation Stay Room` where parent=%(reservation_stay)s and property=%(property)s  limit 1",{"property":self.property,"reservation_stay":self.reservation_stay},as_dict=1)
			if room_info:
				room_info = room_info[0]
				self.room_id = room_info["room_id"]
				self.room_number = room_info["room_number"]
				self.room_type_id = room_info["room_type_id"]
				self.room_type = room_info["room_type"]
				self.room_type_alias = room_info["room_type_alias"]
	else:
		update_room_information(self)

def update_room_information(self):
	if self.room_id and  (not self.room_number or not self.room_type_id or not self.room_type or not self.room_type_alias):
		self.room_number =  frappe.get_cache_value("Room",self.room_id,"room_number")
		self.room_type_id =  frappe.get_cache_value("room_type_id",self.room_id,"room_type_id")
		self.room_type =  frappe.get_cache_value("room_type",self.room_id,"room_type")
		self.room_type_alias = frappe.get_cache_value("room_type_alias",self.room_id,"room_type_alias")
        

def validate_city_ledger_posting(self):
    self.city_ledger_name = frappe.get_cached_value("City Ledger", self.transaction_number,"city_ledger_name")
    self.city_ledger_type = frappe.get_cached_value("City Ledger", self.transaction_number,"city_ledger_type")

def validate_desk_folio_posting(self):
    self.room_id = frappe.get_cached_value("Desk Folio",self.transaction_number, "table_id") 
    if self.room_id:
        update_room_information(self)
    self.business_source = frappe.get_cached_value("Desk Folio",self.transaction_number, "business_source")
    if self.business_source:
    	self.business_source_type = frappe.get_cached_value("Business Source",self.business_source, "business_source_type")
     

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
	

	if self.reservation_stay:
		if  not self.reservation_status:
			self.reservation_status = frappe.db.get_value("Reservation Stay",self.reservation_stay,"reservation_status")

		if not self.business_source:
			self.business_source = frappe.db.get_value("Reservation Stay",self.reservation_stay,"business_source")

	if self.business_source:
		self.business_source_type = frappe.db.get_value("Business Source", self.business_source,"business_source_type")
	else:
		self.business_source_type = ""

	

	

def update_sub_account_description(self):
	
	if self.discount_account:
		if self.discount_amount == 0:
			self.discount_description = ""
		else:
			account_name = frappe.get_cached_value("Account Code", self.discount_account,"account_name")
			if self.discount_type=="Percent":
				self.discount_description = '{} - {}%'.format(account_name, self.discount)
			else:
				self.discount_description = '{}'.format(account_name)
	
		
	if self.tax_1_account:
		if self.tax_1_rate == 0:
			self.tax_1_description = ""
		else:
			account_name = frappe.get_cached_value("Account Code", self.tax_1_account,"account_name")
			self.tax_1_description = '{} - {}%'.format(account_name, self.tax_1_rate)
	
	if self.tax_2_account:
		if self.tax_2_rate == 0:
			self.tax_2_description = ""
		else:
			account_name = frappe.get_cached_value("Account Code", self.tax_2_account,"account_name")
			self.tax_2_description = '{} - {}%'.format(account_name, self.tax_2_rate)
	
	if self.tax_3_account:
		if self.tax_3_rate == 0:
			self.tax_3_description = ""
		else:
			account_name = frappe.get_cached_value("Account Code", self.tax_3_account,"account_name")
			self.tax_3_description = '{} - {}%'.format(account_name, self.tax_3_rate)

	if self.bank_fee_account:
	 
		if self.bank_fee == 0:
			self.bank_fee_description = ""
		else:
			account_name = frappe.get_cached_value("Account Code", self.bank_fee_account,"account_name")
			self.bank_fee_description = '{} - {}% of {}'.format(account_name, self.bank_fee, fmt_money(amount=self.input_amount, currency=frappe.db.get_default("currency")))

	if self.target_transaction_type =="Reservation Folio" and self.target_transaction_number:
		self.report_description = "{} (to {})".format(self.account_name, self.target_transaction_number)
	elif self.target_transaction_type =="City Ledger" and self.target_transaction_number:
		self.report_description = _("{account_name} ( to {city_ledger} - {city_ledger_name})".format( account_name = self.account_name, city_ledger = self.target_transaction_number, city_ledger_name=self.city_ledger_name))
        
	elif self.source_transaction_type =="Reservation Folio" and self.source_transaction_number:
   		self.report_description = _("{account_name} (from {source_transaction_number})".format(account_name = self.account_name,source_transaction_number = self.source_transaction_number))
    
    
     

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
	

def update_inventory(self):
	products = []
	working_day = get_working_day(self.property)
	if self.flags.old_doc:
		# frappe.throw(str([d.product_name for d in self.flags.old_doc.items]))
		products = [{"product_code":d.product_code, "quantity":d.quantity*-1} for d in self.flags.old_doc.items]

	products = products + [{"product_code":d.product_code, "quantity":d.quantity} for d in self.items]

	for product_code in set([d["product_code"] for d in products]):
		quantity = sum([d["quantity"] for d in products if d["product_code"] == product_code])
		if quantity!=0:
			is_inventory_product,unit = frappe.get_cached_value("Product",product_code,['is_inventory_product','unit'])
			if is_inventory_product==1:
				
				in_quantity = 0
				out_quantity = 0
				if quantity>0 :
					if self.type=='Debit':
						out_quantity = quantity
					else:
						in_quantity = quantity
				else:
					if self.type=='Debit':
						in_quantity = abs(quantity)
					else:
						out_quantity = abs(quantity)
						
				
				add_to_inventory_transaction({
					'doctype': 'Inventory Transaction',
					'transaction_type':"Folio Transaction",
					'transaction_date':self.posting_date,
					'transaction_number':self.name,
					'product_code': product_code,
					'portion':"",
					'unit':unit,
					'stock_location':working_day["stock_location"],
					'out_quantity': out_quantity,
					'in_quantity': in_quantity,
					"uom_conversion":1,
					'note': f'Item charge adding to folio. Account Code: {self.account_code}-{self.account_name}',
					'action': 'Submit'
				})

				
 