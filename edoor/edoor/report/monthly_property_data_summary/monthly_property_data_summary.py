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
	
	return columns, report_data["data"],message,report_data["report_chart"],report_data["report_summary"]

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


def get_min_max_day(filters):
	sql = "select min(day(date)) as min_day, max(day(date)) as max_day from `tabDates` where date between %(start_date)s and %(end_date)s"
	data = frappe.db.sql(sql,filters,as_dict=1)
	return data [0]


