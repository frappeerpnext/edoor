# Copyright (c) 2024, Tes Pheakdey and contributors
# For license information, please see license.txt

import frappe


def execute(filters=None):
	columns = get_columns(filters)
	data = get_report_data(filters)
 
	return columns, data

def get_columns(filters):
    return [
		{"fieldname":"today_revenue","label":"Today Revenue", "fieldtype":"Currency"}
	]
def get_report_data(filters):
    return [{
		"today_revenue":2501
	}
	]