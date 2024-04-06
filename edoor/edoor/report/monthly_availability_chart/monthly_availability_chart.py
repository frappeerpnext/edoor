# Copyright (c) 2023, Tes Pheakdey and contributors
# For license information, please see license.txt
import frappe
from frappe import _
from frappe.utils import date_diff,today ,add_months, add_days
from frappe.utils.data import getdate, strip
import datetime
import uuid
from dateutil.rrule import rrule, MONTHLY
from datetime import datetime
import copy
import calendar
def execute(filters=None):
	data = get_data(filters)
	report_data = get_report_data(filters,data)
	chart = get_chart(filters,report_data)
	return get_columns(filters),report_data,None,chart, None


def get_columns(filters):
	columns = [
		{'fieldname':'row_header','align':'left','label':'Room',"width":150 ,"show_in_report":1},
		{'fieldname':'occupancy','align':'center','label':'Occ(%)',"width":75 ,"show_in_report":1},
		
	]
	for n in range(1,32):
		columns.append(
			{'fieldname':str(n),'align':'center','label':str(n),"width":55 ,"show_in_report":1,"is_date":1},
		)
	return columns

def get_filters(filters):
	sql = " and property=%(property)s "
	if filters.get("room_name_types"):
		sql = sql + " and r.room_type_id in %(room_name_types)s "

	return sql

def get_month(filters):
	start_date = datetime.strptime(filters.start_date, '%Y-%m-%d')
	end_date = datetime.strptime(filters.end_date, '%Y-%m-%d')

	months = [{'month_number': dt.month, 'month_name': dt.strftime('%B'),"year": dt.year, "total_day":  calendar.monthrange(dt.year, dt.month)[1]} for dt in rrule(MONTHLY, dtstart=start_date, until=end_date)]

	return months
def get_data(filters):
	sql="""
			select 
				2 as indent,
				name,
				room_number as rooms,
				room_number as row_header, 
				room_type,
				room_type_id,
				room_type_alias
			from 
				`tabRoom` r
			where
				3=3
				{0}
			order by 
				sort_order, room_number
		""".format(get_filters(filters))
	data =   frappe.db.sql(sql,filters,as_dict=1)
	return data

def get_report_data(filters,data):
	
	reservation_status = get_reservation_status()
	months = get_month(filters)
	
	
	report_data = []
	occupy_data = get_occupy_data(filters)
 
	calculate_room_occupancy_include_room_block = frappe.db.get_single_value("eDoor Setting","calculate_room_occupancy_include_room_block")
	
	for m in months:
		#get room occupancy of current month
		
		totol_room_sold = len([d for d in occupy_data if  int(getdate(d["date"]).strftime('%m')) == int(m["month_number"]) and d["type"]=="Reservation" ]) 
		total_day = m["total_day"]

		total_rooms = len(data) * total_day
		if calculate_room_occupancy_include_room_block ==0:
			total_rooms = total_rooms - len( [d for d in  occupy_data if int(getdate(d["date"]).strftime('%m')) == int(m["month_number"]) and d["type"]=="Block"])
		
		#start render room type record

		room_types =  list(dict.fromkeys((d['room_type_id'], d['room_type']) for d in data))
		#get month occupancy
		month_record = {
			"indent":0,
			"row_header": m["month_name"],
			"header":1,
			"occupancy": round(totol_room_sold / (1 if total_rooms==0 else total_rooms) * 100,2) 
		}
		for n in range(1,total_day +1):
			total_rooms = len(data) 
			totol_room_sold = len([d for d in occupy_data if int(getdate(d["date"]).strftime('%m')) == int(m["month_number"]) and int(getdate(d["date"]).strftime('%d')) == n and d["type"]=="Reservation" ]) 
			if calculate_room_occupancy_include_room_block == 0:
				total_rooms = total_rooms - len( [d for d in  occupy_data if int(getdate(d["date"]).strftime('%m')) == int(m["month_number"]) and int(getdate(d["date"]).strftime('%d')) == n   and d["type"]=="Block"])
			

			month_record[str(n)] =   round(totol_room_sold / (1 if total_rooms==0 else total_rooms) * 100,2) 
		
		report_data.append(month_record)



		#end render month record
		
	
		for rt in room_types:
			
			rooms = copy.deepcopy([d for d in data if d["room_type_id"]==rt[0]])

			current_month_data = [d for d in  occupy_data if  int(getdate(d["date"]).strftime('%m')) == int(m["month_number"]) and d["room_type_id"]==rt[0]]

			totol_room_sold = len([d for d in current_month_data if int(getdate(d["date"]).strftime('%m')) == int(m["month_number"]) and d["room_type_id"]==rt[0]  and d["type"]=="Reservation"])
			total_rooms = len(rooms) * total_day
			if calculate_room_occupancy_include_room_block ==0:
				total_rooms = total_rooms - len( [d for d in current_month_data if int(getdate(d["date"]).strftime('%m')) == int(m["month_number"]) and d["room_type_id"]==rt[0]  and d["type"]=="Block"])
			
			room_type_record = {
			"indent":1,
			"row_header": rt[1],
			"month":m["month_name"],
			"occupancy": round(totol_room_sold / (1 if total_rooms==0 else total_rooms) * 100,2)
			}
			for n in range(1,total_day +1):
				total_rooms = len(rooms)
				totol_room_sold = len([d for d in current_month_data if int(getdate(d["date"]).strftime('%m')) == int(m["month_number"]) and int(getdate(d["date"]).strftime('%d')) == n and d["room_type_id"]==rt[0] and d["type"]=="Reservation" ]) 
				if calculate_room_occupancy_include_room_block == 0:
					total_rooms = total_rooms - len( [d for d in current_month_data if int(getdate(d["date"]).strftime('%m')) == int(m["month_number"]) and int(getdate(d["date"]).strftime('%d')) == n   and d["room_type_id"]==rt[0] and d["type"]=="Block"])
				
				room_type_record[str(n)] = round(totol_room_sold / (1 if total_rooms==0 else total_rooms) * 100,2)

			report_data.append(room_type_record)
			
			for r in rooms:
				totol_room_sold = len([d for d in occupy_data if int(getdate(d["date"]).strftime('%m')) == int(m["month_number"]) and d["room_type_id"]==rt[0] and d["room_id"] == r["name"] and d["type"]=="Reservation" ]) 
				total_rooms =  total_day
				if calculate_room_occupancy_include_room_block ==0:
					total_rooms = total_rooms - len( [d for d in  occupy_data if int(getdate(d["date"]).strftime('%m')) == int(m["month_number"]) and d["room_type_id"]==rt[0] and d["room_id"] == r["name"] and d["type"]=="Block"])
				r["occupancy"] = round(totol_room_sold / (1 if total_rooms==0 else total_rooms) * 100,2)

			#start render room record
			
			for md in current_month_data:
				room = [d for d in rooms if d["name"]==md["room_id"] ] 
				if room:
					if md["type"]=="Block":
						room[0][str(int(getdate(md["date"]).strftime('%d')))] = "BL"
					else:
						status = get_status(reservation_status,md["reservation_status"])
						room[0][str(int(getdate(md["date"]).strftime('%d')))] = "" if not status else status["alias"]

			report_data = report_data + rooms

	totol_room_sold = len([d for d in occupy_data if d["type"]=="Reservation" ]) 
	total_day = sum([d["total_day"] for d in months])

	total_rooms = len(data) * total_day
	if calculate_room_occupancy_include_room_block ==0:
		total_rooms = total_rooms - len( [d for d in  occupy_data if d["type"]=="Block"])
	report_data.append({
		"indent":3,
		"row_header":"Grand Total",
		"occupancy":round(totol_room_sold / (1 if total_rooms==0 else total_rooms) * 100,2),
		"is_grand_total":1
	})
	return report_data


def get_occupy_data(filters):
	sql = "select date,room_id,room_type_id,reservation_status,type from `tabRoom Occupy` where is_active=1 and date between %(start_date)s and %(end_date)s and property=%(property)s"
	data = frappe.db.sql(sql,filters,as_dict=1)
	return data

def get_reservation_status():
	sql = "select name,alias,color from `tabReservation Status`"
	data = frappe.db.sql(sql,as_dict=1)
	return data

def get_status(reservation_status, name):
	data = [d for d in reservation_status if d["name"]==name]
	if data:
		return data[0]
	else:
		return None
	
def get_chart(filters,data):
	# frappe.throw(str([obj["room_type"] for obj in data if "room_type" in obj]))
	currency_precision = frappe.db.get_single_value("System Settings","currency_precision")
	if filters.chart_type=="None" or not filters.chart_option:
		return None

	dataset = []
	colors = []
	dataset_values = []

	group_column = get_field(filters)
	if group_column["label"] == "Occupancy by Month":
		group_data = sorted(set([d[group_column["data_field"]] for d  in data if d['indent'] == 0]))
	# frappe.throw(str(group_column))
		for g in group_data: 

			amount = ([d['occupancy'] for d in data if d[group_column["data_field"]] == g])
				
			if group_column["fieldtype"]  =="Currency":
				amount = round(amount,int(currency_precision))


			dataset_values.append(
				amount
			)



		dataset.append({'name':group_column["label"],'values':dataset_values})
		colors.append(group_column["chart_color"])

	
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
	
	elif group_column["label"] == "Room Type":
		group_data = sorted(set([d[group_column["data_field"]] for d  in data if d['indent'] == 1]))
	# frappe.throw(str(group_column))
		for g in group_data: 

			amount = sum([d['occupancy'] for d in data if d[group_column["data_field"]] == g])
				
			if group_column["fieldtype"]  =="Currency":
				amount = round(amount,int(currency_precision))


			dataset_values.append(
				amount
			)



		dataset.append({'name':group_column["label"],'values':dataset_values})
		colors.append(group_column["chart_color"])

	
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
	
	elif group_column["label"] == "Room":
		group_data = sorted(set([d[group_column["data_field"]] for d  in data if d['indent'] == 2]))
	# frappe.throw(str(group_column))
		for g in group_data: 

			amount = sum([d['occupancy'] for d in data if d[group_column["data_field"]] == g])
				
			if group_column["fieldtype"]  =="Currency":
				amount = round(amount,int(currency_precision))


			dataset_values.append(
				amount
			)



		dataset.append({'name':group_column["label"],'values':dataset_values})
		colors.append(group_column["chart_color"])

	
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
	
def get_field(filters):

	return  [d for d in get_report_field() if d["label"] == filters.chart_option][0]

def get_report_field():
	return [
		{"data_field":"row_header", "label":"Occupancy by Month","fieldtype":"Data","chart_color":"#dc9819"},
		{"data_field":"row_header", "label":"Room Type" ,"fieldtype":"Data","chart_color":"#1987dc" },
		{"data_field":"row_header", "label":"Room" ,"fieldtype":"Data" ,"chart_color":"#fd4e8a"}
	]

	