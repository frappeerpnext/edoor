# Copyright (c) 2023, Tes Pheakdey and contributors
# For license information, please see license.txt
from datetime import datetime
from frappe.utils.data import getdate
import frappe
from frappe import _

def execute(filters=None):
	if not filters.property:
		property = frappe.defaults.get_user_default("business_branch")
		if not property:
			data = frappe.db.get_list("Business Branch")
			if len(data)>0:
				property = data[0].name
		filters.property = property
	if not filters.start_date:
		filters.start_date =  getdate(datetime(datetime.now().year, 1, 1))
	if not filters.end_date:
		filters.end_date =  getdate(datetime(datetime.now().year, 12, 31))

 
	if filters.chart_type =='pie' or filters.chart_type=="donut":
		if len(filters.chart_series or [])!=1:
			filters.chart_series = ["occupancy"]
		
				
	data = get_report_data(filters)
	return get_columns(filters), data, None, get_report_chart(filters,data)


def get_columns(filters):
	return [
		{"fieldname": "month", "label":"Month","width":150},
		{"fieldname": "room_available", "label":"Total Room","fieldtype":"Int","align":"center"},
		{"fieldname": "occupy", "label":"occupy","fieldtype":"Int","align":"center"},
		{"fieldname": "house_use", "label":"House Use","fieldtype":"Int","align":"center"},
		{"fieldname": "complimentary", "label":"Complimentary","fieldtype":"Int","align":"center"},
		{"fieldname": "block", "label":"OOO","fieldtype":"Int","align":"center"},
		{"fieldname": "occupancy", "label":"Occupancy(%)", "fieldtype":"Percent","align":"center"},
		{"fieldname": "pax", "label":"Pax", "fieldtype":"Int","align":"center"},
	]

def get_report_data(filters):
	calculate_room_occupancy_include_room_block = frappe.db.get_single_value("eDoor Setting", "calculate_room_occupancy_include_room_block")

	report_data = get_room_available(filters)

	occupy_data = get_occupy_data(filters)
	for r in report_data:
		occupies = [d for d  in occupy_data if d["month"] == r["month"]]
		
		if len(occupies)>0:
			occupy = occupies [0]
			r["occupy"] = occupy["occupy"]
			r["house_use"] = occupy["house_use"]
			r["complimentary"] = occupy["complimentary"]
			r["block"] = occupy["block"]
			r["pax"] = occupy["pax"]

			# occupancy
			total_room = 1 if (r["room_available"] or 0) == 0 else r["room_available"]
			if calculate_room_occupancy_include_room_block==0:
				total_room = total_room - r["block"]
				if total_room == 0:
					total_room = 1

			r["occupancy"] = r["occupy"] / total_room
		else:
			r["occupy"] = 0
			r["house_use"] =0
			r["complimentary"] = 0
			r["block"] = 0
			r["pax"] = 0
			r["occupancy"] = 0
		
	 
	return report_data


def get_room_available(filters):
	sql = "select date_format(date,'%%b-%%Y') as month, sum(total_room) as room_available  from `tabDaily Property Data` where property = %(property)s and date between %(start_date)s and %(end_date)s group by date_format(date,'%%b-%%Y') order by year(date), month(date) "
 
	return frappe.db.sql(sql,filters,as_dict=1)

def get_occupy_data(filters):
	sql = """select 
				date_format(date,'%%b-%%Y') as month, 
				sum(type='Reservation' and is_active=1 and is_complimentary = 0 and is_house_use=0) as occupy,
				sum(type='Block') as block,
				sum(is_house_use=1) as house_use,
				sum(is_complimentary=1) as complimentary,
				sum(adult+child) as pax
			from `tabRoom Occupy` 
			where 
				property = %(property)s and 
				date between %(start_date)s and %(end_date)s and
				is_active_reservation = 1 
			group by date_format(date,'%%b-%%Y')  
				
	"""

	
	return frappe.db.sql(sql,filters,as_dict=1)


def get_report_chart(filters, data):
	if filters.chart_type == "None":
		return None

	report_columns = get_columns(filters)
	chart_series = filters.chart_series
	if not chart_series:
		chart_series = ["occupy","house_use","complimentary","block","occupancy","pax"]
	
	datasets = []
	for c in report_columns:
		if  c["fieldname"] in chart_series:	
 
			if c["label"] =="Occupancy(%)":
				datasets.append({
							"name": c["label"],
							"values": [round(d[c["fieldname"]] * 100,2) for d in data]
				})

			else:

				datasets.append({
							"name": c["label"],
							"values": [d[c["fieldname"]] for d in data]
				})
				
	chart = {
		'data':{
			'labels':[d["month"] for d in data],
			'datasets':datasets
		},
		"type": filters.chart_type,
		"lineOptions": {
			"regionFill": 1,
		},
		'valuesOverPoints':1,
		"axisOptions": {"xIsSeries": 1}
	}
	return chart