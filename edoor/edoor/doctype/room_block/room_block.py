# Copyright (c) 2023, Tes Pheakdey and contributors
# For license information, please see license.txt

from datetime import datetime
from edoor.api.utils import get_date_range
import frappe
from frappe.model.document import Document
from frappe.utils.data import add_to_date, getdate, pretty_date
from edoor.api.frontdesk import get_working_day

class RoomBlock(Document):
	def validate(self):
		self.housekeeping_status = frappe.db.get_default("room_block_status")
		 
		self.status_color = frappe.get_value("Housekeeping Status",self.housekeeping_status, "status_color")
		
		# if datetime.strptime(self.start_date, "%Y-%m-%d").date() < datetime.now().date():
		# 	frappe.throw("Start date cannot be less than current date")
		
		if datetime.strptime(self.end_date, "%Y-%m-%d").date() < datetime.now().date():
			frappe.throw("End date cannot be less than current date")
		
		if datetime.strptime(self.end_date, "%Y-%m-%d").date() < datetime.strptime(self.start_date, "%Y-%m-%d").date():
			frappe.throw("End date cannot be less than start date")
		
	def before_submit(self):
		sql = "select name, date,type from `tabTemp Room Occupy` where room_id='{}' and date between '{}' and '{}' and property='{}' limit 1"
		sql = sql.format(self.room_id, self.start_date, self.end_date, self.property)
		data = frappe.db.sql(sql, as_dict=1)
		if data:
			frappe.throw("Room {} is already occupy or block on date {}".format( self.room_number,data[0]["date"].strftime("%d-%m-%Y")))


	def on_submit(self):
		#generate room to temp room occupy
		dates = get_date_range( datetime.strptime(self.start_date, "%Y-%m-%d").date(), add_to_date (getdate(self.end_date),days=-1),False)
		
		for d in dates: 
			frappe.get_doc({
				"doctype":"Temp Room Occupy",
				"room_type_id":self.room_type_id,
				"room_id":self.room_id,
				"date":d,
				"type":"Block",
				"property":self.property,
				"stay_room_id":self.name,
			}).insert()


			#generate room to room occupy
			frappe.get_doc({
				"doctype":"Room Occupy",
				"room_type_id":self.room_type_id,
				"room_id":self.room_id,
				"date":d,
				"type":"Block",
				"property":self.property,
				"stay_room_id":self.name,
			}).insert()
		#check if block date is equal to current system date than change room status to block
		working_day = get_working_day(self.property)
		if getdate(working_day["date_working_day"])>=getdate(self.start_date) and getdate(working_day["date_working_day"])<=add_to_date(getdate(self.end_date),days=-1):
			 
			room_doc = frappe.get_doc("Room", self.room_id)
			room_doc.housekeeping_status = self.housekeeping_status 
			room_doc.save()


	def on_update_after_submit(self):
		room_doc = frappe.get_doc("Room", self.room_id)
		room_doc.housekeeping_status = self.unblock_housekeeping_status 
		room_doc.save()


	def on_cancel(self):
		frappe.db.sql("delete from `tabTemp Room Occupy` where type='Block' and stay_room_id='{}' and room_id='{}' and property='{}'".format(self.name,self.room_id,self.property))
		frappe.db.sql("delete from `tabRoom Occupy` where type='Block' and stay_room_id='{}' and room_id='{}' and property='{}'".format(self.name,self.room_id,self.property))

