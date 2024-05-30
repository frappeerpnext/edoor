// Copyright (c) 2024, Tes Pheakdey and contributors
// For license information, please see license.txt

frappe.query_reports["Learn Report"] = {
	"filters": [
		{
			"fieldname":"property",
			"fieldtype":"Link",
			"options": "Business Branch",
			"label":"Property",
			"reqd":1
		},
		{
			"fieldname":"arrival_date",
			"fieldtype":"Date"
		}
	]
};
