# Copyright (c) 2023, Tes Pheakdey and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class RoomType(Document):
	def after_insert(self):
		pass
	
	def on_update(self):
		#add_room_type_availability()
		frappe.enqueue("edoor.edoor_property_setup.doctype.room_type.room_type.add_room_type_availability", queue='long', self=self)

def add_room_type_availability(self):
	total_room = frappe.db.count ('Room', {"room_type_id":self.name })
	frappe.db.sql("update `tabRoom Type Availability` set property='{}', room_type='{}' where room_type_id='{}'".format(self.property, self.room_type,self.name))
	#update total room from now on ward
	frappe.db.sql("update `tabRoom Type Availability` set total_rooms={}  where room_type_id='{}' and date>=cast(now() as date)".format(total_room,self.name))
	
	sql = "select date from `tabDates` where date<=cast(DATE_ADD(now(), INTERVAL 1 Year) as date) and date not in (select date from `tabRoom Type Availability` where room_type_id='{}')".format(self.name)
	data = frappe.db.sql(sql,as_dict=1)
	for  d in data:
		frappe.get_doc({
			"doctype":"Room Type Availability",
			"date":d["date"],
			"room_type_id":self.name,
			"total_rooms":total_room,

		}).insert()


	
