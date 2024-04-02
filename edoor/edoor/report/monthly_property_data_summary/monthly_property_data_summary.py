# Copyright (c) 2023, Tes Pheakdey and contributors
# For license information, please see license.txt
from frappe.utils import getdate, add_to_date
import frappe
from edoor.edoor.report.monthly_property_data_summary import report_summary_by_occupy
from edoor.edoor.report.utils import get_months

def execute(filters=None):
	if getdate(filters.start_date) > getdate(filters.end_date):
		frappe.throw("Start date cannot less than end date")

	min_max_day = get_min_max_day(filters)
	columns = get_report_columns(filters,min_max_day)
 
	report_data = {}
	if filters.column_group=="Occupy":
		report_data = report_summary_by_occupy.get_report(filters,columns)
	else:
		frappe.throw("This option is comming soon")
	message = ""
	if filters.row_group == "Room":
		message = "Note: Unassigned rooms in your reservation may affect the accuracy of the occupancy calculation."
	
	return columns, report_data["data"],message

def get_report_columns(filters,min_max_day):
	columns = [
		{"fieldname": "row_group", "label":filters.row_group, "width": 200},
	]

	for n in range(min_max_day["min_day"], min_max_day["max_day"]+1):
		columns.append({
			"fieldname":"col_" + str(n),"label": "{}".format(n), "width":50, "align":"center", "has_total":True
	})
  
	columns.append({
		"fieldname":"occupancy","label": "Occ", "width":100, "align":"center","fieldtype":"Percent"
	})
 
	columns.append({
		"fieldname":"total","label": "Total", "width":100, "align":"center","has_total":True
	})
	
		
	return columns

def get_report_data(filters,min_max_day):
	report_data = []
	
	room_types = get_room_types(filters)
	daily_property_data = get_daily_property_data(filters)
 
	room_occupy = get_room_occupy(filters)
	months = get_months(filters)

	calculate_room_occupancy_include_room_block = frappe.db.get_single_value("eDoor Setting", "calculate_room_occupancy_include_room_block")

	for m in months:
		month_record = {
			"row_group": m["str_month"],
			"indent":0,
			"is_group":1
		}
		report_data.append(month_record)
		room_inventory_records = []
		for rt in room_types:
			room_type_record = {
				"row_group": "{} ({})".format( rt["room_type"] , rt["total_room"]),
				"indent": 1,
				"total":0,
				
			}
			date = m["min_date"] 
			
			while date <= m["max_date"]: 
				total_occupy = get_total_room_occupy_by_day( date,rt.name, daily_property_data,room_occupy)
				room_type_record["col_" + str(date.day)] = total_occupy
				
	
				date = add_to_date(date, days=1)
			
			room_inventory_records.append(room_type_record)

		report_data = report_data + room_inventory_records


		date = m["min_date"]
	 
 

		

 
	
	return {
		"data":report_data, 
		"report_summary":get_report_summary(filters, room_occupy,daily_property_data),
		"report_chart":[]
	}

 
def get_room_occupy(filters):
	sql = """select 
				date, 
				room_type_id,
				sum(type='Reservation') as occupy, 
				sum(type='Reservation' and is_arrival=1) as arrival, 
				sum(type='Reservation' and is_arrival=0 and is_departure=0) as stay_over, 
				sum(type='Reservation' and is_departure=1) as departure, 
				sum(adult) as adult, 
				sum(child) as child, 
				sum(type='Block') as block 
			from `tabRoom Occupy` 
			where 
				property=%(property)s and 
				date between %(start_date)s and %(end_date)s and 
				is_active=1 
			group by 
				date,
				room_type_id"""

	return frappe.db.sql(sql,filters, as_dict=1)


def get_total_room_occupy_by_day(date,room_type_id, daily_property_data, occupy_data):
	total_rooms = sum(d["total_room"] for d in daily_property_data if d["date"]==date and d["room_type_id"]==room_type_id)
	occupy =sum(d["occupy"] for d in occupy_data if d["date"]==date and d["room_type_id"]==room_type_id)
	block =sum(d["block"] for d in occupy_data if d["date"]==date and d["room_type_id"]==room_type_id)
	return total_rooms -( (occupy or 0) + (block or 0))

def get_room_types(filters):
	sql = "select rt.name,  rt.room_type, count(r.name) as total_room from `tabRoom Type` rt inner join `tabRoom` r on r.room_type_id=rt.name and r.disabled=0 where r.property=%(property)s group by rt.name, rt.room_type  order by rt.sort_order "
	return frappe.db.sql(sql, filters, as_dict = 1)

def get_daily_property_data(filters):
	sql = "select date, room_type_id, total_room from `tabDaily Property Data` where date between %(start_date)s and %(end_date)s and property = %(property)s"
	return frappe.db.sql(sql,filters,as_dict=1)

def get_min_max_day(filters):
	sql = "select min(day(date)) as min_day, max(day(date)) as max_day from `tabDates` where date between %(start_date)s and %(end_date)s"
	data = frappe.db.sql(sql,filters,as_dict=1)
	return data [0]


def get_report_summary(filters, occupay_data, daily_property_data):
	if not filters.show_summary:
		return None
	summary = []
	
	total_rooms = sum([d["total_room"] for d in  daily_property_data])
 
	if not filters.show_summary_fields or  "total_room" in filters.show_summary_fields :
		summary.append({
			"label": "Total Rooms",
			"value": total_rooms,
		})
		
	occupy = sum([d["occupy"] for d in  occupay_data])
	if not filters.show_summary_fields or  "occupy" in filters.show_summary_fields:
		summary.append({
			"label": "Occupy",
			"value": occupy,
			"indicator":"green"
		})
	
	block = sum([d["block"] for d in  occupay_data])
	if not filters.show_summary_fields or  "ooo" in filters.show_summary_fields:
		summary.append({
			"label": "OOO",
			"value": block,
			"indicator":"red"
		})
	if not filters.show_summary_fields or  "vacant" in filters.show_summary_fields:
		summary.append({
			"label": "Vacant",
			"value": (total_rooms or 0) - (occupy + block)
		})

	if not filters.show_summary_fields or  "occupancy" in filters.show_summary_fields:
		calculate_room_occupancy_include_room_block = frappe.db.get_single_value("eDoor Setting", "calculate_room_occupancy_include_room_block")
		if calculate_room_occupancy_include_room_block  == 0:
			total_rooms = total_rooms - block

		summary.append({
			"label": "Occupancy",
			"value":  occupy / total_rooms * 100,
			"datatype":"Percent" ,
			"indicator":"green"
		})
	if not filters.show_summary_fields or  "arrival" in filters.show_summary_fields:
		summary.append({
			"label": "Arrival",
			"value": sum([d["arrival"] for d in  occupay_data]),
			"indicator":"blue"
		})
	if not filters.show_summary_fields or  "stay_over" in filters.show_summary_fields:
		summary.append({
			"label": "Stay Over",
			"value": sum([d["stay_over"] for d in  occupay_data]),
			"indicator":"blue"
		})
	
	if not filters.show_summary_fields or  "departure" in filters.show_summary_fields:
			summary.append({
				"label": "departure",
				"value": sum([d["departure"] for d in  occupay_data]),
				"indicator":"blue"
			})
	if not filters.show_summary_fields or  "pax" in filters.show_summary_fields:
		summary.append({
			"label": "Pax",
			"value": "{}".format(sum([d["adult"] + d["child"] for d in  occupay_data]))
		})
	
	if not filters.show_summary_fields or  "adult" in filters.show_summary_fields:
		summary.append({
			"label": "Adult",
			"value":sum([d["adult"]  for d in  occupay_data])
		})
	if not filters.show_summary_fields or  "child" in filters.show_summary_fields:
		summary.append({
			"label": "Child",
			"value":sum([d["child"]  for d in  occupay_data])
		})

	
	return summary


def get_report_chart(filters,months,data):
	min_day = min([d["min_date"].day for d in months])
	max_day = max([d["max_date"].day for d in months])
	precision = frappe.db.get_single_value("System Settings","currency_precision")
	columns = []
	datasets = [
		{"name":"Vacant Room"},
		{"name":"Occupy"},
		{"name":"Occupancy(%)"},
		{"name":"Out of Order"},
		{"name":"Arrival"},
		{"name":"Stay Over"},
		{"name":"Departure"},
		{"name":"Adult"},
		{"name":"Child"},
		{"name":"Pax"},
	]
	if filters.show_chart_fields:
		datasets = [d for d in datasets if d["name"] in filters.show_chart_fields]

	for n in range(min_day, max_day +1):
		columns.append(n)


	for s in datasets:
		values = []
		for n in range(min_day, max_day +1):
			col_name= "col_" + str(n)
			values.append(sum([d[col_name] for d in data if "row_group" in d and d["row_group"]==s["name"]]))
		s["values"] = values
	

	chart = {
		'data':{
			'labels':columns,
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


