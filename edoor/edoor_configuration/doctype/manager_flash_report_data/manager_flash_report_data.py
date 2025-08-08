# Copyright (c) 2025, Tes Pheakdey and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class ManagerFlashReportData(Document):
	pass

@frappe.whitelist()
def generate_report(date):
	pass


@frappe.whitelist()
def get_revenue_summary(date='2025-08-07'):
	# get revenue group from Flash Report Key
	sql = "select name from `tabFlash Report Key` where `group` = 'Revenue Group' order by sort_order"
	data = frappe.db.sql(sql, as_dict=1)
	# today to tal
	
	return data


