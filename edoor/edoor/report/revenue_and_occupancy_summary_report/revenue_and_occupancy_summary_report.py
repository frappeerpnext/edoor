# Copyright (c) 2023, Tes Pheakdey and contributors
# For license information, please see license.txt

from edoor.edoor.report.revenue_and_occupancy_summary_report import report_by_date
from edoor.edoor.report.revenue_and_occupancy_summary_report import report_by_month
from edoor.edoor.report.revenue_and_occupancy_summary_report import report_by_year
from edoor.edoor.report.revenue_and_occupancy_summary_report import report_by_business_source
from edoor.edoor.report.revenue_and_occupancy_summary_report import report_by_reservation_type
from edoor.edoor.report.revenue_and_occupancy_summary_report import report_by_business_source_type
from edoor.edoor.report.revenue_and_occupancy_summary_report import report_by_guest_type
from edoor.edoor.report.revenue_and_occupancy_summary_report import report_by_nationality
from edoor.edoor.report.revenue_and_occupancy_summary_report import report_by_room_type
from edoor.api.frontdesk import get_working_day
from frappe import _
from frappe.utils import date_diff,today ,add_months, add_days,getdate,add_to_date
import frappe
from epos_restaurant_2023.utils import get_date_range_by_timespan

def execute(filters=None):
	if not filters.property:
		filters.property = frappe.defaults.get_user_default("business_branch")
	if not filters.property: 
		business_branch = frappe.db.get_list("Business Branch",pluck="name")
		if not filters.property and len(business_branch)>1:
			frappe.throw(_("Please select property"))
		else:
			filters.property = business_branch[0]

	
	if filters.timespan!="Date Range":
		date_range = get_date_range_by_timespan(filters.timespan)
		filters.start_date =date_range["start_date"]
		filters.end_date = date_range["end_date"]
  
  
	if filters.parent_row_group==filters.row_group:
		frappe.throw("Parent row group and row group can not be the same")
		
	report_config = frappe.get_last_doc("Report Configuration", filters={"property":filters.property, "report":"Revenue and Occupancy Summary Report"} )
	
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
	elif filters.row_group == "Guest Type":
		report =  report_by_guest_type.get_report(filters, report_config)
	elif filters.row_group == "Nationality":
		report =  report_by_nationality.get_report(filters, report_config)
		
	elif filters.row_group == "Room Type":
		report =  report_by_room_type.get_report(filters, report_config)

	message = _("This is report is for past date transaction")
	return report["columns"], report["data"],message,report["report_chart"], report["report_summary"],True

 
	