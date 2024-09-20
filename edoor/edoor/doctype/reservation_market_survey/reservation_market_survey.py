# Copyright (c) 2024, Tes Pheakdey and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class ReservationMarketSurvey(Document):
	pass

@frappe.whitelist()
def get_doc(reservation):
	if frappe.db.exists("Reservation Market Survey",{"reservation":reservation}):
		return frappe.get_doc("Reservation Market Survey",reservation)
	else:
		return {"reservation":reservation}
