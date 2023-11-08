# Copyright (c) 2023, Tes Pheakdey and contributors
# For license information, please see license.txt

from edoor.api.frontdesk import get_working_day
import frappe
from frappe.model.document import Document

class ReservationFolio(Document):
	def validate(self):
		#check reservation status if allow to edit
		
		doc_status = frappe.get_doc("Reservation Status", self.reservation_status)
		if doc_status.allow_user_to_edit_information==0 or  doc_status.is_active_reservation==0:
			frappe.throw("{} reservation is not allow to add or update information".format(self.reservation_status) )
		

		self.balance = (self.total_debit or 0) -( self.total_credit or 0)
		#validate working day 
		if self.is_new():
			working_day = get_working_day(self.property)
			if not working_day["name"]:
				frappe.throw("Please start working")
			
			if not working_day["cashier_shift"]["name"]:
				frappe.throw("Please start cashier shift")
			self.working_day = working_day["name"]
			self.working_date = working_day["date_working_day"]
			self.posting_date = self.working_date
			self.cashier_shift = working_day["cashier_shift"]["name"]

			#check total folio in current reservation stay if not have then set this folio as master folio
			if self.reservation_stay:
				if not frappe.db.exists("Reservation Folio",{"reservation_stay":self.reservation_stay}):
					self.is_master = 1
				#udpate business source 
				
				self.business_source = frappe.db.get_value("Reservation Stay", self.reservation_stay, "business_source")
				#self.reservation_status_color = frappe.db.get_value("Reservation Stay", self.reservation_stay, "business_source")
		else:
			if self.is_master == 1 and self.status == 'Closed':
				frappe.throw("Master folio is not allow to close")
					


		 
		if round(self.balance,int(frappe.db.get_default("currency_precision"))) > 0 and self.status == "Closed":
			frappe.throw("Cannot close folio with balance is greater than 0")
			
	def on_update(self):
		if self.is_master==1:
			#reset other is master = 0
			frappe.db.sql("update `tabReservation Folio` set is_master=0 where is_master=1 and name<>'{}' and reservation_stay='{}'".format(self.name,self.reservation_stay))
	def on_trash(self):
		
		if self.is_master:
			frappe.throw("Master folio is not allow to delete")

		if frappe.db.exists("Folio Transaction",{"transaction_type":"Reservation Folio","transaction_number":self.name}):
			frappe.throw("You cannot delete folio that have transaction")
			
				
		#check reservation status if allow to edit
		if frappe.db.get_value("Reservation Status",self.reservation_status, "allow_user_to_edit_information")==0:
			frappe.throw("{} reservation is not allow to delete this transaction".format(self.reservation_status) )

	def after_insert(self):
		comment = {
			"comment_type":"Created",
			"custom_audit_trail_type":"Created",
			"subject":"Create New Guest Folio",
			"reference_doctype":"Reservation Folio",
			"reference_name":self.name,
			"content":f"New guest folio added. Folio #:<a data-action='view_folio_detail' data-name='{self.name}'>{self.name}</a> Reservation Stay #: <a  data-action='view_reservation_stay_detail' data-name='{self.reservation_stay}'>{self.reservation_stay}</a>,  Reservation # <a data-action='view_reservation_detail' data-name='{self.reservation}'>{self.reservation}</a>, Guest: <a data-action='view_guest_detail' data-name='{self.guest}'> {self.guest} - {self.guest_name}</a>"
		}

		if (self.note):
			comment["content"] = comment["content"] + "<br /> Note: " + self.note

		frappe.enqueue("edoor.api.utils.add_audit_trail",queue='short', data =[comment])


	def after_delete(self):
		working_day = get_working_day(self.property)

		comment = {
			"comment_type":"Deleted",
			"subject":"Delete Guest Folio",
			"reference_doctype":"Reservation Stay",
			"reference_name":self.reservation_stay,
			"content":f"Folio #: {self.name} has been deleted, Reservation Stay #: <a  data-action='view_reservation_stay_detail' data-name='{self.reservation_stay}'>{self.reservation_stay}</a>,  Reservation # <a data-action='view_reservation_detail' data-name='{self.reservation}'>{self.reservation}'</a>, Guest: <a data-action='view_guest_detail' data-name='{self.guest}'> {self.guest} - {self.guest_name}</a>",
			"custom_property":self.property,
			"custom_posting_date": working_day["date_working_day"]
		}
		
		if (self.deleted_note):
			comment["content"] = comment["content"] + "<br /> Note: " + self.deleted_note

		frappe.enqueue("edoor.api.utils.add_audit_trail",queue='short', data =[comment])

