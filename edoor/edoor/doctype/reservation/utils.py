
import frappe

def update_fetch_from_fields(self):
	data_for_updates = []
	
	
	
    
	data_for_updates = data_for_updates +  business_source_change(self)
	data_for_updates = data_for_updates +  reservation_type_change(self)
	data_for_updates = data_for_updates +   group_code_change(self)
	data_for_updates = data_for_updates +   group_name_change(self)
	data_for_updates = data_for_updates +   group_color_change(self)

	if data_for_updates:
		frappe.clear_document_cache('Reservation', self.name)
		for d in set([x["doctype"] for x in data_for_updates]):
			sql="update `tab{}` set {} where reservation='{}'".format(
				d,
				",".join([x["update_field"] for x in data_for_updates if x["doctype"]==d]),
				self.name
			)
			frappe.db.sql(sql)

def business_source_change(self):
	data_for_updates = []
	if self.has_value_changed("business_source"):
		
		business_source_type = frappe.db.get_value("Business Source",self.business_source, "business_source_type")
		data_for_updates.append({"doctype":"Reservation Stay Room","update_field":"business_source='{}'".format(self.business_source)})
		
		data_for_updates.append({"doctype":"Reservation Stay","update_field":"business_source='{}'".format(self.business_source)})
		data_for_updates.append({"doctype":"Reservation Stay","update_field":"business_source_type='{}'".format(self.business_source_type)})
		
		# folio transaction
		data_for_updates.append({"doctype":"Folio Transaction","update_field":"business_source='{}'".format(self.business_source)})
		data_for_updates.append({"doctype":"Folio Transaction","update_field":"business_source_type='{}'".format(self.business_source_type)})
		
		# reservation folio
		data_for_updates.append({"doctype":"Reservation Folio","update_field":"business_source='{}'".format(self.business_source)})
		
		# reservation room rate
		data_for_updates.append({"doctype":"Reservation Room Rate","update_field":"business_source='{}'".format(self.business_source)})
		data_for_updates.append({"doctype":"Reservation Room Rate","update_field":"business_source_type='{}'".format(self.business_source_type)})
		# Room Occupy
		data_for_updates.append({"doctype":"Room Occupy","update_field":"business_source='{}'".format(self.business_source)})
		data_for_updates.append({"doctype":"Room Occupy","update_field":"business_source_type='{}'".format(self.business_source_type)})
		#Revenue Forecast Breakdown
		data_for_updates.append({"doctype":"Revenue Forecast Breakdown","update_field":"business_source='{}'".format(self.business_source)})
		data_for_updates.append({"doctype":"Revenue Forecast Breakdown","update_field":"business_source_type='{}'".format(self.business_source_type)})

	return data_for_updates 

def reservation_type_change(self):
	data_for_updates = []
	if self.has_value_changed("reservation_type"):
		# clear chache 
  
		data_for_updates.append({"doctype":"Reservation Stay","update_field":"reservation_type='{}'".format(self.reservation_type)})
		data_for_updates.append({"doctype":"Reservation Stay Room","update_field":"reservation_type='{}'".format(self.reservation_type)})
		data_for_updates.append({"doctype":"Folio Transaction","update_field":"reservation_type='{}'".format(self.reservation_type)})
		data_for_updates.append({"doctype":"Reservation Room Rate","update_field":"reservation_type='{}'".format(self.reservation_type)})
		data_for_updates.append({"doctype":"Room Occupy","update_field":"reservation_type='{}'".format(self.reservation_type)})
		#Revenue Forecast Breakdown
		data_for_updates.append({"doctype":"Revenue Forecast Breakdown","update_field":"reservation_type='{}'".format(self.reservation_type)})
		
	return data_for_updates  

def group_code_change(self):
    data_for_updates = []
    if self.has_value_changed("group_code"):
        data_for_updates.append({"doctype":"Reservation Stay","update_field":"group_code='{}'".format(self.group_code)})
        data_for_updates.append({"doctype":"Reservation Stay Room","update_field":"group_code='{}'".format(self.group_code)})
        
    return data_for_updates

def group_name_change(self):
    data_for_updates = []
    if self.has_value_changed("group_name"):
        data_for_updates.append({"doctype":"Reservation Stay","update_field":"group_name='{}'".format(self.group_name)})
        data_for_updates.append({"doctype":"Reservation Stay Room","update_field":"group_name='{}'".format(self.group_name)})
        
    return data_for_updates

def group_color_change(self):
    data_for_updates = []
    if self.has_value_changed("group_color"):
        data_for_updates.append({"doctype":"Reservation Stay","update_field":"group_color='{}'".format(self.group_color)})
        data_for_updates.append({"doctype":"Reservation Stay Room","update_field":"group_color='{}'".format(self.group_color)})
        
    return data_for_updates