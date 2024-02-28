// Copyright (c) 2024, Tes Pheakdey and contributors
// For license information, please see license.txt

frappe.query_reports["Extra Charge List"] = {
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
			"fieldname": "parent_account",
			"label": __("Parent Account"),
			"fieldtype": "Link",
			"options":"Account Code",
			filters:{'parent_account_code':['in',['10000','40000']]},
			"on_change": function (query_report) {},
		},
		{
			"fieldname": "row_group",
			"label": __("Row Group By"),
			"fieldtype": "Select",
			"options": "\nDate\nAccount Code\nAccount Category\nParent Account",
			"on_change": function (query_report) {},
			hide_in_filter:1,
		},
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
		 {
			"fieldname": "view_chart_by",
			"label": __("View Chart By"),
			"fieldtype": "Select",
			"options": "\nDate\nAccount Code\nAccount Category\nParent Account",
			hide_in_filter:1,
			"on_change": function (query_report) {},
		},
		{
			"fieldname": "chart_series",
			"label": __("Chart Series"),
			"fieldtype": "MultiSelectList",
			get_data: function(txt) {
				return [
					{"value":"Amount","description":"Amount",fieldtype:"Currency","precision":2},
					{"value":"Discount Amount","description":"Discount Amount",fieldtype:"Currency","precision":2},
					{"value":"Total Tax","description":"Total Tax",fieldtype:"Currency","precision":2},
					{"value":"Total Amount","description":"Total Amount",fieldtype:"Currency"},
					{"value":"Quantity","description":"Quantity",fieldtype:"Int"},
				]
			},
			hide_in_filter:1,
			"on_change": function (query_report) {},
		},
		
		
		{
			"fieldname": "order_by",
			"label": __("Order By"),
			"fieldtype": "Select",
			"options": "Last Update On\nPosting Date\nTransaction\nAccount Code\nAccount Category\nParent Account",
			default:"Posting Date",
			hide_in_filter:1,
			"on_change": function (query_report) {},
		},
		{
			"fieldname": "sort_order",
			"label": __("Sort Order"),
			"fieldtype": "Select",
			"options": "ASC\nDESC",
			default:"ASC",
			hide_in_filter:1,
			"on_change": function (query_report) {},
		},
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
