
import frappe
from frappe import _
from frappe.utils import date_diff,today ,add_months, add_days
from frappe.utils.data import strip
from dateutil.rrule import rrule, MONTHLY
from datetime import datetime, timedelta
import uuid

def execute(filters=None):
	data = get_guest_data(filters)
	summary = get_summary(filters,data)
	report_data = get_report_data(filters,data)
	return get_columns(filters),report_data,None,None, summary

def validate(filters):
	datediff = date_diff(filters.end_date, filters.start_date)
	if filters.start_date and filters.end_date:
		if filters.start_date > filters.end_date:
			frappe.throw("The 'Start Date' ({}) must be before the 'End Date' ({})".format(filters.start_date, filters.end_date))
		if datediff > 30:
			frappe.throw("Your Max date for viewing transaction is only One Month.".format(filters.start_date, filters.end_date))

def get_summary(filters,data):
	get_count = {d['reservation'] for d in data}
	if filters.show_summary:
		return [
			{ "label":"Total Room","value":len(data),"indicator":"red"},
			{ "label":"Total Reservation","value":len(get_count),"indicator":"red"},
			{ "label":"Total Room Nights","value":sum([d["room_nights"] for d in data ]),"indicator":"blue"},
			{ "label":"Total Pax(A/C)","value":"{}/{}".format(sum([d["adult"] for d in data ]),sum([d["child"] for d in data]))},
			{ "label":"Arrival Guest","value": len(data),"indicator":"red"},
			# { "label":"Total Credit","value":len({d[''] for d in data}),"indicator":"green"},
			{ "label":"Departure Guest","value":len(data),"indicator":"blue"},
		]

def get_columns(filters):
	columns =   [
		{"fieldname":"reservation", "label":"Res #",'align':'left', "fieldtype":"Link","options":"Reservation","width":130,"show_in_report":1,"post_message_action": "view_reservation_detail","url":"/frontdesk/reservation-detail"},
		{"fieldname":"name", "label":"Stay #",'align':'left', "fieldtype":"Link","options":"Reservation Stay","width":115,"show_in_report":1,"url":"/frontdesk/stay-detail","post_message_action": "view_reservation_stay_detail"},
		{"fieldname":"reference_number",'align':'left', "label":"Ref #","width":95,"show_in_report":1},
		{'fieldname':'reservation_type','align':'center','label':'Type',"width":60 ,"show_in_report":1},
		{'fieldname':'room_type_alias','align':'center','label':'Room Type',"width":50,"show_in_report":1},
		{'fieldname':'rooms','label':'Room','align':'center',"width":40,"show_in_report":1},
		{"fieldname":"arrival_date", 'align':'left',"label":"Arrival", "fieldtype":"Date","width":95,"show_in_report":1},
		{"fieldname":"departure_date",'align':'left', "label":"Departure", "fieldtype":"Date","width":95,"show_in_report":1},
		{'fieldname':'room_nights','label':'Room Night',"width":40,"show_in_report":1,'align':'center'},
		{'fieldname':'pickup_time','label':'Time','fieldtype':'Time',"width":40,"show_in_report":1,'align':'center'},
		{'fieldname':'arrival_flight_number','label':'Flight',"width":40,"show_in_report":1,'align':'center'},
		{"fieldname":"guest", "label":"Guest", "fieldtype":"Link","options":"Customer","width":90,"show_in_report":0,"post_message_action": "view_guest_detail","url":"/frontdesk/guest-detail"},
		{"fieldname":"guest_name", "label":"Guest Name",'align':'left',"width":90,"show_in_report":1},
		{'fieldname':'total_pax', 'label': 'Pax(A/C)','align':'center',"width":40,"show_in_report":1},
		{'fieldname':'business_source','label':'Source','align':'left',"width":90,"show_in_report":1},
		{'fieldname':'reservation_status','label':'Status','align':'center',"width":95,"show_in_report":1},
		{'fieldname':'note','label':'Guest Note', 'align':'right',"show_in_report":1,"width":90},
		{'fieldname':'housekeeping_note','label':'HK Note','align':'right',"show_in_report":1,"width":90},
	]
	return columns

def get_filters(filters):
	sql = " and property=%(property)s and is_active_reservation=1  "

	if filters.business_source:
		sql = sql + " and rst.business_source = %(business_source)s"
	if filters.get("room_types"):
		sql =  """{} and  name in (
			select distinct reservation_stay from `tabReservation Room Rate` rrr 
			{}	
		) """.format(sql,get_room_rate_filters(filters))
	return sql

def get_room_rate_filters(filters):
	sql = "where property=%(property)s "
	sql =  " {} and date between %(start_date)s and %(end_date)s ".format(sql) 

	if filters.business_source:
		sql = "{} and business_source =  %(business_source)s".format(sql)
	
	if filters.room_types:
		sql = "{} and room_type_id  in %(room_types)s".format(sql)
 
	return sql

def get_guest_data(filters):
	sql="""
			select 
				name,
				reservation_date,
				arrival_date,
				departure_date,
				rooms,
				modified,
				reference_number,
				creation,
				reservation_type,
				reservation,
				room_type_alias,
				room_types,
				nationality,
				business_source,
				adult,
				child,
				concat(adult,'/',child) as total_pax,
				pax,
				room_nights,
				business_source_type,
				rate_type,
				guest,
				guest_name,
				is_active_reservation,
				reservation_status,
				note,
				housekeeping_note
			from `tabReservation Stay` rst
			where
				1=1  
				{}
			
		""".format(get_filters(filters))

	data =   frappe.db.sql(sql,filters,as_dict=1)

	
	return data



def get_report_data(filters,data):
	start_date = datetime.strptime(filters.start_date, '%Y-%m-%d')
	end_date = datetime.strptime(filters.end_date, '%Y-%m-%d')
	delta = end_date - start_date
	stay_over_date=[datetime.strftime(start_date + timedelta(days=i), '%Y-%m-%d') for i in range(delta.days + 1)]

	report_data = []

	arrival = sorted(set([d["arrival_date"] for d in data if d['arrival_date'] >= start_date and d['arrival_date'] <= end_date]))
	if arrival:	
		report_data.append({
				"indent":0,
				"reservation": "Arrival Guest",
				"is_group":1,

			})	
		for g in arrival:
			d = g
			report_data.append({
				"indent":1,
				"reservation": frappe.format(d,{"fieldtype":"Date"}),
				"is_group":1,

			})
			
			report_data = report_data +  [d.update({"indent":2}) or d for d in data if d["arrival_date"]==g]
			report_data.append({
				"indent":1,
				"reservation": "Total",
				"room_nights":sum([d["room_nights"] for d in data if d["arrival_date"]==g]),
				"total_pax":"{}/{}".format(sum([d["adult"] for d in data if d["arrival_date"]==g]),sum([d["child"] for d in data if d["arrival_date"]==g])),
				"is_total_row":1,
				"is_group":1,
			})

	stay_over = sorted(set(stay_over_date))
	if stay_over:
		date = [datetime.strptime(date, '%Y-%m-%d').date() for date in stay_over]
		report_data.append({
				"indent":0,
				"reservation": "Stay Over Guest",
				"is_group":1,
			})	
		for g in date:
			d = g
			report_data.append({
				"indent":1,
				"reservation": frappe.format(d,{"fieldtype":"Date"}),
				"is_group":1,

			})
			
			report_data = report_data +  [d.update({"indent":2}) or d for d in data if d["arrival_date"]<g and d["departure_date"]>g]
			report_data.append({
				"indent":1,
				"reservation": "Total",
				"room_nights":sum([d["room_nights"] for d in data if d["arrival_date"]<g and d["departure_date"]>g]),
				"total_pax":"{}/{}".format(sum([d["adult"] for d in data if d["arrival_date"]<g and d["departure_date"]>g]),sum([d["child"] for d in data if d["arrival_date"]<g and d["departure_date"]>g])),
				"is_total_row":1,
				"is_group":1,
			})
		
	departure = sorted(set([d["departure_date"] for d in data if d['departure_date'] >= start_date and d['departure_date'] <= end_date ]))
	if departure:
		report_data.append({
				"indent":0,
				"reservation": "Departure Guest",
				"is_group":1,

			})	
		for g in departure:
			d = g
			report_data.append({
				"indent":1,
				"reservation": frappe.format(d,{"fieldtype":"Date"}),
				"is_group":1,
			})
			
			report_data = report_data +  [d.update({"indent":2}) or d for d in data if d["departure_date"]==g]
			report_data.append({
				"indent":1,
				"reservation": "Total",
				"room_nights":sum([d["room_nights"] for d in data if d["departure_date"]==g]),
				"total_pax":"{}/{}".format(sum([d["adult"] for d in data if d["departure_date"]==g]),sum([d["child"] for d in data if d["departure_date"]==g])),
				"is_total_row":1,
				"is_group":1,
			})
	report_data.append({
				"indent":0,
				"reservation": "",
				"is_separator":1})
	report_data.append({
				"indent":0,
				"reservation": "Grand Total",
				"room_nights":sum([d["room_nights"] for d in data ]),
				"total_pax":"{}/{}".format(sum([d["adult"] for d in data ]),sum([d["child"] for d in data])),
				"is_total_row":1,
				"is_group":1,
				"is_grand_total":1
			})
	return report_data