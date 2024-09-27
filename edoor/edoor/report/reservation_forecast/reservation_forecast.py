# Copyright (c) 2023, Tes Pheakdey and contributors
# For license information, please see license.txt

from edoor.edoor.report.reservation_forecast import report_by_date
from edoor.edoor.report.reservation_forecast import report_by_month
from edoor.edoor.report.reservation_forecast import report_by_year
from edoor.edoor.report.reservation_forecast import report_by_business_source
from edoor.edoor.report.reservation_forecast import report_by_reservation_type
from edoor.edoor.report.reservation_forecast import report_by_business_source_type
from edoor.edoor.report.reservation_forecast import report_by_guest_type
from edoor.edoor.report.reservation_forecast import report_by_nationality
from edoor.edoor.report.reservation_forecast import report_by_room_type
from edoor.edoor.report.reservation_forecast import report_by_rate_type
from edoor.edoor.report.reservation_forecast import report_by_business_source_type_group
from frappe import _
import frappe
import copy
def execute(filters=None):
    
	if filters.parent_row_group==filters.row_group:
		frappe.throw("Parents row group and row group can not be the same")

	if filters.parent_row_group == "Date" and filters.row_group == "Month":
		frappe.throw("Parents row group cannot be Date and Row group cannot be Month")

	if filters.parent_row_group == "Date" and filters.row_group == "Year":
		frappe.throw("Parents row group cannot be Date and Row group cannot be Year")
	
	if filters.parent_row_group == "Date" and filters.row_group == "Room Type":
		frappe.throw("This Option is coming soon")

	

	if filters.chart_type =='pie' or filters.chart_type=="donut":
		if len(filters.show_chart_series)!=1:
			frappe.throw(_("Please select only one series for the chart, either a pie or donut chart."))
		
	report_config = frappe.get_last_doc("Report Configuration", filters={"property":filters.property, "report":"Reservation Forecast"} )
	
	report = None
	if filters.row_group == "Date":
		report =  report_by_date.get_report(filters, report_config)
	elif filters.row_group == "Month":
		report =  report_by_month.get_report(filters, report_config)
	elif filters.row_group == "Year":
		report =  report_by_year.get_report(filters, report_config)
	elif filters.row_group == "Business Source":
		report =  report_by_business_source.get_report(filters, report_config)	
	elif filters.row_group == "Reservation Type":
		report =  report_by_reservation_type.get_report(filters, report_config)
	elif filters.row_group == "Business Source Type":
		report =  report_by_business_source_type.get_report(filters, report_config)
	elif filters.row_group == "Business Source Group":
		report =  report_by_business_source_type_group.get_report(filters, report_config)

	elif filters.row_group == "Guest Type":
		report =  report_by_guest_type.get_report(filters, report_config)
	elif filters.row_group == "Nationality":
		report =  report_by_nationality.get_report(filters, report_config)
	elif filters.row_group == "Room Type":
		report =  report_by_room_type.get_report(filters, report_config)
	elif filters.row_group == "Rate Type":
		report =  report_by_rate_type.get_report(filters, report_config)


	
	message = None

	if filters.sort_order_field and  not filters.parent_row_group:
		# apply sort 
		report_data = copy.deepcopy(report["data"] )
		report_data  = sorted([d for d in report_data if d.get("is_total_row",0) == 0], key=lambda x: x.get(filters.sort_order_field, 0), reverse=(filters.sort_type =="DESC"))
  
		report_data = report_data + [d for d in report["data"] if d.get("is_total_row",0) == 1]
	else:
	 
		report_data = report["data"] 

	return report["columns"], report_data,message,report["report_chart"], report["report_summary"],True

 
	