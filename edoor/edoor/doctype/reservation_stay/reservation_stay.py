# Copyright (c) 2023, Tes Pheakdey and contributors
# For license information, please see license.txt

from edoor.api.frontdesk import get_working_day
from edoor.api.utils import get_date_range
import frappe
from frappe.model.document import Document
from frappe.utils import add_to_date
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
				
				
		reservation = frappe.get_doc("Reservation",self.reservation)
		self.adult = self.adult or 1
		self.child = self.child or 0

		self.pax = self.adult + self.child
		if self.stays:
			self.rooms = ','.join([(d.room_number or '') for d in self.stays])
			self.room_types = ','.join([d.room_type for d in self.stays])

		for d in self.stays:
			d.property = self.property
			d.reservation_status = self.reservation_status
			d.status_color = self.status_color
			d.reservation_type = self.reservation_type

		 
			if not d.guest:
				d.guest = self.guest
			
			 
			
			d.start_date = d.start_date or self.arrival_date
			d.start_time = d.start_time or self.arrival_time
			d.end_date = d.end_date or self.departure_date
			d.end_time = d.end_time or self.departure_time
			d.adult = self.adult
			d.child = self.child
			d.reference_number = self.reference_number
			d.pax = self.pax,
			d.reservation = self.reservation
			d.rate_type = self.rate_type
			d.room_nights = frappe.utils.date_diff(d.end_date, d.start_date)
			#d.total_amount = (d.rate or  0 )* (d.room_nights or 1)

	def after_insert(self):
		#generate_room_occupy_and_rate(self)
		frappe.enqueue("edoor.edoor.doctype.reservation_stay.reservation_stay.generate_room_occupy_and_rate", queue='short', self=self)

def generate_room_occupy_and_rate(self):		
	dates = get_date_range(self.arrival_date, self.departure_date)
	for stay in self.stays: 
		for d in dates:
			#generate room to temp room occupy
			frappe.get_doc({
				"doctype":"Temp Room Occupy",
				"room_type_id":stay.room_type_id,
				"room_id":stay.room_id,
				"date":d,
				"type":"Reservation",
				"property":self.property,
				"stay_room_id":stay.name,
				"is_arrival":1 if d == self.arrival_date
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
				"reservation_stay":self.name
			}).insert()


			#generate room to reservation room rate
			frappe.get_doc({
				"doctype":"Reservation Room Rate",
				"reservation":self.reservation,
				"reservation_stay":self.name,
				"room_type_id":stay.room_type_id,
				"room_id":stay.room_id,
				"date":d,
				"rate":stay.rate,
				"rate_type":self.rate_type,
				"property":self.property
			}).insert()

	
				 


		

