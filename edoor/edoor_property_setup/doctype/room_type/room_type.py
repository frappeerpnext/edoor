# Copyright (c) 2023, Tes Pheakdey and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class RoomType(Document):
	def after_insert(self):
		pass
	
	def on_update(self):
		sql = "update `tabRoom` set room_type_group = '{}' where room_type_id='{}'".format(self.room_type_group, self.name)
		frappe.db.sql(sql)


	
