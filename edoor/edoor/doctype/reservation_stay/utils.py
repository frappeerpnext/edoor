import frappe
def update_fetch_from_fields(self):
	data_for_updates = []
	if self.has_value_changed("reservation_status"):
		status_color=frappe.db.get_value("Reservation Status",self.reservation_status,"color")
		data_for_updates.append({"doctype":"Folio Transaction","update_field":"reservation_status='{}'".format(self.reservation_status)})
		data_for_updates.append({"doctype":"Folio Transaction","update_field":"reservation_status_color='{}'".format(status_color)})
		
		data_for_updates.append({"doctype":"Reservation Folio","update_field":"reservation_status='{}'".format(self.reservation_status)})
		data_for_updates.append({"doctype":"Reservation Folio","update_field":"reservation_status_color='{}'".format(status_color)})
		data_for_updates.append({"doctype":"Room Occupy","update_field":"reservation_status='{}'".format(self.reservation_status)})

	if data_for_updates:
		for d in set([x["doctype"] for x in data_for_updates]):
			sql="update `tab{}` set {} where reservation_stay='{}'".format(
				d,
				",".join([x["update_field"] for x in data_for_updates if x["doctype"]==d]),
				self.name
			)
			frappe.db.sql(sql)	
		
    