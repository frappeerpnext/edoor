# Copyright (c) 2026, Tes Pheakdey and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from edoor.channel_managers.utils import clear_cache   as clear_cm_cached

class OccupancyCode(Document):
	def on_update(self):
	 
		clear_cache()
 

	def on_trash(self):
		clear_cache()

def clear_cache():
	clear_cm_cached()
	frappe.cache.delete_value("occupancy_codes") 
	properties = frappe.get_all("Business Branch")
	for p in properties:
		frappe.cache.delete_value(f"{p.get('name')}_occupancy_codes") 

