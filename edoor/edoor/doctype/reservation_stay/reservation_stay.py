# Copyright (c) 2023, Tes Pheakdey and contributors
# For license information, please see license.txt

from edoor.api.frontdesk import get_working_day
from edoor.api.utils import get_date_range
import frappe
from frappe.model.document import Document
from frappe.utils import add_to_date,today,now
from py_linq import Enumerable
from edoor.api.utils import update_reservation
 
class ReservationStay(Document):
	def  validate(self):
 
		if not self.reservation:
			frappe.throw("Please select reservation")

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
		
		#validate select uniue guest in additional guest
		master_guest = frappe.db.get_value('Reservation', self.reservation, 'guest')	
		validate_guests = [x for x in self.additional_guests if x.guest == self.guest or x.guest == master_guest]
		unique_list = list(set([x.guest for x in self.additional_guests]))
		if len(unique_list) < len(self.additional_guests):
			validate_guests = True
		if validate_guests:
			frappe.throw("Cannot select duplicate guest.")


		self.adult = self.adult or 1
		self.child = self.child or 0
		



		self.pax = self.adult + self.child

		if self.stays:
			self.rooms = ','.join([(d.room_number or '') for d in self.stays])
			self.room_types = ','.join([d.room_type for d in self.stays])
			self.room_type_alias = ','.join([d.room_type_alias for d in self.stays])

		for d in self.stays:
			d.property = self.property
			d.reservation_status = self.reservation_status
			d.is_active_reservation = self.is_active_reservation
			d.status_color = self.status_color
			d.reservation_type = self.reservation_type
			d.guest = self.guest
			d.start_date = d.start_date or self.arrival_date
			d.start_time = d.start_time or self.arrival_time
			d.end_time = d.end_time or self.departure_time
			d.nd_date = d.end_date or self.departure_date
			d.adult = self.adult or 1
			d.child = self.child or 0
			d.reference_number = self.reference_number
			d.pax = d.adult  + d.child
			d.reservation = self.reservation
			d.rate_type = self.rate_type
			d.room_nights = frappe.utils.date_diff(d.end_date, d.start_date)
			
		#update stay summary
		self.room_nights = Enumerable(self.stays).sum(lambda x: x.room_nights)
		self.room_rate= Enumerable(self.stays).sum(lambda x: x.total_rate or 0)
		self.room_rate_discount= Enumerable(self.stays).sum(lambda x: x.discount or 0)
		self.room_rate_tax_1_amount= Enumerable(self.stays).sum(lambda x: x.tax_1_amount or 0)
		self.room_rate_tax_2_amount= Enumerable(self.stays).sum(lambda x: x.tax_2_amount or 0)
		self.room_rate_tax_3_amount= Enumerable(self.stays).sum(lambda x: x.tax_3_amount or 0)
		self.total_room_rate_tax= Enumerable(self.stays).sum(lambda x: x.total_tax or 0)
		self.total_room_rate= Enumerable(self.stays).sum(lambda x: x.total_rate or 0)
		self.adr = Enumerable(self.stays).sum(lambda x: (x.total_rate or 0)) / self.room_nights


		self.balance  = (self.total_debit or 0)  -  (self.total_credit or 0)  

		#update note & housekeeping note
		if self.is_new():
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

	def after_insert(self):
		generate_room_rate(self)
		#generate_room_occupy_and_rate(self)
		frappe.enqueue("edoor.edoor.doctype.reservation_stay.reservation_stay.generate_room_occupy", queue='short', self=self)

	def on_update(self):
		if  hasattr(self,"update_reservation_stay") and self.update_reservation_stay:
			update_reservation(self.reservation)

def update_note(self):
	self.note_by = frappe.session.user
	self.note_modified = now()
	return self

def update_housekeeping_note(self):
	self.housekeeping_note_by = frappe.session.user
	self.housekeeping_note_modified = now()
	return self

def generate_room_occupy(self):		
	dates = get_date_range(self.arrival_date, self.departure_date)
	for stay in self.stays: 
		for d in dates:
			#generate room to temp room occupy
			frappe.get_doc({
				"doctype":"Temp Room Occupy",
				"reservation":self.reservation,
				"reservation_stay":self.name,
				"room_type_id":stay.room_type_id,
				"room_id":stay.room_id,
				"date":d,
				"type":"Reservation",
				"property":self.property,
				"stay_room_id":stay.name,
				"adult":self.adult,
				"child":self.child,
				"pax":self.pax

			}).insert()


			#generate room to room occupy
			frappe.get_doc({
				"doctype":"Room Occupy",
				"room_type_id":stay.room_type_id,
				"room_id":stay.room_id,
				"date":d,
				"type":"Reservation",
				"property":self.property,
				"stay_room_id":stay.name,
				"reservation":self.reservation,
				"reservation_stay":self.name,
				"adult":self.adult,
				"child":self.child,
				"pax":self.pax
			}).insert()

 

def generate_room_rate(self):		
	dates = get_date_range(self.arrival_date, self.departure_date)
	for stay in self.stays: 
		for d in dates:
			#generate room to reservation room rate
			frappe.get_doc({
				"doctype":"Reservation Room Rate",
				"reservation":self.reservation,
				"reservation_stay":self.name,
				"stay_room_id":stay.name,
				"room_type_id":stay.room_type_id,
				"room_id":stay.room_id,
				"date":d,
				"rate":stay.rate,
				"rate_type":self.rate_type,
				"is_manual_rate":stay.is_manual_rate,
				"property":self.property
			}).insert()



		

