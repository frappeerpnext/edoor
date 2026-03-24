# Copyright (c) 2026, Tes Pheakdey and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from edoor.channel_managers.exely.property_info import send_property_info


class ChannelManagerIntegration(Document):
	@frappe.whitelist()
	def get_property_info(self):
		data = send_property_info()
		
		room_types = data.get("room_types", [])
		rate_plans = data.get("rate_plans", [])
		payment_types = data.get("payment_types", [])
		services = data.get("services", [])
		

		# assign room types		self.room_types = []
		
		for room_type in room_types:
			if not any(d.room_type_code == room_type.get("room_type_code") for d in self.room_types):
				self.append("room_types", {
					"room_type_code": room_type.get("room_type_code"),
					"room_type_name": room_type.get("room_type_name"),
					"data": room_type.get("data")
				})

		# assign rate plans
		for rate_plan in rate_plans:
			if not any(d.rate_plan_code == rate_plan.get("rate_plan_code") for d in self.rate_plans):
				self.append("rate_plans", {
					"rate_plan_code": rate_plan.get("rate_plan_code"),
					"rate_plan_name": rate_plan.get("rate_plan_name")
				})

		# assign payment types
		for payment_type in payment_types:
			if not any(d.payment_type_code == payment_type.get("payment_type_code") for d in self.payment_types):
				
				self.append("payment_types", {
					"payment_type_code": payment_type.get("payment_type_code"),
					"payment_type_name": payment_type.get("payment_type_name"),
					"payment_type_title": payment_type.get("payment_type_title")
				
				})

		# assign services
		for service in services:
			if not any(d.services_code == service.get("services_code") for d in self.services):
				self.append("services", {
					"services_code": service.get("services_code"),
					"service_name": service.get("service_name")
				})

		self.save()
		frappe.msgprint("Property information has been successfully retrieved and saved to the document.")