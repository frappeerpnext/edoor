 
// Copyright (c) 2022, Frappe Technologies and contributors
// For license information, please see license.txt
/* eslint-disable */
frappe.query_reports["City Ledger Report"] = {

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
			"fieldname": "city_ledger_type",
			"label": __("City Ledger Type"),
			"fieldtype": "Link",
			"options":"City Ledger Type",
		}, 
		{
			"fieldname": "business_source",
			"label": __("Business Source"),
			"fieldtype": "Link",
			"options":"Business Source",
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

 