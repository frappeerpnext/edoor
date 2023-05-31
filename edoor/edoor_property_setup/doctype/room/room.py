# Copyright (c) 2023, Tes Pheakdey and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class Room(Document):
	def validate(self): 
		if self.housekeeping_status:
			self.status_color = frappe.db.get_value("Housekeeping Status", self.housekeeping_status, "status_color")


	def after_insert(self):
		#update total_rooms to room type availability
		total_room = frappe.db.count ('Room', { 'property': self.property, "room_type_id":self.room_type_id })
		frappe.db.sql("update `tabRoom Type Availability` set total_rooms={} where room_type_id='{}' and date>now()".format(total_room, self.room_type_id))