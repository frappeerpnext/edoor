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
	
	report_data = get_report_data(filters)

	return get_columns(filters),report_data,None,None, None


def get_columns(filters):
	columns = [
		{'fieldname':'row_header','align':'center','label':'Room',"width":200 ,"show_in_report":1},
		{'fieldname':'occupancy','align':'center','label':'Occ(%)',"width":75 ,"show_in_report":1},
		
	]
	for n in range(1,32):
		columns.append(
			{'fieldname':str(n),'align':'center','label':str(n),"width":55 ,"show_in_report":1,"is_date":1},
		)
	return columns

def get_filters(filters):
	sql = " and property=%(property)s "
	if filters.get("room_type"):
		sql = sql + " and r.room_type_id in %(room_type)s "

	return sql

def get_month(filters):
	start_date = datetime.strptime(filters.start_date, '%Y-%m-%d')
	end_date = datetime.strptime(filters.end_date, '%Y-%m-%d')

	months = [{'month_number': dt.month, 'month_name': dt.strftime('%B'),"year": dt.year, "total_day":  calendar.monthrange(dt.year, dt.month)[1]} for dt in rrule(MONTHLY, dtstart=start_date, until=end_date)]

	return months

# def get_report_chart(filters):
# 	dataset = []
# 	colors = []

# 	chart = {
# 		'data':{
# 			'labels':  dataset,
# 			'datasets':dataset
# 		},
# 		"type": filters.chart_type,
# 		# "lineOptions": {
# 		# 	"regionFill": 1,
# 		# },
# 		'valuesOverPoints':1,
# 		"axisOptions": {"xIsSeries": 1},
		
# 	}
# 	return chart

def get_report_data(filters):
	sql="""
			select 
				2 as indent,
				name,
				room_number as row_header, 
				room_type,
				room_type_id,
				room_type_alias
			from 
				`tabRoom` r
			where
				3=3
				{}
			
		""".format(get_filters(filters))

	reservation_status = get_reservation_status()
	months = get_month(filters)
 
	data =   frappe.db.sql(sql,filters,as_dict=1)
	report_data = []
	occupy_data = get_occupy_data(filters)
	calculate_room_occupancy_include_room_block = frappe.db.get_single_value("eDoor Setting","calculate_room_occupancy_include_room_block")
	
	for m in months:
		#get room occupancy of current month
		
		totol_room_sold = len([d for d in occupy_data if getdate(d["date"]).strftime('%m') == str(m["month_number"]) and d["type"]=="Reservation" ]) 
		total_day = m["total_day"]

		total_rooms = len(data) * total_day
		if calculate_room_occupancy_include_room_block ==0:
			total_rooms = total_rooms - len( [d for d in  occupy_data if getdate(d["date"]).strftime('%m') == str(m["month_number"]) and d["type"]=="Block"])
		

		#get month occupancy
		month_record = {
			"indent":0,
			"row_header": m["month_name"],
			"occupancy": round(totol_room_sold / total_rooms * 100,2) 
		}
		for n in range(1,total_day +1):
			total_rooms = len(data) 
			totol_room_sold = len([d for d in occupy_data if getdate(d["date"]).strftime('%m') == str(m["month_number"]) and int(getdate(d["date"]).strftime('%d')) == n and d["type"]=="Reservation" ]) 
			if calculate_room_occupancy_include_room_block == 0:
				total_rooms = total_rooms - len( [d for d in  occupy_data if getdate(d["date"]).strftime('%m') == str(m["month_number"]) and int(getdate(d["date"]).strftime('%d')) == n   and d["type"]=="Block"])
			

			month_record[str(n)] =   round(totol_room_sold / total_rooms * 100,2) 
		
		report_data.append(month_record)



		#end render month record
		#start render room type record

		room_types =  list(dict.fromkeys((d['room_type_id'], d['room_type']) for d in data))
		
	
		for rt in room_types:
			rooms = copy.deepcopy([d for d in data if d["room_type_id"]==rt[0]])
			
			current_month_data = [d for d in  occupy_data if getdate(d["date"]).strftime('%m') == str(m["month_number"]) and d["room_type_id"]==rt[0]]
			totol_room_sold = len([d for d in current_month_data if getdate(d["date"]).strftime('%m') == str(m["month_number"]) and d["room_type_id"]==rt[0]  and d["type"]=="Reservation"])
			total_rooms = len(rooms) * total_day
			if calculate_room_occupancy_include_room_block ==0:
				total_rooms = total_rooms - len( [d for d in current_month_data if getdate(d["date"]).strftime('%m') == str(m["month_number"]) and d["room_type_id"]==rt[0]  and d["type"]=="Block"])
			
			room_type_record = {
			"indent":1,
			"row_header": rt[1],
			"occupancy": round(totol_room_sold / total_rooms * 100,2)
			}
			for n in range(1,total_day +1):
				total_rooms = len(rooms)
				totol_room_sold = len([d for d in current_month_data if getdate(d["date"]).strftime('%m') == str(m["month_number"]) and int(getdate(d["date"]).strftime('%d')) == n and d["room_type_id"]==rt[0] and d["type"]=="Reservation" ]) 
				if calculate_room_occupancy_include_room_block == 0:
					total_rooms = total_rooms - len( [d for d in current_month_data if getdate(d["date"]).strftime('%m') == str(m["month_number"]) and int(getdate(d["date"]).strftime('%d')) == n   and d["room_type_id"]==rt[0] and d["type"]=="Block"])
				
				room_type_record[str(n)] = round(totol_room_sold / total_rooms * 100,2)

			report_data.append(room_type_record)

			for r in rooms:
				totol_room_sold = len([d for d in occupy_data if getdate(d["date"]).strftime('%m') == str(m["month_number"]) and d["room_type_id"]==rt[0] and d["room_id"] == r["name"] and d["type"]=="Reservation" ]) 
				total_rooms =  total_day
				if calculate_room_occupancy_include_room_block ==0:
					total_rooms = total_rooms - len( [d for d in  occupy_data if getdate(d["date"]).strftime('%m') == str(m["month_number"]) and d["room_type_id"]==rt[0] and d["room_id"] == r["name"] and d["type"]=="Block"])
				r["occupancy"] = round(totol_room_sold / total_rooms * 100,2)

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
		"indent":0,
		"row_header":"Grand Total",
		"occupancy":round(totol_room_sold / total_rooms * 100,2)
	})

	return report_data


def get_occupy_data(filters):
	sql = "select date,room_id,room_type_id,reservation_status,type from `tabRoom Occupy` where is_departure=0 and date between %(start_date)s and %(end_date)s and property=%(property)s"
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
	