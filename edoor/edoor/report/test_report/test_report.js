// Copyright (c) 2023, Tes Pheakdey and contributors
// For license information, please see license.txt

frappe.query_reports["Test Report"] = {
	"filters": [
		{
			"fieldname": "filter_date_by",
			"label": __("Filter Date By"),
			"fieldtype": "Select",
			"options": "Arrival Date\nDeparture Date\nReservation\nStay Date",
			default:"Arrival Date"
		},
	]
};
