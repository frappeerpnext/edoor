# Copyright (c) 2023, Tes Pheakdey and contributors
# For license information, please see license.txt

from edoor.api.frontdesk import get_working_day
import frappe
from frappe.model.document import Document


class DailyPropertyData(Document):
	pass

@frappe.whitelist()
def generate_property_data(property):
	if property:
		working_day = get_working_day(property)
		frappe.db.sql("delete from `tabDaily Property Data` where date>='{}' and property='{}'".format(working_day["date_working_day"], property ))

	data = frappe.db.sql("select room_type_id, count(name) as total_room from `tabRoom` where disabled = 0 group by room_type_id",as_dict=1)

	for d in data:

		sql = """
			insert into `tabDaily Property Data` (name,property,creation, owner, modified,modified_by, date, room_type_id, total_room)
			select 
				uuid(),
				%(property)s,
				now(),
				'Administrator',
				now(),
				'Administrator',
				date,
				%(room_type_id)s,
				%(total_room)s
				
			from `tabDates` d 
			where 
				d.date not in (select date from `tabDaily Property Data` where room_type_id = %(room_type_id)s) 
				
		"""
 

		filter = {
			"room_type_id":d["room_type_id"],
			"property":property,
			"total_room": d["total_room"] 
		}
		
		data = frappe.db.sql(sql,filter,as_dict=1)

	frappe.db.commit()
	
		



	

