// Copyright (c) 2023, Tes Pheakdey and contributors
// For license information, please see license.txt
 
frappe.query_reports["Revenue and Occupancy Summary Report"] = {
	"filters": [
		{
			fieldname: "property",
			label: "Property",
			fieldtype: "Link",
			options:"Business Branch",
			default:frappe.defaults.get_user_default("business_branch") ,
			"reqd": 1,
			"on_change": function (query_report) {

				const property = frappe.query_report.get_filter_value("property")
				const business_source_filter =frappe.query_report.get_filter('business_source');
				business_source_filter.df.get_query = function() {
					return {
						filters: {
							"property": property
						}
					};
				};
				//room type
				const room_type_filter =frappe.query_report.get_filter('room_type');
				room_type_filter.df.get_query = function() {
					return {
						filters: {
							"property": property
						}
					};
				};

				 
			},
		},
		{
			"fieldname":"start_date",
			"label": __("Start Date"),
			"fieldtype": "Date",
			default: new Date( (new Date()).getFullYear(), ( new Date()).getMonth(), 1),
			"reqd": 1,
			"on_change": function (query_report) {},
		},
		{
			"fieldname":"end_date",
			"label": __("End Date"),
			"fieldtype": "Date",
			default: new Date((new Date()).getFullYear(), (new Date()).getMonth() + 1, 0),
			"on_change": function (query_report) {},
			"reqd": 1
		},

		{
			"fieldname": "room_type",
			"label": __("Room Type"),
			"fieldtype": "Link",
			"options":"Room Type",
			"on_change": function (query_report) {},
		},
		{
			"fieldname": "business_source",
			"label": __("Business Source"),
			"fieldtype": "Link",
			"options":"Business Source",
			"on_change": function (query_report) {},
		},
		{
			"fieldname": "guest_type",
			"label": __("Guest Type"),
			"fieldtype": "Link",
			"options":"Customer Group",
			"on_change": function (query_report) {},
		},
		{
			"fieldname": "parent_row_group",
			"label": __("Parent Group By"),
			"fieldtype": "Select",
			"options": "\nDate\nMonth\nYear\nReservation Type\nBusiness Source\nBusiness Source Type",
			"on_change": function (query_report) {},
			hide_in_filter:1,
		},
		{
			"fieldname": "row_group",
			"label": __("Row Group By"),
			"fieldtype": "Select",
			"options": "Date\n\Month\nYear\nReservation Type\nBusiness Source\nRoom Type\nRoom\nOutlet\nTable Group\nTable\nPOS Profile\nCustomer\nCustomer Group\nStock Location\nSale Invoice\nWorking Day\nCashier Shift\nSale Type",
			"default":"Date",
			"on_change": function (query_report) {},
			hide_in_filter:1,
		},

		// {
		// 	"fieldname": "column_group",
		// 	"label": __("Column Group By"),
		// 	"fieldtype": "Select",
		// 	"options": "None\nDaily\nWeekly\nMonthly\nQuarterly\nHalf Yearly\nYearly",
		// 	"default":"None"
		// },
		{
			"fieldname": "show_summary",
			"label": __("Show Summary"),
			"fieldtype": "Check",
			"default":1,
			hide_in_filter:1,
			"on_change": function (query_report) {},
		},
		{
			"fieldname": "chart_type",
			"label": __("Chart Type"),
			"fieldtype": "Select",
			"options": "None\nbar\nline\npie",
			"default":"bar",
			hide_in_filter:1,
			"on_change": function (query_report) {},
		},
		 
	],
	onload: function(report) {
		report.page.add_inner_button ("Preview Report", function () {
			frappe.query_report.refresh();
		});
		report.page.add_inner_dropdown ("Preview Report", function () {
			frappe.query_report.refresh();
		});
		
	},
	"formatter": function(value, row, column, data, default_formatter) {
		const origninal_value = value  || 0
		value = default_formatter(value, row, column, data);
		
		
		 
		value = value.toString().replace("style='text-align: right'","style='text-align: " + column.align + "'");	
	 
 
		if (
			(column.fieldtype || "") == "Int" || 
			((column.fieldtype || "") == "Percent") ||
			((column.fieldtype || "") == "Currency" ) 
		) 
		{
			if(origninal_value==0){
				return "-"
			}
		} 


		
		if ((data && data.is_group==1) || (data && data.is_total_row==1)) {
			
			value = $(`<span>${value}</span>`);

			var $value = $(value).css("font-weight", "bold");
			

			value = $value.wrap("<p></p>").parent().html();
		} 
	 
 
		return value;
	},
	
};

 