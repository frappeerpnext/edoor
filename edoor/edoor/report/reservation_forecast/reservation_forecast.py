# Copyright (c) 2023, Tes Pheakdey and contributors
# For license information, please see license.txt

from edoor.edoor.report.revenue_forecast import report_by_date
# from edoor.edoor.report.revenue_forecast import report_by_month
# from edoor.edoor.report.revenue_forecast import report_by_year
# from edoor.edoor.report.revenue_forecast import report_by_business_source
# from edoor.edoor.report.revenue_forecast import report_by_reservation_type
# from edoor.edoor.report.revenue_forecast import report_by_business_source_type
# from edoor.edoor.report.revenue_forecast import report_by_guest_type
# from edoor.edoor.report.revenue_forecast import report_by_nationality
# from edoor.edoor.report.revenue_forecast import report_by_room_type
from edoor.api.frontdesk import get_working_day
import frappe
def execute(filters=None):
	if filters.parent_row_group==filters.row_group:
		frappe.throw("Parent row group and row group can not be the same")
		
	report_config = frappe.get_last_doc("Report Configuration", filters={"property":filters.property, "report":"Revenue and Occupancy Summary Report"} )
	
	report = None
	if filters.row_group == "Date":
		report =  report_by_date.get_report(filters, report_config)
	# elif filters.row_group == "Month":
	# 	report =  report_by_month.get_report(filters, report_config)
	# elif filters.row_group == "Year":
	# 	report =  report_by_year.get_report(filters, report_config)
	# elif filters.row_group == "Business Source":
	# 	report =  report_by_business_source.get_report(filters, report_config)	
	# elif filters.row_group == "Reservation Type":
	# 	report =  report_by_reservation_type.get_report(filters, report_config)
	# elif filters.row_group == "Business Source Type":
	# 	report =  report_by_business_source_type.get_report(filters, report_config)
	# elif filters.row_group == "Guest Type":
	# 	report =  report_by_guest_type.get_report(filters, report_config)
	# elif filters.row_group == "Nationality":
	# 	report =  report_by_nationality.get_report(filters, report_config)
	# elif filters.row_group == "Room Type":
	# 	report =  report_by_room_type.get_report(filters, report_config)

	message = "This is report is for past date transaction"
	return report["columns"], report["data"],message,report["report_chart"], report["report_summary"],True

 
	