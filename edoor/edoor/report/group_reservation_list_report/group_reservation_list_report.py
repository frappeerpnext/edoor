# Copyright (c) 2024, Tes Pheakdey and contributors
# For license information, please see license.txt

# import frappe


import frappe
from frappe import _
from frappe.utils import date_diff,today ,add_months, add_days
from frappe.utils.data import strip
import datetime
import uuid
def execute(filters=None): 

	if filters.summary_filter:
		if not filters.summary_fields:
			filters.summary_fields = ['total_record', 'room_night']

	 
	report_data = get_report_data(filters)
	summary = get_summary(filters,report_data)
	chart = get_chart(filters,report_data)
	
	return get_columns(filters),report_data,None,chart, summary

def validate(filters):
	datediff = date_diff(filters.end_date, filters.start_date)
	if filters.start_date and filters.end_date:
		if filters.start_date > filters.end_date:
			frappe.throw("The 'Start Date' ({}) must be before the 'End Date' ({})".format(filters.start_date, filters.end_date))
		if datediff > 30:
			frappe.throw("Your Max date for viewing transaction is only One Month.".format(filters.start_date, filters.end_date))

def get_columns(filters):
	columns =   [
		{"fieldname":"name", "label":"Res #",'align':'left', "fieldtype":"Link","options":"Reservation","width":130,"show_in_report":1,"post_message_action": "view_reservation_detail","url":"/frontdesk/reservation-detail"},
		{"fieldname":"reference_number", "label":"Ref #",'align':'left',"width":115,"show_in_report":1,"url":"/frontdesk/stay-detail","post_message_action": "view_reservation_stay_detail"},
		{'fieldname':'reservation_type','align':'center','label':'Type',"width":60 ,"show_in_report":1},
		{"fieldname":"reservation_date",'align':'center', "label":"Res. Date", "fieldtype":"Date","width":95,"show_in_report":1},
		{'fieldname':'room_numbers','label':'Room','align':'center',"width":40,"show_in_report":1},
		{'fieldname':'room_type_alias','align':'center','label':'Room Type',"width":50,"show_in_report":1},
		{"fieldname":"arrival_date", 'align':'center',"label":"Arrival", "fieldtype":"Date","width":95,"show_in_report":1},
		{"fieldname":"departure_date",'align':'center', "label":"Departure", "fieldtype":"Date","width":95,"show_in_report":1},
		{'fieldname':'room_nights','label':'Room Night',"width":40,"show_in_report":1,'align':'center',"fieldtype":"Int"},
		{'fieldname': 'total_pax', 'label': 'Pax(A/C)','align':'center',"width":40,"show_in_report":1},
		{'fieldname':'business_source','label':'Source','align':'left',"width":90,"show_in_report":1},
		{"fieldname":"guest", "label":"Guest", "fieldtype":"Link","options":"Customer","width":90,"show_in_report":0,"post_message_action": "view_guest_detail","url":"/frontdesk/guest-detail"},
		{"fieldname":"guest_name", "label":"Guest Name",'align':'left',"width":90,"show_in_report":1},
		{"fieldname":"guest_type", "label":"Guest Type",'align':'left',"width":90,"show_in_report":1},
		{"fieldname":"total_active_reservation_stay", "label":"Total Stay",'align':'center',"width":90,"show_in_report":1},
		{"fieldname":"rate_type", "label":"Rate Type",'align':'left',"width":90,"show_in_report":1},
		{'fieldname':'adr','label':'ADR','align':'right', 'fieldtype':'Currency',"show_in_report":1,"width":90},
		{'fieldname':'total_amount','label':'Total Room Rate','align':'right', 'fieldtype':'Currency',"show_in_report":1,"width":90},
		{'fieldname':'total_debit','label':'Debit','align':'right', 'fieldtype':'Currency',"show_in_report":1,"width":90},
		{'fieldname':'total_credit','label':'Credit', 'align':'right', 'fieldtype':'Currency',"show_in_report":1,"width":90},
		{'fieldname':'balance','label':'Balance', 'align':'right', 'fieldtype':'Currency',"show_in_report":1,"width":90},
		{'fieldname':'owner','label':'Created By','align':'left',"width":90,"show_in_report":1},
		{'fieldname':'creation','label':'Creation','align':'left',"width":90,"show_in_report":1,'fieldtype':'Date'},
		{'fieldname':'reservation_status','label':'Status','align':'left',"width":95,"show_in_report":1},
		
	]
	return columns


def get_summary(filters,data):
	if filters.show_summary:
		return [
			{ "label":"Total Reservation","value":len(data),"indicator":"red"},
			{ "label":"Total Stay","value":sum([d["total_active_reservation_stay"] for d in data ]),"indicator":"blue"},
			{ "label":"Total Room Nights","value":sum([d["room_nights"] for d in data ]),"indicator":"blue"},
			{ "label":"Total Pax(A/C)","value":"{}/{}".format(sum([d["adult"] for d in data ]),sum([d["child"] for d in data]))},
			{ "label":"Total Debit","value": sum([d["total_debit"] for d in data ]),"datatype": "Currency","indicator":"red"},
			{ "label":"Total Credit","value":sum([d["total_credit"] for d in data ]),"datatype": "Currency","indicator":"green"},
			{ "label":"Total Balance","value":sum([d["balance"] for d in data ]),"datatype": "Currency","indicator":"blue"},
		]

def get_chart(filters,data):
	currency_precision = frappe.db.get_single_value("System Settings","currency_precision")
	 
	chart_series = filters.get("chart_series")
	if filters.chart_type=="None" or not chart_series or not  filters.view_chart_by:
		return None

	dataset = []
	colors = []

	report_fields = get_chart_series()
 
	

	group_column = get_field(filters)
	

	group_data = sorted(set([d[group_column["data_field"]] for d  in data]))
	
	for d in chart_series:
		field = [x for x in report_fields if x["label"] == d][0]
		

		dataset_values = []
		for g in group_data: 
			amount = sum([d[field["data_field"]] for d in data if d[group_column["data_field"]] == g])
			
			if field["fieldtype"]  =="Currency":
				amount = round(amount,int(currency_precision))


			dataset_values.append(
				amount
			)



		dataset.append({'name':field["label"],'values':dataset_values})
		colors.append(field["chart_color"])

 
	chart = {
		'data':{
			'labels': [frappe.format(d,{"fieldtype":group_column["fieldtype"]}) for d in  group_data] ,
			'datasets':dataset
		},
		"type": filters.chart_type,
		# "lineOptions": {
		# 	"regionFill": 1,
		# },
		'valuesOverPoints':1,
		"axisOptions": {"xIsSeries": 1},
		
	}
	return chart

def get_filters(filters):
	sql = " and property=%(property)s and reservation_date between %(start_date)s and %(end_date)s "

	if filters.reservation:
		sql = sql +  " and rst.name  =  %(reservation)s"
	if filters.business_source:
		sql = sql + " and rst.business_source = %(business_source)s"
	if filters.guest:
		sql = sql + " and rst.guest = %(guest)s"

	if filters.get("reservation_status"):
		sql = sql + " and rst.reservation_status in %(reservation_status)s"

	# if filters.get("room_types"):
	# 	sql = sql + " and rst.room_types in %(room_types)s"
		

	
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
		{"label":"Reservation","field":"rst.name"},
		{"label":"Reservation Date","field":"rst.reservation_date"},
		{"label":"Arrival Date","field":"rst.arrival_date"},
		{"label":"Departure Date","field":"rst.departure_date"},
		{"label":"Room Type","field":"rst.room_type_alias"},
		{"label":"Business Source","field":"rst.business_source"},
		{"label":"Reservation Status","field":"rst.reservation_status"},
		{"label":"Last Update On","field":"rst.modified"},
		]

def get_report_data(filters):
	sql="""
			select 
				name,
				reference_number,
				reservation_date,
				arrival_date,
				departure_date,
				room_numbers,
				modified,
				creation,
				reservation_type,
				room_type_alias,
				room_types,
				owner,
				total_active_reservation_stay,
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
				email_address,
				guest_type,
				rate_type,
				creation,
				reservation_status,
				adr,
				total_amount as total_room_rate,
				total_debit,
				total_credit,
				balance,
				1 as is_data,
				1 as total_record
			from `tabReservation` rst
			where
				1=1  
				{}
			
		""".format(get_filters(filters))

	

	data =   frappe.db.sql(sql,filters,as_dict=1)
	return data

# def get_report_data(filters,data):

		
# 		return data


def get_field(filters):
 
	return  [d for d in get_report_field() if d["label"] == filters.view_chart_by][0]

def get_report_field():
	return [
		{"data_field":"arrival_date", "label":"Arrival Date","fieldtype":"Date"},
		{"data_field":"departure_date", "label":"Departure Date" ,"fieldtype":"Date" },
		{"data_field":"name", "label":"Reservation" ,"fieldtype":"Data" },
		
		{"data_field":"reservation_date", "label":"Reservation Date" ,"fieldtype":"Date" },
		{"data_field":"guest_name", "label":"Guest" ,"fieldtype":"Data" },
		{"data_field":"reservation_type", "label":"Reservation Type" ,"fieldtype":"Data" },
		{"data_field":"business_source", "label":"Business Source" ,"fieldtype":"Data" },
		{"data_field":"business_source_type", "label":"Business Source Type" ,"fieldtype":"Data" },
		{"data_field":"room_types", "label":"Room Type" ,"fieldtype":"Data" },
		{"data_field":"rate_type", "label":"Rate Type" ,"fieldtype":"Data" },
		{"data_field":"reservation_status", "label":"Reservation Status" ,"fieldtype":"Data" },
	]

	

def get_chart_series():
	return [
		{"data_field":"total_debit","label":"Total Debit","short_label":"Debit", "fieldtype":"Currency", "align":"center","chart_color":"#dc9819"},
		{"data_field":"total_credit","label":"Total Credit", "short_label":"Credit", "fieldtype":"Currency", "align":"right","chart_color":"#1987dc"},
		{"data_field":"balance","label":"Balance", "short_label":"Balance", "fieldtype":"Currency", "align":"right","chart_color":"#fd4e8a"},
		{"data_field":"adult","label":"Adult", "short_label":"Adult", "fieldtype":"Integer", "align":"right","chart_color":"#d7e528"},
		{"data_field":"child","label":"Child", "short_label":"Child", "fieldtype":"Integer", "align":"right","chart_color":"#df7b5c"},
		{"data_field":"pax","label":"Pax", "short_label":"Pax", "fieldtype":"Integer", "align":"right","chart_color":"#df7b5c"},
		{"data_field":"room_nights","label":"Room Nights", "short_label":"Room Nights", "fieldtype":"Integer", "align":"right","chart_color":"#3ce18e"}
	]