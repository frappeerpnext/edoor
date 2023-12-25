# Copyright (c) 2023, Tes Pheakdey and contributors
# For license information, please see license.txt

from datetime import datetime
from edoor.api.utils import check_user_permission, get_date_range
import frappe
from frappe.model.document import Document
from frappe.utils.data import add_to_date, getdate, pretty_date,date_diff
from edoor.api.frontdesk import get_working_day

class RoomBlock(Document):
	def validate(self):
		working_day = get_working_day(self.property)

		self.housekeeping_status = frappe.db.get_default("room_block_status")
		self.status_color = frappe.get_value("Housekeeping Status",self.housekeeping_status, "status_color")
		
		if getdate(self.end_date) < getdate(working_day["date_working_day"]):
			frappe.throw("End date cannot be less than current date")
		
		if getdate(self.end_date)<= getdate(self.start_date):
			self.end_date = add_to_date(getdate(self.start_date),days=1)
		self.total_night_count = date_diff(self.end_date,self.start_date)
		
		
	def before_submit(self):
		sql = "select name, date,type from `tabTemp Room Occupy` where stay_room_id != '{}' and room_id = '{}' and date between '{}' and '{}' and property='{}' limit 1"
		sql = sql.format(self.name, self.room_id, self.start_date, add_to_date(getdate(self.end_date),days=-1), self.property)
		 
		data = frappe.db.sql(sql, as_dict=1)
		if data:
			frappe.throw("Room {} is already occupy or block on date {}".format( self.room_number,data[0]["date"].strftime("%d-%m-%Y")))


	def on_submit(self):
		generate_block_date(self)
		
	def before_update_after_submit(self):
		self.total_night_count = date_diff(self.end_date,self.start_date)
		if frappe.db.get_single_value("eDoor Setting","allow_user_to_add_back_date_transaction") == 0:
			
			old_start_date = frappe.db.get_value("Room Block", self.name, "start_date")
			if getdate(old_start_date) != getdate(self.start_date):
				working_date = get_working_day(self.property)
				if getdate(self.start_date) <= getdate(working_date["date_working_day"]):
					frappe.throw("Cannot change room block to the past date")
		else: 
			check_user_permission("role_for_back_date_transaction")

	def on_update_after_submit(self): 
		
		if self.is_unblock ==1:
			if not self.unblock_housekeeping_status:
				frappe.throw("Please select current room housekeeping status.")
			room_doc = frappe.get_doc("Room", self.room_id)
			room_doc.housekeeping_status = self.unblock_housekeeping_status 
			room_doc.save()
			frappe.db.sql("delete from `tabTemp Room Occupy` where type='Block' and stay_room_id='{}' and room_id='{}' and property='{}'".format(self.name,self.room_id,self.property))
			frappe.db.sql("delete from `tabRoom Occupy` where type='Block' and stay_room_id='{}' and room_id='{}' and property='{}'".format(self.name,self.room_id,self.property))
		else:
			#check if date is extend
			old_doc = frappe.get_doc("Room Block", self.name)
			if self.end_date != old_doc.end_date or  self.start_date != old_doc.start_date:
				#check if next block date have room occupy 
				sql = "select name, date,type from `tabTemp Room Occupy` where stay_room_id != '{}' and room_id='{}' and date between '{}' and '{}' and property='{}' and stay_room_id != '{}' and is_departure=0 limit 1 "
				sql = sql.format(self.name, self.room_id, self.start_date, add_to_date(getdate(self.end_date),days=-1), self.property,self.name)
 
				data = frappe.db.sql(sql, as_dict=1)
				if data:
					frappe.throw("Room {} is already occupy or block on date {}".format( self.room_number,data[0]["date"].strftime("%d-%m-%Y")))

				generate_block_date(self)

				working_day = get_working_day(self.property)
				room_doc = frappe.get_doc("Room",self.room_id)
				if  getdate(self.start_date)<= getdate(working_day["date_working_day"])  and getdate(self.end_date) > getdate(working_day["date_working_day"]):
					
					room_doc.housekeeping_status = frappe.db.get_single_value("eDoor Setting","room_block_status")
				else:
					room_doc.housekeeping_status = frappe.db.get_single_value("eDoor Setting","hk_status_rb_release_after_audit")
				room_doc.save()


	def after_insert(self):
		frappe.enqueue("edoor.api.utils.add_audit_trail",queue='short', data =[{
			"comment_type":"Created",
			"custom_property": self.property,
			"subject":"Create New Room Block",
			"reference_doctype":"Room Block",
			"custom_audit_trail_type":"Created",
			"custom_icon":"pi pi-file",
			"reference_name":self.name,
			"content":f"Create new room block. <b>Room Block #</b>:<a data-action='view_room_block_detail' data-name='{self.name}'>{self.name}</a>, <b>Room #</b>: {self.room_number}, <b>from</b> { getdate(self.start_date).strftime('%d-%m-%Y')} to { add_to_date(getdate(self.end_date),days=-1).strftime('%d-%m-%Y')}<br/> <b>Reason</b>: {self.reason}"
		}])

	def on_cancel(self):
		frappe.db.sql("delete from `tabTemp Room Occupy` where type='Block' and stay_room_id='{}' and room_id='{}' and property='{}'".format(self.name,self.room_id,self.property))
		frappe.db.sql("delete from `tabRoom Occupy` where type='Block' and stay_room_id='{}' and room_id='{}' and property='{}'".format(self.name,self.room_id,self.property))

def generate_block_date(self):
	data = frappe.get_doc('Room Block', self.name)
	#generate room to temp room occupy
	frappe.db.sql("delete from `tabTemp Room Occupy` where stay_room_id='{}'".format(data.name))
	frappe.db.sql("delete from `tabRoom Occupy` where stay_room_id='{}'".format(data.name))
	dates = get_date_range( datetime.strptime(str(data.start_date), "%Y-%m-%d").date(), add_to_date(getdate(str(data.end_date)),days=-1),False)

	for d in dates: 
		frappe.get_doc({
			"doctype":"Temp Room Occupy",
			"room_type_id":data.room_type_id,
			"room_id":data.room_id,
			"date":d,
			"type":"Block",
			"property":data.property,
			"stay_room_id":data.name,
			"is_active":1
		}).insert()


		#generate room to room occupy
		frappe.get_doc({
			"doctype":"Room Occupy",
			"room_type_id":data.room_type_id,
			"room_id":data.room_id,
			"date":d,
			"type":"Block",
			"property":data.property,
			"stay_room_id":data.name,
			"is_active":1
		}).insert()
	#check if block date is equal to current system date than change room status to block
	working_day = get_working_day(data.property)
	if getdate(working_day["date_working_day"])>=getdate(data.start_date) and getdate(working_day["date_working_day"])<=add_to_date(getdate(data.end_date),days=-1):
		room_doc = frappe.get_doc("Room", data.room_id)
		room_doc.housekeeping_status = data.housekeeping_status 
		room_doc.save()