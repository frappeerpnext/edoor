// Copyright (c) 2023, Tes Pheakdey and contributors
// For license information, please see license.txt
 
 
frappe.query_reports["General Journal Transaction"] = {
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

				//set fitler city ledger
				const city_ledger =frappe.query_report.get_filter('city_ledger');
				city_ledger.df.get_query = function() {
					return {
						filters: {
							"property": property
						}
					};
				};
				//set filter reservation
				frappe.query_report.get_filter('reservation').df.get_query = function() {
					return {
						filters: {
							"property": property
						}
					};
				};
				
				//set filter for stay
				frappe.query_report.get_filter('reservation_stay').df.get_query = function() {
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
			"fieldname": "business_source_type",
			"label": __("Business Source Type"),
			"fieldtype": "Link",
			"options":"Business Source Type",
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
			"fieldname": "guest",
			"label": __("Guest"),
			"fieldtype": "Link",
			"options":"Customer",
			"on_change": function (query_report) {},
		},
		{
			"fieldname": "city_ledger",
			"label": __("City Ledger"),
			"fieldtype": "Link",
			"options":"City Ledger",
			"on_change": function (query_report) {},
		},
		{
			"fieldname": "reservation",
			"label": __("Reservation"),
			"fieldtype": "Link",
			"options":"Reservation",
			"on_change": function (query_report) {},
		},
		{
			"fieldname": "reservation_stay",
			"label": __("Reservation Stay"),
			"fieldtype": "Link",
			"options":"Reservation Stay",
			"on_change": function (query_report) {},
		},
		{
			"fieldname": "account_code",
			"label": __("Account Code"),
			"fieldtype": "Link",
			"options":"Account Code",
			"on_change": function (query_report) {},
		},
		{
			"fieldname": "account_category",
			"label": __("Account Category"),
			"fieldtype": "Link",
			"options":"Account Category",
			"on_change": function (query_report) {},
		},
 
		{
			"fieldname": "ledger_type",
			"label": __("Ledger Type"),
			"fieldtype": "MultiSelectList",
			"options":[
				{"label":"Guest Ledger", "value":"Reservation Folio"},
				{"label":"Deposit Ledger", "value":"Deposit Ledger"},
				{"label":"Desk Folio", "value":"Desk Folio"},
				{"label":"City Ledger", "value":"City Ledger"},
				{"label":"Payable Ledger", "value":"Payable Ledger"},
				{"label":"F&B", "value":"Cashier Shift"}
			],
			"on_change": function (query_report) {},
			hide_in_filter:1,
		},
		// {
		// 	"fieldname": "parent_row_group",
		// 	"label": __("Parent Group By"),
		// 	"fieldtype": "Select",
		// 	"options": "\nDate\nMonth\nYear\nReservation Type\nBusiness Source\nBusiness Source Type",
		// 	"on_change": function (query_report) {},
		// 	hide_in_filter:1,
		// },
		// {
		// 	"fieldname": "row_group",
		// 	"label": __("Row Group By"),
		// 	"fieldtype": "Select",
		// 	"options": "Date\n\Month\nYear\nReservation Type\nBusiness Source\nRoom Type\nRoom\nOutlet\nTable Group\nTable\nPOS Profile\nCustomer\nCustomer Group\nStock Location\nSale Invoice\nWorking Day\nCashier Shift\nSale Type",
		// 	"default":"Date",
		// 	"on_change": function (query_report) {},
		// 	hide_in_filter:1,
		// },

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
		// {
		// 	"fieldname": "chart_type",
		// 	"label": __("Chart Type"),
		// 	"fieldtype": "Select",
		// 	"options": "None\nbar\nline\npie",
		// 	"default":"bar",
		// 	hide_in_filter:1,
		// 	"on_change": function (query_report) {},
		// },
		 
	],
	onload: function(report) {
		report.page.add_inner_button ("Preview Report", function () {
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

 