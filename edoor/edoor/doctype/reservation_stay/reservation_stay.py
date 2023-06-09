# Copyright (c) 2023, Tes Pheakdey and contributors
# For license information, please see license.txt
from frappe.utils import get_url_to_form
from datetime import datetime
from edoor.api.frontdesk import get_working_day
from edoor.api.utils import get_date_range,get_room_rate, update_reservation_stay
import frappe
from frappe.model.document import Document
from frappe.utils import add_to_date,today,now
from py_linq import Enumerable
from edoor.api.utils import update_reservation, update_reservation_color
 
class ReservationStay(Document):
	def  validate(self):
		
		frappe.throw(get_url_to_form("Reservation Stay", self.name))
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

		#check reservation status if allow to edit
		#check with old doc
		if not self.is_new():
			old_doc = frappe.get_doc("Reservation Stay", self.name)
			if frappe.db.get_value("Reservation Status",old_doc.reservation_status, "allow_user_to_edit_information")==0:
				frappe.throw("{} reservation is not allow to change information".format(old_doc.reservation_status) )

			#check prevent unasign room
			
			if self.reservation_status != 'Reserved' and len([d for d in self.stays if (d.room_id or '') == ''])>0:
				frappe.throw("{} reservation is not allow to unasign room".format(self.reservation_status))
		

			
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
			d.group_code = self.group_code
			d.group_name = self.group_name
			d.group_color = self.group_color
			d.guest = self.guest
			d.guest_name = self.guest_name
			d.email = self.guest_email
			d.phone_number = self.guest_phone_number
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
		self.room_rate= Enumerable(self.stays).min(lambda x: x.rate or 0)
		self.room_rate_discount= Enumerable(self.stays).sum(lambda x: x.discount_amount or 0)
 
		self.room_rate_tax_1_amount= Enumerable(self.stays).sum(lambda x: x.tax_1_amount or 0)
		self.room_rate_tax_2_amount= Enumerable(self.stays).sum(lambda x: x.tax_2_amount or 0)
		self.room_rate_tax_3_amount= Enumerable(self.stays).sum(lambda x: x.tax_3_amount or 0)
		self.total_room_rate_tax= Enumerable(self.stays).sum(lambda x: x.total_tax or 0)
		self.total_room_rate= Enumerable(self.stays).sum(lambda x: x.total_rate or 0)
		self.adr = Enumerable(self.stays).avg(lambda x: (x.adr or 0)) 


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
		generate_room_occupy(self)
		update_reservation(name=self.reservation)
	def on_update(self):
		# this block code has been lost
		# this is comment note
		if hasattr(self, 'update_reservation') and self.update_reservation:
			update_reservation(name=self.reservation)
		if hasattr(self, 'update_room_occupy') and self.update_room_occupy:
			change_room_occupy(self)
			generate_room_rate(self)
		if hasattr(self, 'update_reservation_stay') and self.update_reservation_stay:
			update_reservation_stay(name=self.name)


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
	date_avaliables = ""
	self.update_room_rate = False
	for stay in self.stays:
		start_date = datetime.strptime(str(stay.start_date), '%Y-%m-%d')
		end_date = datetime.strptime(str(stay.end_date), '%Y-%m-%d')
		dates = get_date_range(start_date=start_date, end_date=end_date)
 
		for d in dates:
			date_avaliables = date_avaliables + ("'{}',".format(d.strftime("%Y-%m-%d")))
			# validate room old rate update only new rate
			room_rate = frappe.db.count("Reservation Room Rate", filters={'reservation_stay':self.name,'date':d})
			input_rate = stay.rate
			is_manual_rate = stay.is_manual_rate
			if hasattr(self, 'is_override_rate') and self.is_override_rate:
				input_rate = get_room_rate(self.property, self.rate_type, stay.room_type_id, self.business_source, d)
				is_manual_rate = False
			if room_rate == 0:
				#generate room to reservation room rate
				frappe.get_doc({
					"doctype":"Reservation Room Rate",
					"reservation":self.reservation,
					"reservation_stay":self.name,
					"tax_rule":self.tax_rule,
					"rate_include_tax":self.rate_include_tax or "No",
					"tax_1_rate":self.tax_1_rate,
					"tax_2_rate":self.tax_2_rate,
					"tax_3_rate":self.tax_3_rate,
					"stay_room_id":stay.name,
					"room_type_id":stay.room_type_id,
					"room_id":stay.room_id,
					"date":d,
					"input_rate": input_rate,
					"rate_type":self.rate_type,
					"is_manual_rate":is_manual_rate,
					"property":self.property
				}).insert()
			else:
				# avaliable room rate
				old_room_rate = frappe.get_list("Reservation Room Rate", filters={'reservation_stay':self.name,'date':d})
				old_rate = frappe.get_doc('Reservation Room Rate',old_room_rate[0].name)
				old_rate.room_type_id = stay.room_type_id
				old_rate.room_id = stay.room_id
				old_rate.room_number = stay.room_number
				old_rate.input_rate = stay.rate
				old_rate.save()
				frappe.db.commit()
 
	# remove old rate
	sql = "SELECT `name` FROM `tabReservation Room Rate` WHERE `date` NOT IN({}) AND reservation_stay = '{}'".format(date_avaliables[:-1], self.name)
	deleted_old_rates = frappe.db.sql(sql,as_dict=1)
	if len(deleted_old_rates) > 0:
		for d in deleted_old_rates:
			frappe.delete_doc('Reservation Room Rate', d.name)

def change_room_occupy(self):
	self.update_room_occupy = False
	sql = "WHERE reservation_stay = '{0}'".format(self.name)
	frappe.db.sql("delete from `tabTemp Room Occupy` {}".format(sql))
	frappe.db.sql("delete from `tabRoom Occupy` {}".format(sql))
	
	if not self.reservation_status in ['Void','No Show','Cancelled']:
		doc = frappe.get_doc('Reservation Stay', self.name)
		doc.arrival_date = Enumerable(doc.stays).min(lambda x:datetime.strptime(str(x.start_date), '%Y-%m-%d').date())
		doc.departure_date = Enumerable(doc.stays).max(lambda x:datetime.strptime(str(x.end_date), '%Y-%m-%d').date())
		doc.save()
		frappe.db.commit()
		generate_stay_room_occupy(self=doc)

def generate_stay_room_occupy(self):
	self.update_room_occupy = False
	for stay in self.stays:
		dates = get_date_range(start_date=stay.start_date, end_date=stay.end_date)
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