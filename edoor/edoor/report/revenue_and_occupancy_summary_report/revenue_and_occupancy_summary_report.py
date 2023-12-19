# Copyright (c) 2023, Tes Pheakdey and contributors
# For license information, please see license.txt

from edoor.edoor.report.revenue_and_occupancy_summary_report import report_by_date
from edoor.api.frontdesk import get_working_day
import frappe
def execute(filters=None):
	if filters.parent_row_group==filters.row_group:
		frappe.throw("Parent row group and row group can not be the same")
		
	report_config = frappe.get_last_doc("Report Configuration", filters={"property":filters.property, "report":"Revenue and Occupancy Summary Report"} )
	 
	
	report = None
	if filters.row_group == "Date":
		report =  report_by_date.get_report(filters, report_config)

	message = "This is report is for past date transaction"

	return report["columns"], report["data"],message,report["report_chart"], report["report_summary"],True

	# return get_columns(filters), report_data, message, report_chart, get_report_summary(report_data,filters),skip_total_row


def get_report_columns(filters,report_config):
	columns = [d for d in row_group_columns() if d["key"] == filters.row_group]

	#group by date
	 


	#room avalidable
	columns.append({"fieldname":"room_available","label":"Room Avai","width":100})
	for g in report_config.report_fields:
		if g.show_in_report==1:
			columns.append({"fieldname":g.fieldname,"label":g.label,"width":g.width,"fieldtype":g.fieldtype,"aligh":"right"})
	
	return columns

def row_group_columns():
	return [
		{'key': "Date","fieldname":"row_group","label":"Date","fieldtype":"Date","width":125,},
		{'key':"Month","fieldname":"row_group","label":"Month","width":100},
		{'key':"Year","fieldname":"row_group","label":"Year","width":50},
		{'key':"Reservation Type","fieldname":"row_group","label":"Reservation Type","width":150},
		{'key':"Business Source","fieldname":"row_group","label":"Business Source","width":150},
		{'key':"Room Type","fieldname":"row_group","label":"Room Type","width":200},
		{'key':"Room","fieldname":"row_group","label":"Room","width":75},
	]

def get_report_data(filters,report_config):
	calculate_room_occupancy_include_room_block = frappe.db.get_single_value("eDoor Setting", "calculate_room_occupancy_include_room_block")

	data = get_occupy_data(filters,report_config)
	folio_transaction_data = get_folio_transaction_data(filters,report_config)


	#get row group data 
	report_data = []
	
	if filters.row_group in ["Date","Month","Year"]:
 
		report_data = get_row_group_report_data(filters, report_config)
		
	else:
		#get row group data for reservation type, business source, ...
		report_data =report_group_row_from_result_data(data, folio_transaction_data)
		


	room_available_datas= get_room_available(filters)
	total_rooms = get_total_rooms(filters)
	#assign value for data
	for row in report_data:
		#set default value 0 for field that dont have value
		for d in  report_config.report_fields:
			row[d.fieldname] = 0

		#room available
		if filters.row_group in ["Date","Month","Year","Room Type"]:
			room_available_record = [d for d in room_available_datas if str(d["row_group"])==str(row["row_group"]) ]
			if len(room_available_record)>0:
				row["room_available"] = room_available_record[0]["total_rooms"]
			else:
				row["room_available"] = total_rooms
		else:
			# room available is same for each record
			if len(room_available_datas)>0:
				row["room_available"] = room_available_datas[0]["total_rooms"]


		occupy_records = [d for d in data if d["row_group"] == row["row_group"]]
		if len(occupy_records)> 0:
				#occupy
				occupy_record = occupy_records[0]
				# set value occupy dynamic field
				for f in report_config.report_fields :
					if f.show_in_report==1 and f.reference_doctype=="Room Occupy":
						#set static field
						#room occupy
						if f.fieldname=='occupancy':
							
							if calculate_room_occupancy_include_room_block==1:
								row["occupancy"] = (row["occupy"] or 0) / (1 if row["room_available"] <=0 else row["room_available"]) 
							else:
								row["occupancy"] = (row["occupy"] or 0) / (1 if (row["room_available"]  - row["room_block"])<=0 else (row["room_available"]  - row["room_block"]))
							row["occupancy"] = row["occupancy"] * 100
						else:
							row[f.fieldname] =   occupy_record[f.fieldname]
		
		# get data from folio folio transaction
							
		if len(folio_transaction_data)> 0:
			folio_transaction_records  = [d for d in folio_transaction_data if d["row_group"] == row["row_group"]]
			if len(folio_transaction_records)> 0:

				folio_transaction_record  = folio_transaction_records[0]
				for f in report_config.report_fields :
					if f.show_in_report==1 and f.reference_doctype=="Folio Transaction":
						#f.fildname is from report config
						if f.fieldname=='adr':
							row['adr'] = (row["room_charge"] or 0) / (1 if  (row["occupy"] or 0) == 0 else (row["occupy"] or 0) -(row["complimentary"] + row["house_use"] ))
						else:
		
							row[f.fieldname] =   folio_transaction_record[f.fieldname]
						



	return report_data

def report_group_row_from_result_data(occupy_data, folio_transaction_data):

	row_group = [d["row_group"] for d in occupy_data]
	row_group = row_group +  [d["row_group"] for d in folio_transaction_data]
	row_group = set(row_group)
	row_group =  [{"row_group": d} for d in row_group]
	return row_group


def get_row_group_report_data(filters,report_config):
	sql =""
	if filters.row_group =='Date':
		# get date from table Dates
		sql ="select date as row_group from `tabDates` where date between %(start_date)s and %(end_date)s order by date"
		 
	elif filters.row_group =='Month':
		sql ="select distinct date_format(date,'%%b-%%Y') as row_group from `tabDates` where date between %(start_date)s and %(end_date)s order by date"
	 
	elif filters.row_group =='Year':
		sql ="select distinct year(date) row_group from `tabDates` where date between %(start_date)s and %(end_date)s order by date"
	data = frappe.db.sql(sql,filters,as_dict=1)
	 

	return data
	
def get_occupy_data(filters,report_config):
	sql = "select "
	# select field
	# group row field
	sql = f'{sql} {get_room_occupy_group_by_field(filters)} as row_group,'

	#other aggregate field
	sql = "{} {}".format(sql,','.join([d.sql_expression for d in report_config.report_fields if d.reference_doctype =='Room Occupy' and d.sql_expression]) )

	
	#filter
	sql = sql+ " from `tabRoom Occupy` a where 1=1 "
	sql = sql + " and date between %(start_date)s and %(end_date)s and property=%(property)s "

	# group by
	sql = '{} group by {}'.format(sql, get_room_occupy_group_by_field(filters))
	data = frappe.db.sql(sql,filters,as_dict = 1)
	
	return data


def get_room_occupy_group_by_field(filters):
	group_by =  ",".join([d["value"] for d in room_occupy_group_by_fields() if d["key"] == filters.row_group])
 
	return group_by

def room_occupy_group_by_fields():
	# a. is base table alias
	return [
		{"key":"Date", "value": "a.date" },
		{"key":"Month", "value": "date_format(a.date,'%%b-%%Y')"},
		{"key":"Year", "value": "year(a.date)"},
		{"key":"Reservation Type", "value": "a.reservation_type"},
		{"key":"Business Source", "value": "a.business_source"},
		{"key":"Room Type", "value": "a.room_type_id"}
	]



def get_room_available(filters):
	sql=""
	if filters.row_group in ["Date","Month","Year"]:
		if filters.row_group=="Date":
			sql ="select date as row_group, sum(total_room) as total_rooms from `tabDaily Property Data` where "
		elif filters.row_group=="Month":
			sql ="select date_format(date,'%%b-%%Y') as row_group, sum(total_room) as total_rooms from `tabDaily Property Data` where "
		elif filters.row_group=="Year":
			sql ="select date_format(date,'%%Y') as row_group, sum(total_room) as total_rooms from `tabDaily Property Data` where "
		#set where statement
		sql = sql + " property=%(property)s and date between %(start_date)s and %(end_date)s "
		if filters.room_type:
			sql = sql + " and room_type=%(room_type)s"

		#group by
		if filters.row_group=="Date":
			sql = sql + " group by date"
		elif filters.row_group=="Month":
			sql = sql + "  group by  date_format(date,'%%b-%%Y') "	
		elif filters.row_group=="Year":
			sql = sql + "  group by  date_format(date,'%%Y') "
	elif filters.row_group == "Room Type":
		sql = "select room_type_id, sum(total_room) as total_rooms from `tabDaily Property Data` where property=%(property)s and date between %(start_date)s and %(end_date)s group by room_type_id"
	else:
		sql = "select sum(total_room) as total_rooms from `tabDaily Property Data` where property=%(property)s and date between %(start_date)s and %(end_date)s"

	

	return frappe.db.sql(sql,filters, as_dict=1)

def get_total_rooms(filters):
	data =  frappe.db.sql("select count(name)  as total_room from `tabRoom` where disabled=0 and property=%(property)s",filters,as_dict=1)
	if data:
		return data[0]["total_room"]
	return 0



def get_folio_transaction_data(filters, report_config ):
	sql = "select "
	# select field
	# group row field
	sql = f'{sql} {get_folio_transaction_group_by_field(filters)} as row_group,'
	#other 
	sql = "{} {}".format(sql,','.join([d.sql_expression for d in report_config.report_fields if d.reference_doctype =='Folio Transaction' and d.sql_expression]) )
	#filter
	sql = sql+ " from `tabFolio Transaction` a where transaction_type='Reservation Folio' "

	sql = sql + " and posting_date between %(start_date)s and %(end_date)s and property=%(property)s "
	# group by
	sql = '{} group by {}'.format(sql, get_folio_transaction_group_by_field(filters))

	data = frappe.db.sql(sql,filters,as_dict = 1)
 
	return data

def get_folio_transaction_group_by_field(filters):
	return [d["value"] for d in folio_transaction_group_by_fields() if d["key"] == filters.row_group][0]

def folio_transaction_group_by_fields():
	# a. is base table alias
	return [
		{"key":"Date", "value": "a.posting_date" },
		{"key":"Month", "value": "date_format(a.posting_date,'%%b-%%Y')"},
		{"key":"Year", "value": "year(a.posting_date)"},
		{"key":"Reservation Type", "value": "a.reservation_type"},
		{"key":"Business Source", "value": "a.business_source"},
		{"key":"Room Type", "value": "a.room_type_id"}
	]




	