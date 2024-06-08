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
	
	report_data = get_report_data(data)
	# Summary = get_summary(filters,data)
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
		{'fieldname':'room_nights','label':'Nights',"width":75,"show_in_report":1,'align':'center',"fieldtype":"Int"},
		{'fieldname': 'total_pax', 'label': 'Pax(A/C)','align':'center',"width":65,"show_in_report":1},
		{'fieldname':'business_source','label':'Source','align':'left',"width":90,"show_in_report":1},
		{"fieldname":"guest", "label":"Guest", "fieldtype":"Link","options":"Customer","width":90,"show_in_report":0,"post_message_action": "view_guest_detail","url":"/frontdesk/guest-detail"},
		{"fieldname":"guest_name", "label":"Guest Name",'align':'left',"width":90,"show_in_report":1},
		{'fieldname':'reservation_status','label':'Status','align':'left',"width":95,"show_in_report":1},
		{'fieldname':'adr','label':'ADR','align':'right', 'fieldtype':'Currency',"show_in_report":1,"width":90},
		{'fieldname':'total_room_rate','label':'Total Room Rate','align':'right', 'fieldtype':'Currency',"show_in_report":1,"width":90},
		{'fieldname':'cancelled_by','label':'By','align':'left', 'fieldtype':'Data',"show_in_report":1,"width":90},
		{'fieldname':'cancelled_date','label':'Date', 'align':'right', 'fieldtype':'Date',"show_in_report":1,"width":90},
		{'fieldname':'cancelled_note','label':'Note', 'align':'left', 'fieldtype':'Data',"show_in_report":1,"width":90},
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
			adr,
   			is_reserved_room,
			if(is_reserved_room=1 and reservation_status='No Show' ,'No Show Reserved Room',reservation_status) as status
		from `tabReservation Stay` rst
			where
				1=1  
				{}
			
		""".format(get_filters(filters))

	 

	data =   frappe.db.sql(sql,filters,as_dict=1)
	return data

def get_filters(filters):
	sql = " and property=%(property)s and reservation_status in ('No Show','Void','Cancelled') "
	if filters.business_source:
		sql = sql + " and rst.business_source = %(business_source)s "
	
	if filters.reservation_type:
		sql = sql + " and rst.reservation_type = %(reservation_type)s"
	 
	if filters.filter_date_by =='Cancelled Date':
		sql = sql + " and rst.cancelled_date between %(start_date)s and %(end_date)s " 
	elif filters.filter_date_by =='Arrival Date':
		sql = sql + " and rst.arrival_date between %(start_date)s and %(end_date)s "  
	elif filters.filter_date_by =='Departure Date':
		sql = sql + " and rst.depareture_date between %(start_date)s and %(end_date)s " 
	else:
		stay_name_sql = "select  distinct reservation_stay from `tabReservation Room Rate` where is_active_reservation = 0 and date between %(start_date)s and %(end_date)s and property=%(property)s "
		if filters.reservation_type:
			stay_name_sql = stay_name_sql + " and reservation_type = %(reservation_type)s"
	
		if filters.business_source:
			stay_name_sql = stay_name_sql + " and business_source = %(reservation_type)s"
	
		stay_names = frappe.db.sql(stay_name_sql,filters,as_dict=1)
		
		filters.stay_names = set([d["reservation_stay"] for d in stay_names])
		
		sql = sql + " and rst.name in %(stay_names)s"
  
	sql = sql + " order by {} {}".format(
		[d for d in  get_order_field() if d["label"] == filters.order_by][0]["field"],
		filters.sort_order
	)
	
	return sql
 
def get_report_data(data):
 
	report_data = []
	reservation_status = ["No Show Reserved Room",'No Show','Cancelled','Void']
	for s in reservation_status:
		if [d for d in data if d["status"] == s]:
			report_data.append({
				"indent":0,
				"reservation": s,
				"is_group":1,
			})

			# render sub record
			sub_record = [d.update({"indent":1}) or d for d in data if d["status"]==s]
			report_data = report_data +  sub_record
			if len(sub_record)>1:
				report_data.append({
					"indent":0,
					"reservation": "Total",
					"reservation_type":len(sub_record),
					"room_nights":sum([d["room_nights"] for d in sub_record ]),
					"total_pax":"{}/{}".format(sum([d["adult"] for d in sub_record ]),sum([d["child"] for d in sub_record])),
					"total_room_rate":sum([d["total_room_rate"] for d in sub_record]),
					"is_total_row":1,
					"is_group":1,
				})

	report_data.append({})
	report_data.append({
					"indent":0,
					"reservation": "Grand Total",
					"reservation_type":len(data),
     				"is_total_row":1,
					"room_nights":sum([d["room_nights"] for d in data ]),
					"total_pax":"{}/{}".format(sum([d["adult"] for d in data ]),sum([d["child"] for d in data])),
					"total_room_rate":sum([d["total_room_rate"] for d in data]),
				})
	return report_data

	



	

