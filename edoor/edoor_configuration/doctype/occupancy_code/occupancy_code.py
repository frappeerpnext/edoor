# Copyright (c) 2026, Tes Pheakdey and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class OccupancyCode(Document):
	def on_update(self):
		# clear chache
		frappe.cache.delete_value("occupancy_codes") 
		properties = frappe.get_all("Business Branch")
		for p in properties:
			frappe.cache.delete_value(f"{p.get('name')}_occupancy_codes") 


