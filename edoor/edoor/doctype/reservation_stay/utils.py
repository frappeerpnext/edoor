import frappe
def update_fetch_from_fields(self):
	data_for_updates = []
	data_value_for_update ={}
	condiction_keys = [
		{
      		"key":"name",
   			"doctypes":["Reservation Stay"]
      	}
	]
	if self.has_value_changed("reservation_status"):
		if self.reservation_status == 'In-house' and self.reservation_color:
			data_for_updates.append({"doctype":"Reservation Stay","update_field":"reservation_color=''"})
			data_for_updates.append({"doctype":"Reservation Stay","update_field":"reservation_color_code=''"})

		status_color=frappe.db.get_value("Reservation Status",self.reservation_status,"color")
		data_value_for_update["reservation_status"] = self.reservation_status
		data_value_for_update["status_color"] = status_color

  
		data_for_updates.append({"doctype":"Folio Transaction","update_field":"reservation_status='{}'".format(status_color)})
		data_for_updates.append({"doctype":"Folio Transaction","update_field":"reservation_status_color='{}'".format(status_color)})
		
		data_for_updates.append({"doctype":"Reservation Folio","update_field":"reservation_status='{}'".format(self.reservation_status)})
		data_for_updates.append({"doctype":"Reservation Folio","update_field":"reservation_status_color='{}'".format(status_color)})
		data_for_updates.append({"doctype":"Room Occupy","update_field":"reservation_status='{}'".format(self.reservation_status)})
	if self.has_value_changed("business_source"):
		#Revenue Forecast Breakdown
		data_for_updates.append({"doctype":"Revenue Forecast Breakdown","update_field":"business_source='{}'".format(self.business_source)})
		
	# guest
	if self.has_value_changed("guest"):		
  
		data_for_updates.append({"doctype":"Revenue Forecast Breakdown","update_field":"guest='{}'".format(self.guest)})
		data_for_updates.append({"doctype":"Revenue Forecast Breakdown","update_field":"guest_type='{}'".format(self.guest_type)})
		data_for_updates.append({"doctype":"Revenue Forecast Breakdown","update_field":"nationality='{}'".format(self.nationality)})
		
		data_for_updates.append({"doctype":"Reservation Room Rate","update_field":"guest='{}'".format(self.guest)})
		data_for_updates.append({"doctype":"Reservation Room Rate","update_field":"guest_name='{}'".format(self.guest_name)})
		data_for_updates.append({"doctype":"Reservation Room Rate","update_field":"guest_type='{}'".format(self.guest_type)})
		data_for_updates.append({"doctype":"Reservation Room Rate","update_field":"nationality='{}'".format(self.nationality)})


		
	
	if data_for_updates:
		for d in set([x["doctype"] for x in data_for_updates]):
			key = [f["key"] for f in condiction_keys if d in f["doctypes"]]
			
			key = "reservation_stay" if not key else key[0]

			sql="update `tab{}` set {} where {}='{}'".format(
				d,
				",".join([x["update_field"] for x in data_for_updates if x["doctype"]==d]),
				key,
				self.name
			)

			frappe.db.sql(sql)	
		
    