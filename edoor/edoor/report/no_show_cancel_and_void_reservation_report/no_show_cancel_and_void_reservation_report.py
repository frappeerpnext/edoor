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

	 

	tran_date = get_data(filters)
	reserved = get_no_show_reserved_room(filters)
	report_data = get_report_data(filters,tran_date,reserved)
	Summary = get_summary(filters,tran_date)
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
		{"fieldname":"reservation", "label":"Res #",'align':'left', "fieldtype":"Link","options":"Reservation","width":130,"show_in_report":1,"post_message_action": "view_reservation_detail","url":"/frontdesk/reservation-detail"},
		{"fieldname":"name", "label":"Stay #",'align':'left', "fieldtype":"Link","options":"Reservation Stay","width":115,"show_in_report":1,"url":"/frontdesk/stay-detail","post_message_action": "view_reservation_stay_detail"},
		{'fieldname':'reservation_type','align':'center','label':'Type',"width":60 ,"show_in_report":1},
		{'fieldname':'rooms','label':'Room','align':'center',"width":40,"show_in_report":1},
		{'fieldname':'room_type_alias','align':'center','label':'Room Type',"width":50,"show_in_report":1},
		{"fieldname":"arrival_date", 'align':'center',"label":"Arrival", "fieldtype":"Date","width":95,"show_in_report":1},
		{"fieldname":"departure_date",'align':'center', "label":"Departure", "fieldtype":"Date","width":95,"show_in_report":1},
		{'fieldname':'room_nights','label':'Room Night',"width":40,"show_in_report":1,'align':'center',"fieldtype":"Int"},
		{'fieldname': 'total_pax', 'label': 'Pax(A/C)','align':'center',"width":40,"show_in_report":1},
		{'fieldname':'business_source','label':'Source','align':'left',"width":90,"show_in_report":1},
		{"fieldname":"guest", "label":"Guest", "fieldtype":"Link","options":"Customer","width":90,"show_in_report":0,"post_message_action": "view_guest_detail","url":"/frontdesk/guest-detail"},
		{"fieldname":"guest_name", "label":"Guest Name",'align':'left',"width":90,"show_in_report":1},
		{'fieldname':'reservation_status','label':'Status','align':'left',"width":95,"show_in_report":1},
		{'fieldname':'adr','label':'ADR','align':'right', 'fieldtype':'Currency',"show_in_report":1,"width":90},
		{'fieldname':'total_room_rate','label':'Total Room Rate','align':'right', 'fieldtype':'Currency',"show_in_report":1,"width":90},
		{'fieldname':'cancelled_by','label':'By','align':'right', 'fieldtype':'Data',"show_in_report":1,"width":90},
		{'fieldname':'cancelled_date','label':'Date', 'align':'right', 'fieldtype':'Date',"show_in_report":1,"width":90},
		{'fieldname':'cancelled_note','label':'Note', 'align':'right', 'fieldtype':'Data',"show_in_report":1,"width":90},
	]
	return columns


def get_summary(filters,data):
	get_count = {d['reservation'] for d in data}
	if filters.show_summary:
		return [
			{ "label":"Total Room","value":len(data),"indicator":"red"},
			{ "label":"Total Reservation","value":len(get_count),"indicator":"red"},
			{ "label":"Total Room Nights","value":sum([d["room_nights"] for d in data ]),"indicator":"blue"},
			{ "label":"Total Pax(A/C)","value":"{}/{}".format(sum([d["adult"] for d in data ]),sum([d["child"] for d in data]))},
		]


def get_filters(filters):
	sql = " and property=%(property)s and reservation_status in ('No Show','Cancelled','Void')"
	if filters.business_source:
		sql = sql + " and rst.business_source = %(business_source)s "
	
	if filters.reservation_type:
		sql = sql + " and rst.reservation_type = %(reservation_type)s"

	sql = sql + " order by {} {}".format(
		[d for d in  get_order_field() if d["label"] == filters.order_by][0]["field"],
		filters.sort_order
	)

	return sql

def get_order_field():
	return [
		{"label":"Created On","field":"rst.creation"},
		{"label":"Reservation","field":"rst.reservation"},
		{"label":"Reservation Stay","field":"rst.name"},
		{"label":"Arrival Date","field":"rst.arrival_date"},
		{"label":"Departure Date","field":"rst.departure_date"},
		{"label":"Room Type","field":"rst.room_type_alias"},
		{"label":"Business Source","field":"rst.business_source"},
		{"label":"Reservation Status","field":"rst.reservation_status"},
		{"label":"Last Update On","field":"rst.modified"},
		]

def get_data(filters):
	sql="""
			select 
            name,
            reservation,
            arrival_date,
            departure_date,
            room_nights,
            guest,
            guest_name,
            reservation_status,
            cancelled_note,
            business_source,
            room_nights,
            rooms,
			concat(adult,'/',child) as total_pax,
            room_type_alias,
            reservation_type,
            reference_number,
            cancelled_by,
            cancelled_date,
            total_room_rate,
            adult,
            child,
			is_reserved_room,
            adr
        from `tabReservation Stay` rst
			where
				1=1  
				{}
			
		""".format(get_filters(filters))

	

	data =   frappe.db.sql(sql,filters,as_dict=1)
	return data

def get_filters_data(filters):
	sql = " and property=%(property)s and reservation_status in ('No Show') and is_reserved_room = 1 and arrival_date <= %(start_date)s and departure_date > %(end_date)s "
	if filters.business_source:
		sql = sql + " and rst.business_source = %(business_source)s "
	
	if filters.reservation_type:
		sql = sql + " and rst.reservation_type = %(reservation_type)s"
	
	sql = sql + " order by {} {}".format(
		[d for d in  get_order_field() if d["label"] == filters.order_by][0]["field"],
		filters.sort_order
	)

	return sql

def get_no_show_reserved_room(filters):
	sql="""
			select 
            name,
            reservation,
            arrival_date,
            departure_date,
            room_nights,
            guest,
            guest_name,
            reservation_status,
            cancelled_note,
            business_source,
            room_nights,
            rooms,
			concat(adult,'/',child) as total_pax,
            room_type_alias,
            reservation_type,
            reference_number,
            cancelled_by,
            cancelled_date,
            total_room_rate,
            adult,
            child,
			is_reserved_room,
            adr
        from `tabReservation Stay` rst
			where
				1=1  
				{}
			
		""".format(get_filters_data(filters))

	

	data1 =   frappe.db.sql(sql,filters,as_dict=1)
	return data1

def get_report_data(filters,data,data1):
	start_date = datetime.strptime(filters.start_date, '%Y-%m-%d').date()
	end_date = datetime.strptime(filters.end_date, '%Y-%m-%d').date()
	report_data = []
	tran_date = sorted(set([d['reservation_status'] for d in data if 'cancelled_date' in d and d['cancelled_date'] >= start_date and d['cancelled_date'] <= end_date]))
	if tran_date:
		report_data.append({
			"indent":0,
			"reservation":"Today No Show, Cancel & Void",
			"is_group":1
		})
		for g in tran_date:
			d = g
			report_data.append({
				"indent":1,
				"reservation": d,
				"is_group":1,
			})
			report_data = report_data +  [d.update({"indent":1}) or d for d in data if d["reservation_status"]==g]
			report_data.append({
				"indent":1,
				"reservation": "Total",
				"room_nights":sum([d["room_nights"] for d in data if d["reservation_status"]==g]),
				"total_pax":"{}/{}".format(sum([d["adult"] for d in data if d["reservation_status"]==g]),sum([d["child"] for d in data if d["reservation_status"]==g])),
				"adr":sum([d["adr"] for d in data if d["reservation_status"]==g]),
				"is_total_row":1,
				"is_group":1,
			})
	arrival = sorted(set([d['reservation_status'] for d in data if d['arrival_date'] >= start_date and d['arrival_date'] <= end_date]))
	if arrival:
		report_data.append({
			"indent":0,
			"reservation":"No Show, Cancel & Void",
			"is_group":1
		})
		for g in arrival:
			d = g
			report_data.append({
				"indent":1,
				"reservation": d,
				"is_group":1,
			})
			report_data = report_data +  [d.update({"indent":1}) or d for d in data if d["reservation_status"]==g]
			report_data.append({
				"indent":1,
				"reservation": "Total",
				"room_nights":sum([d["room_nights"] for d in data if d["reservation_status"]==g]),
				"total_pax":"{}/{}".format(sum([d["adult"] for d in data if d["reservation_status"]==g]),sum([d["child"] for d in data if d["reservation_status"]==g])),
				"adr":sum([d["adr"] for d in data if d["reservation_status"]==g]),
				"is_total_row":1,
				"is_group":1,
			})
	reserved_room = sorted(set([d['reservation_status'] for d in data1]))
	if reserved_room:
		report_data.append({
			"indent":0,
			"reservation":"No Show(Reserved)",
			"is_group":1
		})
		for g in reserved_room:
			d = g
			report_data.append({
				"indent":1,
				"reservation": d,
				"is_group":1,
			})
			report_data = report_data +  [d.update({"indent":1}) or d for d in data1 if d["reservation_status"]==g]
			report_data.append({
				"indent":1,
				"reservation": "Total",
				"room_nights":sum([d["room_nights"] for d in data1 if d["reservation_status"]==g]),
				"total_pax":"{}/{}".format(sum([d["adult"] for d in data1 if d["reservation_status"]==g]),sum([d["child"] for d in data1 if d["reservation_status"]==g])),
				"adr":sum([d["adr"] for d in data1 if d["reservation_status"]==g]),
				"is_total_row":1,
				"is_group":1,
			})
	return report_data

	



	

