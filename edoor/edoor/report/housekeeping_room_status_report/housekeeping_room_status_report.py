
import frappe
from frappe import _
from frappe.utils import date_diff,today ,add_months, add_days
from frappe.utils.data import strip
from dateutil.rrule import rrule, MONTHLY
from datetime import datetime, timedelta
import uuid

def execute(filters=None):
	# data = get_guest_data(filters)
	# summary = get_summary(filters,data)
	report_data = get_data(filters)
	return get_columns(filters),report_data,None,None, None


# def get_summary(filters,data):
# 	get_count = {d['reservation'] for d in data}
# 	if filters.show_summary:
# 		return [
# 			{ "label":"Total Room","value":len(data),"indicator":"red"},
# 			{ "label":"Total Reservation","value":len(get_count),"indicator":"red"},
# 			{ "label":"Total Room Nights","value":sum([d["room_nights"] for d in data ]),"indicator":"blue"},
# 			{ "label":"Total Pax(A/C)","value":"{}/{}".format(sum([d["adult"] for d in data ]),sum([d["child"] for d in data]))},
# 			{ "label":"Arrival Guest","value": len(data),"indicator":"red"},
# 			# { "label":"Total Credit","value":len({d[''] for d in data}),"indicator":"green"},
# 			{ "label":"Departure Guest","value":len(data),"indicator":"blue"},
# 		]

def get_columns(filters):
	columns =   [
		{"fieldname":"room_number", "label":"Room #",'align':'left',"width":130,"show_in_report":1,},
		{"fieldname":"housekeeping_status", "label":"Status",'align':'left', "width":115,"show_in_report":1,},
		{'fieldname':'room_type','align':'left','label':'Room Type',"width":170,"show_in_report":1},
		{'fieldname':'reservation_stay','label':'Stay #','fieldtype':'Link','options':"Reservation Stay","header_class":'text-center','post_message_action':"view_reservation_stay_detail","default":True,"show_in_report":1},
		{"fieldname":"guest", "label":"Guest", "fieldtype":"Link","options":"Customer","width":90,"show_in_report":0,"post_message_action": "view_guest_detail","url":"/frontdesk/guest-detail"},
		{"fieldname":"guest_name", "label":"Guest Name",'align':'left',"width":90,"show_in_report":1},
		{'fieldname':'reservation_status','label':'Status','align':'center',"width":95,"show_in_report":1},
		{'fieldname':'housekeeper','label':'Housekeeper','align':'left',"show_in_report":1,"width":90},
	]
	return columns

def get_filters_data(filters):
	sql = " and property=%(property)s"
	
	if filters.room_types:
		sql = sql + " and r.room_type_id in %(room_types)s"
	if filters.building:
		sql = sql + " and r.building in %(building)s"
	if filters.floor:
		sql = sql + " and r.floor in %(floor)s"

	if filters.housekeeper:
		sql = sql + " and r.housekeeper in %(housekeeper)s"
	if filters.housekeeping_status:
		sql = sql + " and r.housekeeping_status in %(housekeeping_status)s"
	
	sql = sql + " order by {} {}".format(
		[d for d in  get_order_field() if d["label"] == filters.order_by][0]["field"],
		filters.sort_order
	)

	return sql
def get_order_field():
	return [
		{"label":"Created On","field":"r.creation"},
		{"label":"Reservation","field":"r.reservation"},
		{"label":"Reservation Stay","field":"r.name"},
		{"label":"Arrival Date","field":"r.arrival_date"},
		{"label":"Departure Date","field":"r.departure_date"},
		{"label":"Room Type","field":"r.room_type_alias"},
		{"label":"Business Source","field":"r.business_source"},
		{"label":"Reservation Status","field":"r.reservation_status"},
		{"label":"Last Update On","field":"r.modified"},
		]

def get_data(filters):
	sql="""
		select
				name,
				room_number,
				housekeeping_status,
				housekeeping_status_code,
				room_status,
				building,
				'' as reservation_status,
				status_color,
				housekeeper,
				room_type,
				floor,
				'' as room_block
		from `tabRoom` r
		where
				1=1  
				{}
			
		""".format(get_filters_data(filters))

	data =   frappe.db.sql(sql,filters,as_dict=1)
	return data

def get_filters(filters):
	sql = " and property=%(property)s and date = %(start_date)s"
	
	if filters.room_types:
		sql = sql + " and rc.room_type_id in %(room_types)s"
	if filters.building:
		sql = sql + " and rc.building in %(building)s"
	if filters.floor:
		sql = sql + " and rc.floor in %(floor)s"
	
	
	sql = sql + " order by {} {}".format(
		[d for d in  get_order_field() if d["label"] == filters.order_by][0]["field"],
		filters.sort_order
	)

	return sql
def get_order_field_data():
	return [
		{"label":"Created On","field":"rc.creation"},
		{"label":"Reservation","field":"rc.reservation"},
		{"label":"Reservation Stay","field":"rc.name"},
		{"label":"Arrival Date","field":"rc.arrival_date"},
		{"label":"Departure Date","field":"rc.departure_date"},
		{"label":"Room Type","field":"rc.room_type_alias"},
		{"label":"Business Source","field":"rc.business_source"},
		{"label":"Reservation Status","field":"rc.reservation_status"},
		{"label":"Last Update On","field":"rc.modified"},
		]
def get_reservation_stay_data(filters):
	sql ="""
      select 
            date,
            room_id,
            is_arrival,                           
            is_departure, 
            reservation_stay,                      
            reservation_status,
            type,
            stay_room_id

      from `tabRoom Occupy` rc
      where 
				1=1  
				{}
			
		""".format(get_filters(filters))
	occupy_data =   frappe.db.sql(sql,filters,as_dict=1)
	return occupy_data

def get_report_date(filters,data,occupy_data):
	report_data = []
	

	return report_data


