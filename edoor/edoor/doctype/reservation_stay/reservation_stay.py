# Copyright (c) 2023, Tes Pheakdey and contributors
# For license information, please see license.txt
import json
from frappe.utils import get_url_to_form
from datetime import datetime
from edoor.api.frontdesk import get_working_day
from edoor.api.utils import get_date_range,get_room_rate, update_reservation_stay
import frappe
from frappe.model.document import Document
from frappe.utils import add_to_date,today,now,getdate
from py_linq import Enumerable
from edoor.api.utils import update_reservation, update_reservation_color
 
class ReservationStay(Document):
	def  validate(self):
		working_day = get_working_day(self.property)
	 
		if not self.reservation:
			frappe.throw("Please select reservation")
			
		 
		if  getdate(self.arrival_date)< getdate( working_day["date_working_day"]) and self.is_new():
			frappe.throw("You don't have permission to add back date transaction")
		
		if  getdate(self.departure_date)<=getdate(self.arrival_date):
			frappe.throw("Departure date cannot less than or equal to arrival date")
		

		
		if not working_day:
			frappe.throw("There is no working open")
		else:

			if not working_day["cashier_shift"]:
				frappe.throw("There is no cashier open. Please open your cashier shift")
			if self.is_new():
				self.working_day = working_day["name"]
				self.working_date = working_day["date_working_day"]
				self.cashier_shift = working_day["cashier_shift"]["name"]

		reservation_status = frappe.get_doc("Reservation Status", self.reservation_status)
		#check with old doc
		if not self.is_new():
			old_doc = frappe.get_doc("Reservation Stay", self.name)
			if frappe.db.get_value("Reservation Status",old_doc.reservation_status, "allow_user_to_edit_information")==0:
				frappe.throw("{} reservation is not allow to change information".format(old_doc.reservation_status) )

			#check prevent unasign room
			
			if not self.reservation_status in ['Reserved', 'Confirmed'] and len([d for d in self.stays if (d.room_id or '') == ''])>0:
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
			self.rooms = ','.join([(d.room_number or '') for d in self.stays if (d.room_number or '') !='' ])
			self.room_types = ','.join(set([d.room_type for d in self.stays]))
			self.room_type_alias = ','.join(set([d.room_type_alias for d in self.stays]))
			# json stay room
			rooms_data = []
			for s in self.stays:
				rooms_data.append({
					"name": s.name,
					"room_number": s.room_number or '',
					"room_type_alias": s.room_type_alias,
					"room_type": s.room_type
				})
			self.rooms_data = json.dumps(rooms_data)
		for d in self.stays:
			d.property = self.property
			d.reservation_status = self.reservation_status
			d.is_active_reservation = self.is_active_reservation
			d.show_in_room_chart = reservation_status.show_in_room_chart
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
		# frappe.enqueue("edoor.edoor.doctype.reservation_stay.reservation_stay.generate_room_rate", queue='short', self = self)
		# frappe.enqueue("edoor.edoor.doctype.reservation_stay.reservation_stay.generate_room_occupy", queue='short', self = self)
		generate_room_occupy(self)
		generate_room_rate(self, is_update_reservation_stay=True)

	def on_update(self):
		frappe.db.sql("update `tabReservation Stay Room` set rooms='{}',arrival_date='{}',departure_date='{}' where parent='{}'".format(self.rooms,self.arrival_date,self.departure_date, self.name))


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

def generate_room_rate(self,is_update_reservation_stay=False): 
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
			
			if room_rate == 0:
				#generate room to reservation room rate
				is_manual_rate = stay.is_manual_rate
				regenerate_rate = False
				if hasattr(self, 'is_override_rate') and self.is_override_rate:
					regenerate_rate = True
					is_manual_rate = False
			 
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
					"input_rate": stay.input_rate,
					"rate_type":self.rate_type,
					"is_manual_rate":is_manual_rate,
					"property":self.property,
					"regenerate_rate":regenerate_rate,
					"is_active_reservation":1
				}).insert()
			else:
				# avaliable room rate
				old_room_rate = frappe.get_list("Reservation Room Rate", filters={'reservation_stay':self.name,'date':d})
				old_rate = frappe.get_doc('Reservation Room Rate',old_room_rate[0].name)
				old_rate.room_type_id = stay.room_type_id
				old_rate.room_id = stay.room_id
				old_rate.room_number = stay.room_number
				if hasattr(self, 'is_old_override_rate') and self.is_old_override_rate:
					old_rate.input_rate = get_room_rate(self.property, self.rate_type, stay.room_type_id, self.business_source, d)
				old_rate.save()
				frappe.db.commit()
 
	# remove old rate
	sql = "SELECT `name` FROM `tabReservation Room Rate` WHERE `date` NOT IN({}) AND reservation_stay = '{}'".format(date_avaliables[:-1], self.name)
	deleted_old_rates = frappe.db.sql(sql,as_dict=1)
	if len(deleted_old_rates) > 0:
		for d in deleted_old_rates:
			frappe.delete_doc('Reservation Room Rate', d.name)
	if is_update_reservation_stay:
		update_reservation_stay(name=self.name)
	return True

def change_room_occupy(self):
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