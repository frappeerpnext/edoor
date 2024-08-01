import frappe
def update_fetch_from_fields(self):
	data_for_updates = []
	data_value_for_update ={}
 
	if self.has_value_changed("reservation_status"):
		if self.reservation_status == 'In-house':
			frappe.db.set_value("Reservation Stay", self.name, {"reservation_color": "", "reservation_color_code": ""})

		status_color=frappe.db.get_value("Reservation Status",self.reservation_status,"color")
		data_value_for_update["reservation_status"] = self.reservation_status
		data_value_for_update["status_color"] = status_color

  
		data_for_updates.append({"doctype":"Folio Transaction","update_field":"reservation_status=%(reservation_status)s"})
		data_for_updates.append({"doctype":"Folio Transaction","update_field":"reservation_status_color=%(status_color)s"})
		
		data_for_updates.append({"doctype":"Reservation Folio","update_field":"reservation_status=%(reservation_status)s"})
		data_for_updates.append({"doctype":"Reservation Folio","update_field":"reservation_status_color=%(status_color)s"})
		data_for_updates.append({"doctype":"Room Occupy","update_field":"reservation_status=%(reservation_status)s"})
	if self.has_value_changed("business_source"):
		#Revenue Forecast Breakdown
		data_value_for_update["business_source"] = self.business_source
		data_for_updates.append({"doctype":"Revenue Forecast Breakdown","update_field":"business_source=%(business_source)s"})
		
	# guest
	if self.has_value_changed("guest"):		
		data_value_for_update["guest"] = self.guest
		data_value_for_update["guest_name"] = self.guest_name
		data_value_for_update["guest_type"] = self.guest_type
		data_value_for_update["nationality"] = self.nationality
  
		data_for_updates.append({"doctype":"Revenue Forecast Breakdown","update_field":"guest=%(guest)s"})
		data_for_updates.append({"doctype":"Revenue Forecast Breakdown","update_field":"guest_type=%(guest_type)s"})
		data_for_updates.append({"doctype":"Revenue Forecast Breakdown","update_field":"nationality=%(nationality)s"})
		
		data_for_updates.append({"doctype":"Reservation Room Rate","update_field":"guest=%(guest)s"})
		data_for_updates.append({"doctype":"Reservation Room Rate","update_field":"guest_name=%(guest_name)s"})
		data_for_updates.append({"doctype":"Reservation Room Rate","update_field":"guest_type=%(guest_type)s"})
		data_for_updates.append({"doctype":"Reservation Room Rate","update_field":"nationality=%(nationality)s"})

		
	
	if data_for_updates:
		for d in set([x["doctype"] for x in data_for_updates]):
			sql="update `tab{}` set {} where reservation_stay='{}'".format(
				d,
				",".join([x["update_field"] for x in data_for_updates if x["doctype"]==d]),
				self.name
			)
			frappe.db.sql(sql,data_value_for_update)	
		
    