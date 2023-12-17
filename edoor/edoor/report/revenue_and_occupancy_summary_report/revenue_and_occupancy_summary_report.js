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
			"on_change": function (query_report) {},
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
			"fieldname": "customer_group",
			"label": __("Guest Type"),
			"fieldtype": "MultiSelectList",
			get_data: function(txt) {
				return frappe.db.get_link_options('Customer Group', txt);
			},
			"on_change": function (query_report) {},
		},
		{
			"fieldname": "parent_row_group",
			"label": __("Parent Group By"),
			"fieldtype": "Select",
			"options": "\nDate\nMonth\nYear\nReservation Type\nBusiness Source\nRoom Type\nRoom\nPOS Profile\nCustomer\nCustomer Group\nStock Location\nDate\n\Month\nYear\nSale Invoice\nWorking Day\nCashier Shift\nSale Type",
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
		
		console.log(column.align, value);
		if (value.indexOf("style='text-align: right'")>=0){
			console.log(column.align, value?.replace("style='text-align: right'","style='text-align: center'"));	
		}
		

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

 