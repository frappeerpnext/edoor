# Copyright (c) 2023, Tes Pheakdey and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class Room(Document):
	def validate(self): 
		if not self.reservation_stay:
			self.guest = None
			self.arrival_date = None
			self.departure_date = None
			self.guest_name = None

		if self.housekeeping_status_code and self.room_status and self.room_status!="Room Block": 
			status = frappe.db.get_list("Housekeeping Status", filters={"room_status":self.room_status, "housekeeping_status_code":self.housekeeping_status_code}, fields=["name","status_color", "icon","show_in_room_availability","is_block_room"])
			if len(status)>0:
				self.housekeeping_status = status[0].name
				self.status_color = status[0].status_color
				self.housekeeping_icon= status[0].icon
				self.show_in_room_availability= status[0].show_in_room_availability
				self.block_room= status[0].is_block_room
		elif  self.room_status=="Room Block":
 
			status = frappe.db.get_list("Housekeeping Status", filters={"room_status":self.room_status}, fields=["name","status_color", "icon","show_in_room_availability","is_block_room"],ignore_permissions=True)
			if len(status)>0:
				self.housekeeping_status = status[0].name
				self.status_color = status[0].status_color
				self.housekeeping_icon= status[0].icon
				self.show_in_room_availability= status[0].show_in_room_availability
				self.block_room= status[0].is_block_room
