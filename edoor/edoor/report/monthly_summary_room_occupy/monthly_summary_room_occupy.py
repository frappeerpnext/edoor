# Copyright (c) 2024, Tes Pheakdey and contributors
# For license information, please see license.txt

import frappe
from edoor.edoor.report.monthly_summary_room_occupy import report_by_business_source

def execute(filters=None):
	report = None
	if filters.row_group:
		report = report_by_business_source(filters)
	return report["columns"], report["data"],None,None, None


