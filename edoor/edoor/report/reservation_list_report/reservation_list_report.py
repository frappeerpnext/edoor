import frappe
from frappe import _
from frappe.utils import date_diff,today ,add_months, add_days
from frappe.utils.data import strip
import datetime
import uuid
def execute(filters=None): 
	data = get_report_data(filters)
	return get_columns(filters),data

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
		{"fieldname":"reservation_date",'align':'left', "label":"Res. Date", "fieldtype":"Date","width":95,"show_in_report":1},
		{'fieldname':'rooms','label':'Room','align':'center',"width":40,"show_in_report":1},
		{'fieldname':'room_type_alias','align':'center','label':'Room Type',"width":50,"show_in_report":1},
		{"fieldname":"arrival_date", 'align':'left',"label":"Arrival", "fieldtype":"Date","width":95,"show_in_report":1},
		{"fieldname":"departure_date",'align':'left', "label":"Departure", "fieldtype":"Date","width":95,"show_in_report":1},
		{'fieldname':'room_nights','label':'Room Night',"width":40,"show_in_report":1,'align':'center'},
		{'fieldname': 'pax', 'label': 'Pax(A/C)','align':'center',"width":40,"show_in_report":1},
		{'fieldname':'business_source','label':'Source','align':'left',"width":90,"show_in_report":1},
		{"fieldname":"guest", "label":"Guest", "fieldtype":"Link","options":"Customer","width":90,"show_in_report":0,"post_message_action": "view_guest_detail","url":"/frontdesk/guest-detail"},
		{"fieldname":"guest_name", "label":"Guest Name",'align':'left',"width":90,"show_in_report":1},
		{'fieldname':'reservation_status','label':'Status','align':'center',"width":95,"show_in_report":1},
		{'fieldname':'total_debit','label':'Debit','align':'right', 'fieldtype':'Currency',"show_in_report":1,"width":90},
		{'fieldname':'total_credit','label':'Credit', 'align':'right', 'fieldtype':'Currency',"show_in_report":1,"width":90},
		{'fieldname':'balance','label':'Balance', 'align':'right', 'fieldtype':'Currency',"show_in_report":1,"width":90},
		# {"fieldname":"creation", "label":"Creation", "fieldtype":"Date","width":95},
		# {"fieldname":"modified", "label":"Modified", "fieldtype":"Datetime","width":95},
	]
	return columns

def get_filters(filters):
	sql = " and property=%(property)s "

	if filters.filter_date_by =="Arrival Date":
		sql = sql +  " and rst.arrival_date between %(start_date)s and %(end_date)s "
	elif filters.filter_date_by == "Stay Date":
		filters.reservation_stays = get_reservation_stays(filters)
		sql = sql + " and rst.name in %(reservation_stays)s"
	elif filters.filter_date_by == "Reservation":
		filters.reservations = get_reservation(filters)
		sql = sql + " and rst.reservation in %(reservations)s"
	elif filters.filter_date_by == "Departure Date":
		sql = sql +  " and rst.departure_date between %(start_date)s and %(end_date)s "

	if filters.reservation:
		sql = sql +  " and rst.reservation  =  %(reservation)s"
	if filters.business_source:
		sql = sql + " and rst.business_source = %(business_source)s"
	if filters.guest:
		sql = sql + " and rst.guest = %(guest)s"

	if filters.get("reservation_status"):
		sql = sql + " and rst.reservation_status in %(reservation_status)s"
	
	if filters.reservation_type:
		sql = sql + " and rst.reservation_type = %(reservation_type)s"
	# elif filters.reservation_type == "GIT":
	# 	sql = sql + " and rst.reservation_type in %(reservation_type)s"

	if filters.is_active_reservation:
		sql = sql + " and rst.is_active_reservation = %(is_active_reservation)s"

	if filters.order_by == "Last Update On" and filters.sort_order == "ASC":
		sql = sql + " order by rst.modified asc"
	elif filters.order_by == "Last Update On" and filters.sort_order == "DESC":
		sql = sql + " order by rst.modified desc"

	elif filters.order_by == "Created On" and filters.sort_order == "ASC":
		sql = sql + " order by rst.creation asc"
	elif filters.order_by == "Created On" and filters.sort_order == "DESC":
		sql = sql + " order by rst.creation desc"

	elif filters.order_by == "Reservation" and filters.sort_order == "ASC":
		sql = sql + " order by rst.reservation asc"
	elif filters.order_by == "Reservation" and filters.sort_order == "DESC":
		sql = sql + " order by rst.reservation desc"

	elif filters.order_by == "Reservation Stay" and filters.sort_order == "ASC":
		sql = sql + " order by rst.name asc"
	elif filters.order_by == "Reservation Stay" and filters.sort_order == "DESC":
		sql = sql + " order by rst.name desc"

	elif filters.order_by == "Arrival Date" and filters.sort_order == "ASC":
		sql = sql + " order by rst.arrival_date asc"
	elif filters.order_by == "Arrival Date" and filters.sort_order == "DESC":
		sql = sql + " order by rst.arrival_date desc"

	elif filters.order_by == "Departure Date" and filters.sort_order == "ASC":
		sql = sql + " order by rst.departure_date asc"
	elif filters.order_by == "Departure Date" and filters.sort_order == "DESC":
		sql = sql + " order by rst.departure_date desc"

	elif filters.order_by == "Room Type" and filters.sort_order == "ASC":
		sql = sql + " order by rst.room_type_alias asc"
	elif filters.order_by == "Room Type" and filters.sort_order == "DESC":
		sql = sql + " order by rst.room_type_alias desc"
	
	elif filters.order_by == "Reservation Status" and filters.sort_order == "ASC":
		sql = sql + " order by rst.reservation_status asc"
	elif filters.order_by == "Reservation Status" and filters.sort_order == "DESC":
		sql = sql + " order by rst.reservation_status desc"
		

	return sql

def get_reservation_stays(filters):
	sql = """
		select 
			distinct reservation_stay 
		from `tabRoom Occupy` 
		where 
			date  between %(start_date)s and %(end_date)s 
	"""
	if filters.reservation:
		sql = sql +  " and rst.reservation  =  %(reservation)s"
	if filters.business_source:
		sql = sql + " and rst.business_source = %(business_source)s"
	if filters.guest:
		sql = sql + " and rst.guest = %(guest)s"
	if filters.get("reservation_status"):
		sql = sql + " and rst.reservation_status in %(reservation_status)s"


	data =  frappe.db.sql(sql, filters, as_dict=1)
	return [d["reservation_stay"] for d in data]

def get_reservation(filters):
	sql = """
		select 
			distinct reservation
		from `tabRoom Occupy` 
		where 
			date  between %(start_date)s and %(end_date)s
	"""
	if filters.reservation:
		sql = sql +  " and rst.reservation  =  %(reservation)s"
	if filters.business_source:
		sql = sql + " and rst.business_source = %(business_source)s"
	if filters.guest:
		sql = sql + " and rst.guest = %(guest)s"
	if filters.get("reservation_status"):
		sql = sql + " and rst.reservation_status in %(reservation_status)s"
	

		
	data =  frappe.db.sql(sql, filters, as_dict=1)
	return [d["reservation"] for d in data]


def get_report_data(filters):
	sql="""
		select 
			name,
			reservation_date,
			arrival_date,
			departure_date,
			rooms,
			modified,
			creation,
			reservation_type,
			reservation,
			room_type_alias,
			room_types,
			nationality,
			business_source,
			adult,
			child,
			concat(adult,'/',child) as pax,
			room_nights,
			business_source_type,
			rate_type,
			guest,
			guest_name,
			is_active_reservation,
			reservation_status,
			total_debit,
			total_credit,
			balance
		from `tabReservation Stay` rst
		where
			1=1  
			{}
		
	""".format(get_filters(filters))

	

	data =   frappe.db.sql(sql,filters,as_dict=1)

	if filters.group_by:
		group_column = get_group_by_column(filters)
		group_data = sorted(set([d[group_column["data_field"]] for d  in data]))
		report_data = []
		for g in group_data:
			d = g
			if group_column["fieldtype"]=="Date":
				d  = frappe.format(g,{"fieldtype":"Date"})
			id =  str(uuid.uuid4())
			report_data.append({
				"indent":0,
				"reservation": d,
				"is_group":1,
				"id":id
			})
			report_data = report_data +  [d.update({"indent":1,"parent":id}) or d for d in data if d[group_column["data_field"]]==g]
			
			report_data.append({
				"indent":0,
				"reservation": "Total",
				"room_nights":sum([d["room_nights"] for d in data if d[group_column["data_field"]]==g]),
				"pax":"{}/{}".format(sum([d["adult"] for d in data if d[group_column["data_field"]]==g]),sum([d["child"] for d in data if d[group_column["data_field"]]==g])),
				"total_debit":sum([d["total_debit"] for d in data if d[group_column["data_field"]]==g]),
				"total_credit":sum([d["total_credit"] for d in data if d[group_column["data_field"]]==g]),
				"balance":sum([d["balance"] for d in data if d[group_column["data_field"]]==g]),
				"is_total_row":1,
				"is_group":0,
				"parent":id
			})

		report_data.append({
				"indent":0,
				"reservation": "",
				"is_separator":1})
		report_data.append({
				"indent":0,
				"reservation": "Grand Total",
				"room_nights":sum([d["room_nights"] for d in data ]),
				"pax":"{}/{}".format(sum([d["adult"] for d in data ]),sum([d["child"] for d in data])),
				"total_debit":sum([d["total_debit"] for d in data]),
				"total_credit":sum([d["total_credit"] for d in data]),
				"balance":sum([d["balance"] for d in data ]),
				"is_total_row":1,
				"is_group":0,
				"is_grand_total":1
			})

		return report_data
	else:
		data.append({
			"indent":0,
			"reservation": "Total",
			"total_debit":sum([d["total_debit"] for d in data]),
			"total_credit":sum([d["total_credit"] for d in data]),
			"balance":sum([d["balance"] for d in data ]),
			"room_nights":sum([d["room_nights"] for d in data ]),
			"pax":"{}/{}".format(sum([d["adult"] for d in data ]),sum([d["child"] for d in data])),
			"is_total_row":1
		})
		return data

def get_group_by_column(filters):
 
	return  [d for d in group_by_columns() if d["label"] == filters.group_by][0]

def group_by_columns():
	
	return [
		{"fieldname":"group_by","data_field":"arrival_date", "label":"Arrival Date","fieldtype":"Date"},
		{"fieldname":"group_by","data_field":"departure_date", "label":"Departure Date" ,"fieldtype":"Date" },
		{"fieldname":"group_by","data_field":"reservation", "label":"Reservation" ,"fieldtype":"Data" },
		{"fieldname":"group_by","data_field":"reservation_date", "label":"Reservation Date" ,"fieldtype":"Date" },
		{"fieldname":"group_by","data_field":"guest", "label":"Guest" ,"fieldtype":"Data" },
		{"fieldname":"group_by","data_field":"reservation_type", "label":"Reservation Type" ,"fieldtype":"Data" },
		{"fieldname":"group_by","data_field":"nationality", "label":"Nationality" ,"fieldtype":"Data" },
		{"fieldname":"group_by","data_field":"business_source", "label":"Business Source" ,"fieldtype":"Data" },
		{"fieldname":"group_by","data_field":"business_source_type", "label":"Business Source Type" ,"fieldtype":"Data" },
		{"fieldname":"group_by","data_field":"room_types", "label":"Room Type" ,"fieldtype":"Data" },
		{"fieldname":"group_by","data_field":"rate_type", "label":"Rate Type" ,"fieldtype":"Data" },
		{"fieldname":"group_by","data_field":"reservation_status", "label":"Reservation Status" ,"fieldtype":"Data" },
	]