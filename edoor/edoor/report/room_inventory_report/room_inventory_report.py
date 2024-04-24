# Copyright (c) 2023, Tes Pheakdey and contributors
# For license information, please see license.txt
from frappe.utils import getdate, add_to_date
import frappe


def execute(filters=None):
	if getdate(filters.start_date) > getdate(filters.end_date):
		frappe.throw("Start date cannot less than end date")

	min_max_day = get_min_max_day(filters)
	columns = get_report_columns(filters,min_max_day)
	report_data = get_report_data(filters,min_max_day)
	

	return columns, report_data["report_data"],None, report_data["report_chart"], report_data["report_summary"]

def get_report_columns(filters,min_max_day):
	columns = [
		{"fieldname": "row_group", "label":"Room Type", "width": 200},
	]
	columns.append({
		"fieldname":"total","label": "Total", "width":100, "align":"center",
	})
	
	for n in range(min_max_day["min_day"], min_max_day["max_day"]+1):
		columns.append({
			"fieldname":"col_" + str(n),"label": "{}".format(n), "width":50, "align":"center"
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
				
				
				room_type_record["total"] = (room_type_record["total"] or 0) + total_occupy 
				date = add_to_date(date, days=1)
			
			room_inventory_records.append(room_type_record)

		report_data = report_data + room_inventory_records
		#vacant room
		vacant_record = {"row_group": "Vacant Room","total":0,"indent":1,"is_group":0}
		occupy_record = {"row_group": "Occupy","total":0,"indent":1,"is_group":0}
		ooo_record = {"row_group": "Out of Order","total":0,"indent":1,"is_group":0}
		occupancy_record = {"row_group": "Occupancy(%)","total":0,"indent":1,"is_group":1}
		arrival_record = {"row_group": "Arrival","total":0,"indent":1,"is_group":0}
		stay_over_record = {"row_group": "Stay Over","total":0,"indent":1,"is_group":0}
		departure_record = {"row_group": "Departure","total":0,"indent":1,"is_group":0}
		adult_record = {"row_group": "Adult","total":0,"indent":1,"is_group":0}
		child_record = {"row_group": "Child","total":0,"indent":1,"is_group":0}
		pax_record = {"row_group": "Pax","total":0,"indent":1,"is_group":0}

		date = m["min_date"]
		while date <= m["max_date"]: 
			col_name = "col_" + str(date.day)
			vacant_record[col_name] = sum(d[col_name] for d  in  room_inventory_records) or 0
			vacant_record["total"] = (vacant_record["total"] or 0) + vacant_record[col_name] 
			
			#occupy record
			occupy_record[col_name] = sum(d["occupy"] for d  in  room_occupy if d["date"] == date) or 0
			occupy_record["total"] = (occupy_record["total"] or 0) + occupy_record[col_name]
			
			#ooc record
			ooo_record[col_name] = sum(d["block"] for d  in  room_occupy if d["date"] == date) or 0
			ooo_record["total"] = (ooo_record["total"] or 0) + ooo_record[col_name]
			
			#occupancy

			total_rooms = (sum([d["total_room"] for d in daily_property_data if d["date"] == date]))
			calculate_room_occupancy_include_room_block = frappe.db.get_single_value("eDoor Setting", "calculate_room_occupancy_include_room_block")
			if calculate_room_occupancy_include_room_block==0:
				total_rooms = total_rooms - (ooo_record[col_name] or 0)
			if total_rooms<=0:
				total_rooms = 1

			occupancy_record[col_name] =round(occupy_record[col_name] /total_rooms * 100,(2 if filters.show_decimal_place_in_room_occupy else 0) )
		
			#arrival
			arrival_record[col_name] = sum(d["arrival"] for d  in  room_occupy if d["date"] == date) or 0
			arrival_record["total"] = (arrival_record["total"] or 0) + arrival_record[col_name]
			
			#stay over
			stay_over_record[col_name] = sum(d["stay_over"] for d  in  room_occupy if d["date"] == date) or 0
			stay_over_record["total"] = (stay_over_record["total"] or 0) + stay_over_record[col_name]
			
			#departure
			departure_record[col_name] = sum(d["departure"] for d  in  room_occupy if d["date"] == date) or 0
			departure_record["total"] = (departure_record["total"] or 0) + departure_record[col_name]

			#adult
			adult_record[col_name] = sum(d["adult"] for d  in  room_occupy if d["date"] == date) or 0
			adult_record["total"] = (adult_record["total"] or 0) + adult_record[col_name]
			
			#child
			child_record[col_name] = sum(d["child"] for d  in  room_occupy if d["date"] == date) or 0
			child_record["total"] = (child_record["total"] or 0) + child_record[col_name]
			#pax
			pax_record[col_name] = sum(d["adult"]  + d["child"] for d  in  room_occupy if d["date"] == date) or 0
			pax_record["total"] = (pax_record["total"] or 0) + pax_record[col_name]

			
			
			date = add_to_date(date, days=1)

		report_data.append(vacant_record)
		report_data.append(occupy_record)
		report_data.append(ooo_record)
		#update total occupancy percentage
		total_rooms = (sum([d["total_room"] for d in daily_property_data if d["date"]>=m["min_date"] and d["date"]<=m["max_date"]]))
		
		if calculate_room_occupancy_include_room_block==0:
			total_rooms = total_rooms - (ooo_record["total"] or 0)
		if total_rooms<=0:
			total_rooms = 1
		occupancy_record["total"] =round((occupy_record["total"] / total_rooms) * 100,2)
		report_data.append(occupancy_record)
		report_data.append(arrival_record)
		report_data.append(stay_over_record)
		report_data.append(departure_record)
		report_data.append(adult_record)
		report_data.append(child_record)
		report_data.append(pax_record)

		

	grand_total_data = get_grand_total_row(filters, months, room_occupy, daily_property_data)
	if len(months)>1:
		report_data += grand_total_data
	
	return {
		"report_data":report_data, 
		"report_summary":get_report_summary(filters, room_occupy,daily_property_data),
		"report_chart": get_report_chart(filters,months, grand_total_data if len(months)>1 else report_data)
	}

def get_grand_total_row(filters,months, occupy_data, daily_property_data):
	rows = [{
		"row_group":"Grand Total",
		"indent":0,
		"is_group":1,
	}]
	

	min_day = min([d["min_date"].day for d in months])
	max_day = max([d["max_date"].day for d in months])

	vacant_record = {"row_group": "Vacant Room","total":0,"indent":1,"is_group":0}
	occupy_record = {"row_group": "Occupy","total":0,"indent":1,"is_group":0}
	ooo_record = {"row_group": "Out of Order","total":0,"indent":1,"is_group":0}
	occupancy_record = {"row_group": "Occupancy(%)","total":0,"indent":1,"is_group":1}
	arrival_record = {"row_group": "Arrival","total":0,"indent":1,"is_group":0}
	stay_over_record = {"row_group": "Stay Over","total":0,"indent":1,"is_group":0}
	departure_record = {"row_group": "Departure","total":0,"indent":1,"is_group":0}
	adult_record = {"row_group": "Adult","total":0,"indent":1,"is_group":0}
	child_record = {"row_group": "Child","total":0,"indent":1,"is_group":0}
	pax_record = {"row_group": "Pax","total":0,"indent":1,"is_group":0}

	for n in range(min_day, max_day+1):
		col_name = "col_" + str(n)
		total_rooms = sum([d["total_room"] for d in daily_property_data if getdate(d["date"]).day == n])
		occupy = sum([d["occupy"] for d in occupy_data if getdate(d["date"]).day == n])
		block = sum([d["block"] for d in occupy_data if getdate(d["date"]).day == n])

		vacant_record[col_name] = total_rooms - ((occupy or 0) + (block or 0))
		vacant_record["total"] = (vacant_record["total"] or 0) + vacant_record[col_name] 
		
		#occupy record
		occupy_record[col_name] = occupy
		occupy_record["total"] = (occupy_record["total"] or 0) + occupy_record[col_name]

		
		#ooc record
		ooo_record[col_name] =block
		ooo_record["total"] = (ooo_record["total"] or 0) + ooo_record[col_name]
		
		#occupancy
		calculate_room_occupancy_include_room_block = frappe.db.get_single_value("eDoor Setting", "calculate_room_occupancy_include_room_block")
		if calculate_room_occupancy_include_room_block==0:
			total_rooms = total_rooms - (ooo_record[col_name] or 0)
		if total_rooms<=0:
			total_rooms = 1

		occupancy_record[col_name] =round(occupy_record[col_name] /total_rooms * 100,2)
	
		#arrival
		arrival_record[col_name] = sum(d["arrival"] for d  in  occupy_data  if getdate(d["date"]).day == n) or 0
		arrival_record["total"] = (arrival_record["total"] or 0) + arrival_record[col_name]
		
		#stay over
		stay_over_record[col_name] = sum(d["stay_over"] for d  in  occupy_data  if getdate(d["date"]).day == n) or 0
		stay_over_record["total"] = (stay_over_record["total"] or 0) + stay_over_record[col_name]
		
		#departure
		departure_record[col_name] = sum(d["departure"] for d  in  occupy_data  if getdate(d["date"]).day == n) or 0
		departure_record["total"] = (departure_record["total"] or 0) + departure_record[col_name]

		#adult
		adult_record[col_name] = sum(d["adult"] for d  in  occupy_data  if getdate(d["date"]).day == n) or 0
		adult_record["total"] = (adult_record["total"] or 0) + adult_record[col_name]
		
		#child
		child_record[col_name] = sum(d["child"] for d  in   occupy_data  if getdate(d["date"]).day == n) or 0
		child_record["total"] = (child_record["total"] or 0) + child_record[col_name]
		#pax
		pax_record[col_name] = sum(d["adult"]  + d["child"] for d  in   occupy_data  if getdate(d["date"]).day == n) or 0
		pax_record["total"] = (pax_record["total"] or 0) + pax_record[col_name]

	rows.append(vacant_record)
	rows.append(occupy_record)
	rows.append(ooo_record)
	#update total occupancy percentage
	total_rooms = sum([d["total_room"] for d in daily_property_data])
	
	if calculate_room_occupancy_include_room_block==0:
		total_rooms = total_rooms - (ooo_record["total"] or 0)
	if total_rooms<=0:
		total_rooms = 1
	occupancy_record["total"] =round((occupy_record["total"] / total_rooms) * 100,2)

	rows.append(occupancy_record)
	rows.append(arrival_record)
	rows.append(stay_over_record)
	rows.append(departure_record)
	rows.append(adult_record)
	rows.append(child_record)
	rows.append(pax_record)

	return rows

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

def get_months(filters):
	sql="select   month(date) as month, year(date) as year, date_format(date, '%%b-%%Y') as str_month, min(date) as min_date,max(date) as max_date from `tabDates` where date between %(start_date)s and %(end_date)s group by month(date),year(date) order by year(date), month(date)"
	return frappe.db.sql(sql,filters, as_dict=1)

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


