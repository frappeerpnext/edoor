# Copyright (c) 2023, Tes Pheakdey and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document
from frappe.utils.data import now

class FrontdeskNote(Document):
	def validate(self):
		if not hasattr(self, 'note_date') and self.note_date:
			self.note_date = now()
