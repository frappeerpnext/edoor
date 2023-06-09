# Copyright (c) 2023, Tes Pheakdey and contributors
# For license information, please see license.txt

from edoor.api.frontdesk import get_working_day
from edoor.api.utils import get_date_range
import frappe
from frappe.model.document import Document
from frappe.utils import add_to_date,today
from py_linq import Enumerable

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
		validate_guests = [x for x in self.additional_guests if x.guest == self.guest]
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

		for d in self.stays:
			d.property = self.property
			d.reservation_status = self.reservation_status
			d.is_active_reservation = self.is_active_reservation
			d.status_color = self.status_color
			d.reservation_type = self.reservation_type
			d.guest = self.guest
			d.start_date = d.start_date or self.arrival_date
			d.start_time = d.start_time or self.arrival_time
			d.end_date = d.end_date or self.departure_date
			d.end_time = d.end_time or self.departure_time
			d.adult = self.adult 
			d.child = self.child
			d.reference_number = self.reference_number
			d.pax = d.adult + d.child
			d.reservation = self.reservation
			d.rate_type = self.rate_type
			d.room_nights = frappe.utils.date_diff(d.end_date, d.start_date)

			#d.total_amount = (d.rate or  0 )* (d.room_nights or 1)


		#update stay summayr
		self.room_nights = Enumerable(self.stays).sum(lambda x: x.room_nights)
		self.total_room_rate= Enumerable(self.stays).sum(lambda x: x.rate * x.room_nights)

		self.adr_rate =self.total_room_rate /  (self.room_nights or 1)
		



	def after_insert(self):
		#generate_room_occupy_and_rate(self)
		frappe.enqueue("edoor.edoor.doctype.reservation_stay.reservation_stay.generate_room_occupy_and_rate", queue='short', self=self)


	def on_update(self):
		#will run this in queue
		update_data_to_reservation(self)


def update_data_to_reservation(self):
	
	if not hasattr(self,"update_reservation") or self.update_reservation:
			sql ="update `tabTemp Room Occupy` set adult={}, child={} , pax = {} where reservation_stay = '{}'".format(self.adult,self.child,self.pax,self.name)
			frappe.db.sql(sql)

			sql = """select 
						min(if(is_active_reservation=0,'2050-01-01', arrival_date)) as arrival_date,
						max(if(is_active_reservation=0,'2000-01-01', departure_date)) as departure_date,
						count(name) as total_stay,
						sum(if(is_active_reservation =1,1,0)) as total_active_stay, 
						sum(if(is_active_reservation =1,adult,0)) as adult, 
						sum(if(is_active_reservation =1,child,0)) as child ,
						
						sum(if(is_active_reservation=1 and reservation_status='In-House',1,0)) as total_checked_in,
						sum(if(is_active_reservation=1 and reservation_status='Checked Out',1,0)) as total_checked_out,
						sum(if(is_active_reservation=0 and reservation_status='Cancelled',1,0)) as total_cancelled,
						sum(if(is_active_reservation=0 and reservation_status='No Show',1,0)) as total_no_show,
						sum(if(is_active_reservation=0 and reservation_status='Void',1,0)) as total_void,
						
						sum(if(is_active_reservation =1,room_nights,0)) as room_nights,
						sum(if(is_active_reservation=1,total_room_rate,0)) as total_room_rate,
						sum(if(is_active_reservation=1,adr_rate,0)) as total_adr_rate

						

					from `tabReservation Stay`
					where 
						reservation='{}'
					""".format(self.reservation)
			
			data = frappe.db.sql(sql,as_dict=1)


			#update to reservation 
			doc_reservation = frappe.get_doc("Reservation", self.reservation)
			doc_reservation.total_reservation_stay = data[0][ "total_stay"]
			doc_reservation.total_active_reservation_stay = data[0][ "total_active_stay"]
			doc_reservation.arrival_date = data[0]["arrival_date"]
			doc_reservation.departure_date= data[0]["departure_date"]
			
			doc_reservation.adult = data[0][ "adult"]
			doc_reservation.child = data[0][ "child"]

			doc_reservation.room_nights= data[0]["room_nights"]
			doc_reservation.total_room_rate= data[0]["total_room_rate"]
			doc_reservation.total_adr_rate= data[0]["total_adr_rate"]

			doc_reservation.total_checked_in= data[0]["total_checked_in"]
			doc_reservation.total_checked_out= data[0]["total_checked_out"]
			doc_reservation.total_cancelled= data[0]["total_cancelled"]
			doc_reservation.total_void= data[0]["total_void"]
			doc_reservation.total_no_show= data[0]["total_no_show"]


			doc_reservation.update_reservation_stay = False
			
			doc_reservation.save()

def generate_room_occupy_and_rate(self):		
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
				"is_manual_rate":stay.is_manual_rate,
				"property":self.property
			}).insert()

	
				 


		

