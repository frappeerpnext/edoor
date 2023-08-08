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
		sql = "select name, date,type from `tabTemp Room Occupy` where stay_room_id != '{}' and room_id = '{}' and date between '{}' and '{}' and property='{}' limit 1"
		sql = sql.format(self.name, self.room_id, self.start_date, add_to_date(getdate(self.end_date),days=-1), self.property)
		data = frappe.db.sql(sql, as_dict=1)
		if data:
			frappe.throw("Room {} is already occupy or block on date {}".format( self.room_number,data[0]["date"].strftime("%d-%m-%Y")))


	def on_submit(self):
		generate_block_date(self)
		
	def on_update_after_submit(self):
		if self.is_unblock ==1:
			room_doc = frappe.get_doc("Room", self.room_id)
			room_doc.housekeeping_status = self.unblock_housekeeping_status 
			room_doc.save()
			frappe.db.sql("delete from `tabTemp Room Occupy` where type='Block' and stay_room_id='{}' and room_id='{}' and property='{}'".format(self.name,self.room_id,self.property))
			frappe.db.sql("delete from `tabRoom Occupy` where type='Block' and stay_room_id='{}' and room_id='{}' and property='{}'".format(self.name,self.room_id,self.property))
		else:
			#check if date is extend
			old_doc = frappe.get_doc("Room Block", self.name)
			if self.end_date != old_doc.end_date:
				#check if next block date have room occupy 
				sql = "select name, date,type from `tabTemp Room Occupy` where stay_room_id != '{}' and room_id='{}' and date between '{}' and '{}' and property='{}' and stay_room_id != '{}' limit 1 "
				sql = sql.format(self.name, self.room_id, self.start_date, add_to_date(getdate(self.end_date),days=-1), self.property,self.name)
 
				data = frappe.db.sql(sql, as_dict=1)
				if data:
					frappe.throw("Room {} is already occupy or block on date {}".format( self.room_number,data[0]["date"].strftime("%d-%m-%Y")))

				generate_block_date(self)
				 



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
		}).insert()
	#check if block date is equal to current system date than change room status to block
	working_day = get_working_day(data.property)
	if getdate(working_day["date_working_day"])>=getdate(data.start_date) and getdate(working_day["date_working_day"])<=add_to_date(getdate(data.end_date),days=-1):
			
		room_doc = frappe.get_doc("Room", data.room_id)
		room_doc.housekeeping_status = data.housekeeping_status 
		room_doc.save()