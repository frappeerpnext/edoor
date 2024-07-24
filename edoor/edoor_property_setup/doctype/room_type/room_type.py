# Copyright (c) 2023, Tes Pheakdey and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class RoomType(Document):
	def after_insert(self):
		pass
		
	def on_update(self):
		if self.creation != self.modified:
			update_fetch_from_fields(self)
   
def update_fetch_from_fields(self):
	data_for_updates = []

	if self.has_value_changed("room_type_group"):
		data_for_updates.append({"doctype":"Room","update_field":"room_type_group='{}'".format(self.room_type_group)})
	
	if self.has_value_changed("room_type"):
		data_for_updates.append({"doctype":"Room","update_field":"room_type='{}'".format(self.room_type)})
		data_for_updates.append({"doctype":"Deposit Ledger","update_field":"room_type='{}'".format(self.room_type)})
		data_for_updates.append({"doctype":"Desk Folio","update_field":"room_type='{}'".format(self.room_type)})
		data_for_updates.append({"doctype":"Folio Transaction","update_field":"room_type='{}'".format(self.room_type)})
		data_for_updates.append({"doctype":"Payable Ledger","update_field":"room_type='{}'".format(self.room_type)})
		data_for_updates.append({"doctype":"Rate Plan","update_field":"room_type='{}'".format(self.room_type)})
		data_for_updates.append({"doctype":"Reservation Room Rate","update_field":"room_type='{}'".format(self.room_type)})
		data_for_updates.append({"doctype":"Reservation Stay Room","update_field":"room_type='{}'".format(self.room_type)})
  
	if self.has_value_changed("alias"):
		data_for_updates.append({"doctype":"Folio Transaction","update_field":"room_type_alias='{}'".format(self.alias)})
		data_for_updates.append({"doctype":"Reservation Room Rate","update_field":"room_type_alias='{}'".format(self.alias)})
		data_for_updates.append({"doctype":"Reservation Stay Room","update_field":"room_type_alias='{}'".format(self.alias)})
		data_for_updates.append({"doctype":"Room","update_field":"room_type_alias='{}'".format(self.alias)})
		
	if data_for_updates:
		for d in set([x["doctype"] for x in data_for_updates]):
			sql="update `tab{}` set {} where room_type_id='{}'".format(
				d,
				",".join([x["update_field"] for x in data_for_updates if x["doctype"]==d]),
				self.name
			)
			
			frappe.db.sql(sql)