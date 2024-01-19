# Copyright (c) 2023, Tes Pheakdey and contributors
# For license information, please see license.txt
from decimal import Decimal
import json
from frappe.utils import get_url_to_form
from datetime import datetime
from edoor.api.frontdesk import get_working_day
from edoor.api.utils import get_date_range,get_room_rate, update_is_arrival_date_in_room_rate, update_reservation_stay
import frappe
from frappe.model.document import Document
from frappe.utils import add_to_date,today,now,getdate
from py_linq import Enumerable
from edoor.api.utils import update_reservation


class ReservationStay(Document):
	def  validate(self):
		if self.flags.ignore_validate:
			return
		

		working_day = get_working_day(self.property)
		
		if not self.reservation:
			frappe.throw("Please select reservation")

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
				if not hasattr(self,"is_undo_check_out"): 
					frappe.throw("{} reservation is not allow to change information".format(old_doc.reservation_status) )

			#check prevent unasign room
			
			if not old_doc.reservation_status in ['Reserved', 'Confirmed','No Show'] and len([d for d in self.stays if (d.room_id or '') == ''])>0:
				frappe.throw("{} reservation is not allow to unasign room".format(self.reservation_status))
		

		if not self.reservation_color_code:
			self.reservation_color = None

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
		


		rooms_data = []
		self.pax = self.adult + self.child 	
		if self.stays:
			self.rooms = ','.join([(d.room_number or '') for d in self.stays if (d.room_number or '') !='' ])
			self.room_types = ','.join(set([d.room_type for d in self.stays]))
			self.room_type_alias = ','.join(set([d.room_type_alias for d in self.stays]))
		
		
				
		for d in self.stays:
			
			d.property = self.property
			d.reservation_status = self.reservation_status
			d.is_active_reservation = self.is_active_reservation
			d.allow_user_to_edit_information = self.allow_user_to_edit_information

			d.additional_guest_name= ' / '.join(set([d.guest_name for d in self.additional_guests]))

			if self.is_reserved_room:
			 
				d.show_in_room_chart  = self.is_reserved_room
			else:
				 
				d.show_in_room_chart = reservation_status.show_in_room_chart
			
			if self.is_reserved_room==1:
				d.is_active_reservation = 1

			d.status_color = self.status_color
			d.reservation_type = self.reservation_type
			d.group_code = self.group_code
			d.group_name = self.group_name
			d.group_color = self.group_color
			d.reservation_color = self.reservation_color
			d.reservation_color_code = self.reservation_color_code
			d.guest = self.guest
			d.guest_name = self.guest_name
			d.email = self.guest_email
			d.phone_number = self.guest_phone_number
			d.start_date = d.start_date or self.arrival_date
			d.start_time = d.start_time or self.arrival_time
			d.end_time = d.end_time or self.departure_time
			d.end_date = d.end_date or self.departure_date
			d.adult = self.adult or 1
			d.child = self.child or 0
			d.reference_number = self.reference_number
			d.pax = d.adult  + d.child
			d.reservation = self.reservation
			d.rate_type = self.rate_type
			d.room_nights = frappe.utils.date_diff(d.end_date, d.start_date)
			d.stay_rooms = self.rooms
			d.stay_room_types = self.room_types 
			d.can_change_start_date = 1 if (len(self.stays) == 1 or self.stays.index(d) ==0) and self.reservation_status in ["Reserved","Confirmed"]     else 0
			d.can_change_end_date = 1 if (len(self.stays) == 1 or self.stays.index(d) == len(self.stays)-1 ) and  self.reservation_status in ["Confirmed","Reserved","In-house"] else 0
			#generate room data
			rooms_data.append({
					"name": d.name,
					"room_number": d.room_number or '',
					"room_type_alias": d.room_type_alias,
					"room_type": d.room_type
				})
			
		
		for d in self.additional_guests:
			d.reservation = self.reservation


		self.rooms_data = json.dumps(rooms_data)

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
 
		self.arrival_date = Enumerable(self.stays).min(lambda x:getdate(x.start_date))
		self.departure_date = Enumerable(self.stays).max(lambda x:getdate(x.end_date))

		self.balance  = (self.total_debit or 0)  -  (self.total_credit or 0)

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

 

	def after_insert(self):
		generate_room_rate(self)
		frappe.enqueue("edoor.api.utils.add_audit_trail",queue='long', data =[{
			"comment_type":"Created",
			"subject":"Create New Reservation Stay",
			"reference_doctype":"Reservation Stay",
			"reference_name":self.name,
			"custom_audit_trail_type":"Created",
			"custom_icon":"pi pi-file",
			"content":f"New reservation stay added. Reservation Stay #: <a target='_blank' href='/frontdesk/stay-detail/{self.name}'>{self.name}</a>,  Reservation # <a target='_blank' href='/frontdesk/reservation-detail/{self.reservation}'>{self.reservation}</a>, Ref #: {self.reference_number or ''}, Reservation Type: {self.reservation_type}, Guest: {self.guest} - {self.guest_name}, Bussiness Source: {self.business_source}"
		}])

	def on_update(self):

		if self.flags.ignore_on_update:
			return
		

		if self.is_master:
			reservation_stays = frappe.get_list("Reservation Stay",filters={
				'reservation': self.reservation
			},
			page_length=100)
			
			frappe.db.sql("update `tabReservation Stay Room` set is_master = 0 where is_master = 1 and parent in('{}')".format("','".join([str(x.name) for x in reservation_stays])))
		
		data_for_udpate = {
			"rooms":self.rooms,
			"note":self.note,
			"total_credit": self.total_credit or 0,
			"total_debit": self.total_debit or 0,
			"balance":self.balance or 0,
			"total_room_rate":self.total_room_rate or 0,
			"internal_reference_number":self.internal_reference_number or '',
			"arrival_date":self.arrival_date,
			"departure_date":self.departure_date,
			"is_master":self.is_master,
			"reservation_color":self.reservation_color or '',
			"group_color":self.group_color or '',
			"group_code":self.group_code or '',
			"group_name":self.group_name or '',
			"reservation_type":self.reservation_type,
			"paid_by_master_room":self.paid_by_master_room,
			"reservation_stay_adr":self.adr,
			"name": self.name
		}
		frappe.db.sql("""
			update `tabReservation Stay Room` 
			set rooms=%(rooms)s,
			note=%(note)s,
			total_credit=%(total_credit)s,
			total_debit=%(total_debit)s,
			balance=%(balance)s,
			total_room_rate=%(total_room_rate)s,
			internal_reference_number = %(internal_reference_number)s,
			arrival_date=%(arrival_date)s,
			departure_date=%(departure_date)s,
			is_master=%(is_master)s,
		 	reservation_color=%(reservation_color)s,
			group_color=%(group_color)s,
			group_code=%(group_code)s,
			group_name=%(group_name)s,
			reservation_stay_adr=%(reservation_stay_adr)s,
			reservation_type=%(reservation_type)s,
			paid_by_master_room=%(paid_by_master_room)s
		 where parent=%(name)s
		""",data_for_udpate)
	
 

def update_note(self):
	self.note_by = frappe.session.user
	self.note_modified = now()
	return self



def update_housekeeping_note(self):
	self.housekeeping_note_by = frappe.session.user
	self.housekeeping_note_modified = now()
	return self

def generate_room_rate_after_change_stay(data):
	for d in data:
		update_reservation_stay_room_rate_after_resize(data=d["data"], stay_doc = d["stay_doc"])

@frappe.whitelist()
def generate_room_occupy(self =None, stay_name=None):

		 
	frappe.db.sql("delete from `tabRoom Occupy` where reservation_stay='{}'".format( stay_name if not self else self.name))
	frappe.db.commit()
	if not self:
		if frappe.db.exists("Reservation Stay", stay_name):
			self = frappe.get_doc("Reservation Stay", stay_name)
		else:
			return 
		
	

	is_pickup, is_drop_off = frappe.db.get_value("Reservation Stay", self.name,["require_pickup","require_drop_off"])

	for stay in self.stays: 
		dates = get_date_range(getdate( stay.start_date), getdate(stay.end_date),exlude_last_date=False if stay.name == self.stays[len(self.stays)-1].name else True)
		for d in dates:
			occ_doc = frappe.get_doc({
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
					"pax":self.pax,
					"is_stay_over":1 if (getdate(d)>getdate(self.checked_in_system_date or self.arrival_date) and getdate(d)< getdate(self.departure_date)) or  self.is_early_checked_out ==1  else 0,
					"is_arrival": 1 if getdate(d)==getdate(self.checked_in_system_date or  self.arrival_date) else 0,
					"is_departure": 1 if getdate(d)==getdate(self.departure_date) else 0 ,
					"is_active":1 if (getdate(d)<getdate(self.departure_date) or self.is_early_checked_out) and getdate(d)>=getdate(self.checked_in_system_date or self.arrival_date) else 0 ,
					"pick_up": 1 if getdate(d)==getdate(self.arrival_date) and is_pickup==1 else 0,
					"drop_off": 1 if getdate(d)==getdate(self.departure_date) and is_drop_off ==1 else 0 

				})
			if occ_doc.is_stay_over==1 and occ_doc.is_arrival==1:
				occ_doc.is_stay_over==0
			occ_doc.insert( ignore_permissions=True)


	frappe.db.commit()



def generate_temp_room_occupy(self=None, stay_name =None ):	
 
		
	frappe.db.sql("delete from `tabTemp Room Occupy` where reservation_stay='{}'".format(stay_name if not self else self.name))
	
	if not self:
		if frappe.db.exists("Reservation Stay", stay_name):
			self = frappe.get_doc("Reservation Stay", stay_name)
		else:
			frappe.db.commit()
			return 
	for stay in self.stays: 
		dates = get_date_range(getdate( stay.start_date), getdate( stay.end_date),exlude_last_date=True)
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
				"is_active":1 
			}).insert()


def generate_room_rate(self, run_commit = True): 

	date_avaliables = ""
	self.update_room_rate = False
	for stay in self.stays:
		start_date =getdate(stay.start_date)
		end_date = getdate(stay.end_date)
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
					"is_active_reservation":1,
					"is_active":1,
					"is_arrival": 1 if getdate(d) == getdate(self.arrival_date) else 0 
				}).insert()
			else:
				# avaliable room rate
	 
				old_room_rate = frappe.get_list("Reservation Room Rate", filters={'reservation_stay':self.name,'date':d})
				old_rate = frappe.get_doc('Reservation Room Rate',old_room_rate[0].name)
				old_rate.room_type_id = stay.room_type_id
				old_rate.room_id = stay.room_id
				old_rate.room_number = stay.room_number
				if hasattr(self, 'is_override_rate') and self.is_override_rate==1:
					old_rate.input_rate = get_room_rate(self.property, self.rate_type, stay.room_type_id, self.business_source, d)
					
				old_rate.save()
				
 
	# remove old rate
	sql = "SELECT `name` FROM `tabReservation Room Rate` WHERE `date` NOT IN({}) AND reservation_stay = '{}'".format(date_avaliables[:-1], self.name)
	deleted_old_rates = frappe.db.sql(sql,as_dict=1)
	if len(deleted_old_rates) > 0:
		for d in deleted_old_rates:
			frappe.delete_doc('Reservation Room Rate', d.name)
			
	if run_commit:
		frappe.db.commit()

	return True


def update_reservation_stay_room_rate(data):
	docs = frappe.db.sql("select name  from `tabReservation Room Rate` where stay_room_id=%(stay_room_id)s",{"stay_room_id":data["stay_room_id"]},as_dict=1)
	for d in docs:
		doc = frappe.get_doc("Reservation Room Rate", d["name"])
		doc.input_rate = data['rate']
		doc.room_id = data["room_id"]
		doc.room_type_id =  data["room_type_id"]
		doc.room_type=  data["room_type"]
		doc.room_number=  data["room_number"]
		doc.save()
	

def update_reservation_stay_room_rate_after_resize(data, stay_doc):
	# date min and max date from reservation room rate
	sql = "select min(date) as start_date, max(date) as end_date from `tabReservation Room Rate` where stay_room_id='{}'".format(data["name"]) 
	old_stay_date = frappe.db.sql(sql, as_dict=1)
	#1 check if user resize from end back ward   so we just delete record
	frappe.db.sql("delete from `tabReservation Room Rate` where stay_room_id='{}' and date>='{}'".format(data["name"],data["end_date"]))
	#2 check if user resize from start forward   so we just delete record
	frappe.db.sql("delete from `tabReservation Room Rate` where stay_room_id='{}' and date<'{}'".format(data["name"],data["start_date"]))

	date_range = []
	room_rate = 0
	rate_type = stay_doc.rate_type
	is_manual_rate = 0
	#3 if user resize from the end forward
	if add_to_date(getdate(old_stay_date[0]["end_date"]),days=1) <getdate(data["end_date"]):	
		
		date_range = get_date_range(add_to_date(getdate(old_stay_date[0]["end_date"]), days=1), getdate( data["end_date"]))
		if data["generate_rate_type"] =="stay_rate":
			room_rate_doc = frappe.db.sql("select rate_type, input_rate,is_manual_rate from `tabReservation Room Rate` where stay_room_id ='{}' and date='{}'".format(data["name"],old_stay_date[0]["end_date"]),as_dict=1)
			if room_rate_doc:
				room_rate = room_rate_doc[0]["input_rate"]
				rate_type = room_rate_doc[0]["rate_type"]
				is_manual_rate  = room_rate_doc[0]["is_manual_rate"]
	else:# if user resize from arrival date back ward
		date_range = get_date_range( getdate( data["start_date"]),getdate(old_stay_date[0]["start_date"]))
		if data["generate_rate_type"] =="stay_rate":
			room_rate_doc = frappe.db.sql("select rate_type, input_rate,is_manual_rate from `tabReservation Room Rate` where stay_room_id ='{}' and date='{}'".format(data["name"],old_stay_date[0]["start_date"]),as_dict=1)
			if room_rate_doc:
				room_rate = room_rate_doc[0]["input_rate"]
				rate_type = room_rate_doc[0]["rate_type"]
				is_manual_rate  = room_rate_doc[0]["is_manual_rate"]
	
	for d in date_range:
 
		frappe.get_doc({
				"doctype":"Reservation Room Rate",
				"reservation":stay_doc.reservation,
				"reservation_stay":stay_doc.name,
				"tax_rule":stay_doc.tax_rule,
				"rate_include_tax":stay_doc.rate_include_tax or "No",
				"tax_1_rate":stay_doc.tax_1_rate,
				"tax_2_rate":stay_doc.tax_2_rate,
				"tax_3_rate":stay_doc.tax_3_rate,
				"stay_room_id":data["name"],
				"room_type_id":data["room_type_id"],
				"room_id": data["room_id"]  if "room_id" in data and data["room_id"]  else None,
				"date":d,
				"input_rate": room_rate,
				"rate_type":rate_type,
				"is_manual_rate":is_manual_rate,
				"property":stay_doc.property,
				"regenerate_rate":0 if (data["generate_rate_type"] =="stay_rate") else 1,
				"is_active_reservation":1,
				"is_active":1
			}).insert()
		

	#update first date in reservation room is_arrival = 1
	frappe.enqueue("edoor.api.utils.update_is_arrival_date_in_room_rate",queue='long', stay_name=stay_doc.name) 

	
def update_reservation_stay_room_rate_after_move(data,stay_doc):

	date_range = get_date_range( getdate( data["start_date"]),getdate(data["end_date"]))
	room_rates = frappe.db.get_list("Reservation Room Rate",filters={"stay_room_id":data["name"]},order_by="date",  start=0, page_length=1000  ) 
	
	for d in room_rates:
		rate_doc = frappe.get_doc("Reservation Room Rate",d.name)
		
		rate_doc.date = date_range[room_rates.index(d)]
		rate_doc.room_id=data["room_id"]
		rate_doc.room_type_id=data["room_type_id"] or frappe.db.get_value("Room", rate_doc.room_id,"room_type_id")
	 

		if data["generate_rate_type"] =="rate_plan":

			rate_doc.is_manual_rate = 0
			rate_doc.regenerate_rate = 1


		rate_doc.save()

	#update first date in reservation room is_arrival = 1
	update_is_arrival_date_in_room_rate(stay_doc.name)
	