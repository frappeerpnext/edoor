# Copyright (c) 2024, Tes Pheakdey and contributors
# For license information, please see license.txt

import frappe


def execute(filters=None):
	frappe.throw("ss")
	columns, data = [{"fieldname":"aaaa","label":"Sale Reveenu","fieldtype":"Currency"},{"fieldname":"b","label":"Sale Reveenu","fieldtype":"Currency"}], [{"a":50,"b":45},{"a":50,"b":55}]
	return columns, data
