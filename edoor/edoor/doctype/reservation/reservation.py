# Copyright (c) 2023, Tes Pheakdey and contributors
# For license information, please see license.txt

from datetime import datetime
from decimal import Decimal
import frappe
from frappe.model.document import Document
from edoor.api.frontdesk import get_working_day
from frappe.utils import now,getdate,add_to_date

class Reservation(Document):
	def validate(self):
		if self.departure_date<=self.arrival_date:
			frappe.throw("Departure date cannot less than or equal to arrival date")

		working_day = get_working_day(self.property)
		
		if not working_day:
			frappe.throw("There is no working open")
		else:

			if not working_day["cashier_shift"]:
				frappe.throw("There is no cashier open. Please open your cashier shift")
			if self.is_new():
				self.working_day = working_day["name"]
				self.working_date = working_day["date_working_day"]
				self.cashier_shift = working_day["cashier_shift"]["name"]
		
		self.pax = (self.adult or 1) + (self.child or 0)
		self.balance = (self.total_debit or 0) - (self.total_credit or 0) 
		currency_precision = frappe.db.get_single_value("System Settings","currency_precision")
		if abs(round(self.balance, int(currency_precision)))<= (Decimal('0.1') ** int(currency_precision)):
			self.balance = 0
			
		#update note & housekeeping note
		if self.is_new():
			#set default check in and check out time
			self.arrival_time = frappe.db.get_single_value("eDoor Setting","default_check_in_time")			
			self.departure_time = frappe.db.get_single_value("eDoor Setting","default_check_out_time")			
			

			if self.note:
				self = update_note(self=self)
			if self.housekeeping_note:
				self = update_housekeeping_note(self=self)
		else:
			if self.note:
				note = frappe.db.get_value('Reservation Stay', self.name,'note')
				if self.note != note:
					self = update_note(self=self)
				
			if self.housekeeping_note:
				note = frappe.db.get_value('Reservation Stay', self.name,'housekeeping_note')
				if self.housekeeping_note != note:
					self = update_housekeeping_note(self=self)
	
	
	def on_update(self):
		frappe.db.sql("update `tabReservation Stay Room` set reservation_type = '{}' where reservation = '{}'".format(self.reservation_type, self.name))

	def after_insert(self):
		
		frappe.enqueue("edoor.api.utils.add_audit_trail",queue='long',enqueue_after_commit=20,now=False, data =[{
			"comment_type":"Created",
			"subject":"Create New Reservation",
			"reference_doctype":"Reservation",
			"reference_name":self.name,
			"custom_audit_trail_type":"Created",
			"custom_icon":"pi pi-file",
			"content":f"New reservation added. Reservation # <a target='_blank' href='/frontdesk/reservation-detail/{self.name}'>{self.name}</a>, Ref #: {self.reference_number or ''}, Reservation Type: {self.reservation_type}, Guest: {self.guest} - {self.guest_name}, Bussiness Source: {self.business_source}"

		}])
	 

def update_note(self):
	self.note_by = frappe.session.user
	self.note_modified = now()
	return self

def update_housekeeping_note(self):
	self.housekeeping_note_by = frappe.session.user
	self.housekeeping_note_modified = now()
	return self





