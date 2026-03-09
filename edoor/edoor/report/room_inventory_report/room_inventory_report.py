# Copyright (c) 2023, Tes Pheakdey and contributors
# For license information, please see license.txt
from frappe.utils import getdate, add_to_date
import frappe
from edoor.edoor.report.room_inventory_report import room_inventory_separate_month
from edoor.edoor.report.room_inventory_report import monthly_room_inventory

def execute(filters=None):
	if getdate(filters.start_date) > getdate(filters.end_date):
		frappe.throw("Start date cannot less than end date")
	max_min_date = room_inventory_separate_month.get_min_max_day(filters)
	report = []
	if filters.view_separate_month:
		report = room_inventory_separate_month.get_report(filters,max_min_date)
	else:
		report = monthly_room_inventory.get_report(filters,max_min_date)
	


	return report["columns"], report["data"],None,report["report_chart"], report["report_summary"],True




