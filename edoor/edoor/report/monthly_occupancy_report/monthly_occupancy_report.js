// Copyright (c) 2023, Tes Pheakdey and contributors
// For license information, please see license.txt

frappe.query_reports["Monthly Occupancy Report"] = {
	"filters": [
		{
			fieldname: "property",
			label: "Property",
			fieldtype: "Link",
			options:"Business Branch",
			default:frappe.defaults.get_user_default("business_branch") ,
			"on_change": function (query_report) {
				 
			},
		},
		{
			"fieldname":"start_date",
			"label": __("Start Date"),
			"fieldtype": "Date",

			
			"on_change": function (query_report) {},
		},
		{
			"fieldname":"end_date",
			"label": __("End Date"),
			"fieldtype": "Date",

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
		report.page.add_inner_button("Print Report", function () {
			frappe.ui.get_print_settings(false, function(print_settings) {
			  frappe.query_report.print_report({
				  format: print_settings.format,
				  orientation: print_settings.orientation,
				  letter_head: print_settings.letter_head
			  });
		  });
		}).addClass('btn-print-custom').html('<i class="fa fa-print"></i> Print Report');
		 
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

 