 
// Copyright (c) 2022, Frappe Technologies and contributors
// For license information, please see license.txt
/* eslint-disable */
frappe.query_reports["Guest Ledger Report"] = {

	"filters": [
		
		{
			"fieldname":"start_date",
			"label": __("Start Date"),
			"fieldtype": "Date",
			default:frappe.datetime.get_today(),
			"reqd": 1
		},
		{
			"fieldname":"end_date",
			"label": __("End Date"),
			"fieldtype": "Date",
			default:frappe.datetime.get_today(),
			"reqd": 1
		},
		{
			"fieldname": "property",
			"label": __("Property"),
			"fieldtype": "Link",
			"options":"Business Branch",
			"reqd": 1
			
		} ,
		{
			"fieldname": "reservation",
			"label": __("Reservation"),
			"fieldtype": "Link",
			"options":"Reservation",
		} ,
		
		{
			"fieldname": "reservation_stay",
			"label": __("Reservation Stay"),
			"fieldtype": "Link",
			"options":"Reservation Stay",
		} ,
		{
			"fieldname": "business_source",
			"label": __("Business Source"),
			"fieldtype": "Link",
			"options":"Business Source",
		} ,
		{
			"fieldname": "guest",
			"label": __("Guest"),
			"fieldtype": "Link",
			"options":"Customer",
			
		}, 
		{
			"fieldname": "reservation_status",
			"label": __("Reservation Status"),
			"fieldtype": "Link",
			"options":"Reservation Status",
			
		}, 
		{
			"fieldname": "is_master",
			"label": __("Show Master Folio Only"),
			"fieldtype": "Check",
			
		} 

	],
	"formatter": function(value, row, column, data, default_formatter) {
	
		value = default_formatter(value, row, column, data);

		if (data && data.is_group==1) {
			value = $(`<span>${value}</span>`);

			var $value = $(value).css("font-weight", "bold");
			

			value = $value.wrap("<p></p>").parent().html();
		}
		
		return value;
	},
	
};

 