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
from edoor.edoor.report.monthly_availability_chart.monthly_avalability_chart_separate_by_month import get_report_datas

def execute(filters=None):
    
	# data = get_data(filters)
	# report_data = get_report_data(filters,data)
	# chart = get_chart(filters,report_data)

	report_datas = get_report_datas(filters)
	return report_datas["columns"],report_datas["report_data"],None,report_datas["report_chart"], None


def get_columns(filters):
	columns = [
		{'fieldname':'row_header','align':'left','label':'Room',"width":150 ,"show_in_report":1},
		{'fieldname':'occupancy','align':'center','label':'Occ(%)',"width":65 ,"show_in_report":1},
		{'fieldname':'occupy','align':'center','label':'Occ',"width":65 ,"show_in_report":1},
		{'fieldname':'block','align':'center','label':'OOO',"width":65 ,"show_in_report":1},
		
	]
	date = getdate(filters.start_date)
 
	while date<= getdate(filters.end_date):
		columns.append(
			{'fieldname':date,'align':'center','label': date.strftime('%d %b'),"width":75 ,"show_in_report":1,"is_date":1},
		)
		date = add_days(date,1)
  
	return columns

def get_filters(filters):
	sql = " and property=%(property)s "
	if filters.get("room_name_types"):
		sql = sql + " and r.room_type_id in %(room_name_types)s "

	return sql

def get_data(filters):
	sql="""
			select 
				1 as indent,
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

	
	
	report_data = []
	occupy_data = get_occupy_data(filters)
	calculate_room_occupancy_include_room_block = frappe.db.get_single_value("eDoor Setting","calculate_room_occupancy_include_room_block")
	
	#get room occupancy of current month

	totol_room_sold = len([d for d in occupy_data if    d["type"]=="Reservation" ]) 
	total_day = date_diff(filters.end_date, filters.start_date) + 1
	 

	total_rooms = len(data) * total_day
	if calculate_room_occupancy_include_room_block ==0:
		total_rooms = total_rooms - len( [d for d in  occupy_data if    d["type"]=="Block"])
	
	#start render room type record

	room_types =  list(dict.fromkeys((d['room_type_id'], d['room_type']) for d in data))
 
	for rt in room_types:
		rooms = copy.deepcopy([d for d in data if d["room_type_id"]==rt[0]])
		room_type_row = {"row_header": "{} ({})".format( rt[1], len(rooms))  }
		report_data.append(room_type_row)
  
		
		# show occupancy 
		
		date = getdate(filters.start_date)
		while date<= getdate(filters.end_date):
			occupy = len([d for d in occupy_data if d["type"] =="Reservation"  and date == d["date"] and d["room_type_id"] == rt[0] ])
			block = len([d for d in occupy_data if d["type"] =="Block" and date == d["date"] and d["room_type_id"] == rt[0] ])
			if int(frappe.get_cached_value("eDoor Setting",None, "calculate_room_occupancy_include_room_block")) ==1:
				total_room = len(rooms)
				if total_room == 0:
					total_room = 1
				room_type_row[str(date)] = round( occupy  / total_room * 100,2) 
			else:
				total_room = len(rooms) - block 
				if total_room == 0:
					total_room = 1
				room_type_row[str(date)] = round( occupy  / total_room * 100,2)
			
			date = add_days(date,1)
			
		# occupancy column of room type
		occupy = len([d for d in occupy_data if d["type"] =="Reservation"  and  d["room_type_id"] == rt[0] ])
		block = len([d for d in occupy_data if d["type"] =="Block" and   d["room_type_id"] == rt[0] ])
		room_type_row["occupy"] = occupy
		room_type_row["block"] = block
		if int(frappe.get_cached_value("eDoor Setting",None, "calculate_room_occupancy_include_room_block")) ==1:
			room_type_row["occupancy"] = round( occupy  / total_rooms * 100,2) 
		else:
			total_rooms =total_rooms - block 
			if total_room == 0:
				total_room = 1
			room_type_row["occupancy"] = round( occupy  / total_rooms * 100,2)
		


		report_data = report_data + rooms
	for occ in occupy_data:
		room = [d for d in  report_data if "name" in d and d["name"] == occ["room_id"]] 
		if room:
			room = room[0]
			status = get_status(reservation_status, occ["reservation_status"])
			if occ["type"] == "Block":
				room[str(occ["date"])] = "BL" 
			else:
				room[str(occ["date"])] = status["alias"]
		
  
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

	