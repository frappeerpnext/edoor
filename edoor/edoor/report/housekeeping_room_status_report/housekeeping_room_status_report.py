
import frappe
from edoor.api.frontdesk import get_working_day
from frappe import _
from frappe.utils import date_diff,today ,add_months, add_days
from frappe.utils.data import strip
from dateutil.rrule import rrule, MONTHLY
from datetime import datetime, timedelta
import uuid

def execute(filters=None):
	# data = get_guest_data(filters)
	# summary = get_summary(filters,data)
	data = get_data(filters)
	occupy_data = get_occupy_data(filters)
	report_data = get_report_data(filters,data,occupy_data)
	return get_columns(filters),report_data,None,None, None


def get_columns(filters):
	columns =   [
		{"fieldname":"room_number", "label":"Room #",'align':'left',"width":130,"show_in_report":1,},
		{"fieldname":"housekeeping_status", "label":"Status",'align':'left', "width":160,"show_in_report":1,},
		{'fieldname':'room_type','align':'left','label':'Room Type',"width":170,"show_in_report":1},
		{'fieldname':'reservation_stay','label':'Stay #',"width":130,'fieldtype':'Link','options':"Reservation Stay","header_class":'text-center','post_message_action':"view_reservation_stay_detail","default":True,"show_in_report":1},
		{"fieldname":"guest", "label":"Guest", "fieldtype":"Link","options":"Customer","width":130,"show_in_report":0,"post_message_action": "view_guest_detail","url":"/frontdesk/guest-detail"},
		{"fieldname":"guest_name", "label":"Guest Name",'align':'left',"width":130,"show_in_report":1},
		{'fieldname':'reservation_status','label':'Status','align':'center',"width":110,"show_in_report":1},
		{'fieldname':'housekeeper','label':'Housekeeper','align':'left',"show_in_report":1,"width":100},
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
		[d for d in  get_order_field_data() if d["label"] == filters.order_by][0]["field"],
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
def get_occupy_data(filters):
	sql ="""
      select 
            date,
            room_id,
            is_arrival,                           
            is_departure,
			is_active,
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

def get_report_data(filters,data,occupy_data):
	working_day = get_working_day(filters["property"])
	
	for d in occupy_data:
		data_room = [r for r in data if r['name']==d['room_id']]
		room = None
		if data_room:
			room = data_room[0]
			
			if room:
				
				if d.get("type") =="Reservation":
					room['reservation_stay'] = d['reservation_stay']
					room['reservation_status'] = d['reservation_status']

					if d['is_arrival'] == 1:
						if working_day["date_working_day"] == d["date"] and d["reservation_status"]=="Reserved":
							room['reservation_status'] = "Arrival"
					elif  d["is_departure"] == 1 and d["reservation_status"] in ["In-house","Reserved"]:
						room["reservation_status"] = "Departure"
					elif d["is_arrival"]==0 and d["is_departure"] ==0 and d["reservation_status"] in ["In-house"]:
						room["reservation_status"] = "Stay Over"

					if d["reservation_stay"]:
						guest, guest_name = frappe.db.get_value('Reservation Stay', d["reservation_stay"] , ['guest', 'guest_name'])
						room["guest"] =guest
						room["guest_name"] =guest_name
				else:
					room["room_block"] = d["stay_room_id"]
					room["housekeeping_status"] = frappe.db.get_single_value("eDoor Setting","room_block_status")
					room["status_color"] = frappe.db.get_single_value("eDoor Setting","room_block_color")

	return data


