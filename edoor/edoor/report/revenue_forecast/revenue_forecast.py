# Copyright (c) 2023, Tes Pheakdey and contributors
# For license information, please see license.txt

import frappe


def execute(filters=None):
	
	return get_columns(filters), get_data(filters)

def get_columns(filters):
	return [
		{"fieldname":"name","label":"Guest","width":150,"align":"center", "fieldtype":"Link", "options":"Customer"},
		{"fieldname":"customer_name_en","label":"Guest Name","width":250,"align":"right" },
		{"fieldname":"amount","label":"Total Purchase","width":250,"fieldtype":"Currency" }
	]

def get_data(filters):
	sql ="select name, customer_name_en, 145 as amount from `tabCustomer`"
	return frappe.db.sql(sql,as_dict=1)

	# return get_columns(filters), report_data, message, report_chart, get_report_summary(report_data,filters),skip_total_row
