# Copyright (c) 2024, Tes Pheakdey and contributors
# For license information, please see license.txt

# import frappe


import frappe
from frappe import _
from frappe.utils import date_diff,today ,add_months, add_days
from frappe.utils.data import strip
from dateutil.rrule import rrule, MONTHLY
from datetime import datetime, timedelta
import uuid
def execute(filters=None): 

	if filters.summary_filter:
		if not filters.summary_fields:
			filters.summary_fields = ['total_record', 'room_night']

	 

	data = get_data(filters)
	report_data = get_report_data(filters,data)
	Summary = get_summary(filters,data)
	return get_columns(filters),report_data,None,None, None

def validate(filters):
	datediff = date_diff(filters.end_date, filters.start_date)
	if filters.start_date and filters.end_date:
		if filters.start_date > filters.end_date:
			frappe.throw("The 'Start Date' ({}) must be before the 'End Date' ({})".format(filters.start_date, filters.end_date))
		if datediff > 30:
			frappe.throw("Your Max date for viewing transaction is only One Month.".format(filters.start_date, filters.end_date))

def get_columns(filters):
	columns =   [
		{"fieldname":"reservation", "label":"Res #",'align':'left', "fieldtype":"Link","options":"Reservation","width":150,"show_in_report":1,"post_message_action": "view_reservation_detail","url":"/frontdesk/reservation-detail"},
		{"fieldname":"reservation_stay", "label":"Stay #",'align':'left', "fieldtype":"Link","options":"Reservation Stay","width":150,"show_in_report":1,"url":"/frontdesk/stay-detail","post_message_action": "view_reservation_stay_detail"},
		{"fieldname":"date", 'align':'center',"label":"Date", "fieldtype":"Date","width":120,"show_in_report":1},
		{'fieldname': 'room_type', 'label': 'Room Type','align':'left',"width":170,"show_in_report":1},
		{'fieldname': 'room_number', 'label': 'Room','align':'left',"width":150,"show_in_report":1},
		{'fieldname': 'rate_type', 'label': 'Rate Type','align':'left',"width":150,"show_in_report":1},
		{'fieldname':'business_source','label':'Source','align':'left',"width":150,"show_in_report":1},
		{'fieldname':'rate','label':'Rate','align':'right',"width":90,"show_in_report":1,"fieldtype":"Currency"},
		{'fieldname':'discount','label':'Discount','align':'right',"width":90,"show_in_report":1,"fieldtype":"Currency"},
		{'fieldname':'tax','label':'Tax','align':'right',"width":90,"show_in_report":1,"fieldtype":"Currency"},
		{'fieldname':'total_rate','label':'Total Rate','align':'right',"width":90,"show_in_report":1,"fieldtype":"Currency"},
		
	]
	return columns


def get_summary(filters,data):
	get_count = {d['reservation'] for d in data}
	if filters.show_summary:
		return [
			{ "label":"Total Room","value":len(data),"indicator":"red"},
			{ "label":"Total Reservation","value":len(get_count),"indicator":"red"},
			
		]


def get_filters(filters):
	sql = " and property=%(property)s and reservation_stay in (select name from `tabReservation Stay`) and date between %(start_date)s and %(end_date)s "
	if filters.business_source:
		sql = sql + " and rr.business_source = %(business_source)s "
	
	if filters.room_types:
		sql = sql + " and rr.room_type_id = %(room_types)s"

	sql = sql + " order by {} {}".format(
		[d for d in  get_order_field() if d["label"] == filters.order_by][0]["field"],
		filters.sort_order
	)

	return sql

def get_order_field():
	return [
		{"label":"Created On","field":"rr.creation"},
		{"label":"Reservation","field":"rr.reservation"},
		{"label":"Reservation Stay","field":"rr.name"},
		{"label":"Arrival Date","field":"rr.arrival_date"},
		{"label":"Departure Date","field":"rr.departure_date"},
		{"label":"Room Type","field":"rr.room_type_alias"},
		{"label":"Business Source","field":"rr.business_source"},
		{"label":"Reservation Status","field":"rr.reservation_status"},
		{"label":"Last Update On","field":"rr.modified"},
		]

def get_data(filters):
	sql="""
			select date, 
                reservation, 
                reservation_stay, 
                business_source, 
                room_type, 
                room_number, 
                rate_type, 
				rate, 
                discount_amount, 
                total_tax, 
                total_rate,
				is_complimentary,
				is_house_use
            from 
                `tabReservation Room Rate` rr
			where
				1=1  
				{}
			
		""".format(get_filters(filters))

	

	data =   frappe.db.sql(sql,filters,as_dict=1)
	return data

def get_report_data(filters,data):

	report_data = []
	is_complimentary = sorted(set([d['is_complimentary'] for d in data if d['is_complimentary'] == 1]))
	if is_complimentary:
		report_data.append({
			"indent":0,
			"reservation":"Complimentary Room",
			"is_group":1
		})
		
		report_data = report_data +  [d.update({"indent":1}) or d for d in data if d['is_complimentary'] == 1]

	house_use = sorted(set([d['is_house_use'] for d in data if d['is_house_use'] == 1]))
	if house_use:
		report_data.append({
			"indent":0,
			"reservation":"House Use Room",
			"is_group":1
		})
		
		report_data = report_data +  [d.update({"indent":1}) or d for d in data if d['is_house_use'] == 1]
		
	return report_data

	



	


