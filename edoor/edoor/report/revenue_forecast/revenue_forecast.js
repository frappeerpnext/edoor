// Copyright (c) 2023, Tes Pheakdey and contributors
// For license information, please see license.txt

frappe.query_reports["Revenue Forecast"] = {
	"filters": [
			{
				"fieldname": "property",
				"label": __("Property"),
				"fieldtype":"Link",
				"options":"Business Branch"
			}
	]
};
