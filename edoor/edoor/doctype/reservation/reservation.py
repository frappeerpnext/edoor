# Copyright (c) 2023, Tes Pheakdey and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from edoor.api.frontdesk import get_working_day

class Reservation(Document):
	def validate(self):
		if self.departure_date<=self.arrival_date:
			frappe.throw("Departure date cannot less than or equal to arrival date")

		working_day = get_working_day(self.property)
		if not working_day:
			frappe.throw("There is no working open")
		else:

			if not working_day["cashier_shift"]:
				frappe.throw("There is no cashier open. Please open your cashier shift")
			if self.is_new():
				self.working_day = working_day["name"]
				self.working_date = working_day["date_working_day"]
				self.cashier_shift = working_day["cashier_shift"]["name"]

				

		self.pax = (self.adult or 1) + (self.child or 0)
		data = frappe.db.get_list("Reservation Stay",filters={"reservation":self.name})
		for d in data:
			doc = frappe.get_doc("Reservation Stay",d)
			doc.reservation_type=self.reservation_type
			doc.save()

			#frappe.db.set_value("Reservation Stay",d,"reservation_type",)


