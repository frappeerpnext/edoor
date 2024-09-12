// Copyright (c) 2023, Tes Pheakdey and contributors
// For license information, please see license.txt

frappe.query_reports["Room Inventory Report"] = {
	"filters": [
		{
			fieldname: "property",
			label: "Property",
			fieldtype: "Link",
			options: "Business Branch",
			default: frappe.defaults.get_user_default("business_branch"),
			"reqd": 1,
			"on_change": function (query_report) {
				setLinkField()
			},
		},
		{
			"fieldname": "start_date",
			"label": __("Start Date"),
			"fieldtype": "Date",
			default: new Date((new Date()).getFullYear(), (new Date()).getMonth(), 1),
			"reqd": 1,
			"on_change": function (query_report) {
				// Get the selected start date
				let start_date = frappe.query_report.get_filter_value('start_date');
				
				// Convert to JavaScript Date object
				let startDateObj = new Date(start_date);
				
				// Calculate end date as exactly 30 or 31 days later
				let endDateObj = new Date(startDateObj);
				endDateObj.setDate(startDateObj.getDate() + 30); // Add 30 days
				
				// Adjust for months with 31 days or months with fewer days
				// If the end date is in the next month and exceeds the last day of that month
				let lastDayOfEndMonth = new Date(endDateObj.getFullYear(), endDateObj.getMonth() + 1, 0); // Last day of the end month
				if (endDateObj > lastDayOfEndMonth) {
					endDateObj = lastDayOfEndMonth;
				}
				
				// Set the end date filter value to ensure it falls within 30/31 day range
				frappe.query_report.set_filter_value('end_date', endDateObj);
			},
		},
		{
			"fieldname": "end_date",
			"label": __("End Date"),
			"fieldtype": "Date",
			default: new Date((new Date()).getFullYear(), (new Date()).getMonth() + 1, 0),
			"reqd": 1,
			"on_change": function (query_report) { }
		},		
				
		{
			"fieldname": "show_decimal_place_in_room_occupy",
			"label": __("Show/Hide Decimal Places in Occupancy Record"),
			"fieldtype": "Check",
			"default": 0,
			hide_in_filter: 1,
			"on_change": function (query_report) { },
		},
		{
			"fieldname": "show_summary",
			"label": __("Show Summary"),
			"fieldtype": "Check",
			"default": 1,
			hide_in_filter: 1,
			"on_change": function (query_report) { },
		},
		{
			"fieldname": "show_summary_fields",
			"label": __("Show Summary Field"),
			"fieldtype": "MultiSelectList",
			"on_change": function (query_report) { },
			"hide_in_filter": 1,
			"options":[
				{value:"total_room",description:"Total Room Available"},
				{value:"occupy",description:"Occupy"},
				{value:"ooo",description:"Out of Order"},
				{value:"vacant",description:"Vacant"},
				{value:"occupancy",description:"Occupancy"},
				{value:"arrival",description:"Arrival"},
				{value:"stay_over",description:"Occupy"},
				{value:"departure",description:"Departure"},
				{value:"pax",description:"Pax"},
				{value:"adult",description:"Adult"},
				{value:"child",description:"Child"},
			]

		},
		
		{
			"fieldname": "chart_type",
			"label": __("Chart Type"),
			"fieldtype": "Select",
			"options": "None\nbar\nline\npie",
			"default": "line",
			hide_in_filter: 1,
			"on_change": function (query_report) { },
		},
{
			"fieldname": "show_chart_fields",
			"label": __("Show chart fields"),
			"fieldtype": "MultiSelectList",
			"on_change": function (query_report) { },
			"hide_in_filter": 1,
			"options": [
				{"value":"Vacant Room","description":"Vacant Room"},
				{"value":"Occupy","description":"Occupy"},
				{"value":"Occupancy(%)","description":"Occupancy(%)"},
				{"value":"Out of Order","description":"Out of Order"},
				{"value":"Arrival", "description":"Arrival"},
				{"value":"Stay Over","description":"Stay Over"},
				{"value":"Departure","description":"Departure", },
				{"value":"Adult","description":"Adult"},
				{"value":"Child", "description":"Adult"},
				{"value":"Pax","description":"Pax"},
			]

		},
		{
			"fieldname": "view_separate_month",
			"label": __("View in Separate Month"),
			"fieldtype": "Check",
			hide_in_filter: 1,
			"on_change": function (query_report) { },
		},
	],
	onload: function (report) {
		report.page.add_inner_button("Preview Report", function () {
			frappe.query_report.refresh();
		});

		setLinkField();
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
	"formatter": function (value, row, column, data, default_formatter) {
		const origninal_value = value || 0
		value = default_formatter(value, row, column, data);



		value = value.toString().replace("style='text-align: right'", "style='text-align: " + column.align + "'");

 
			
		if (origninal_value == 0 || origninal_value == "0") {
			return "<div style='text-align:" + (column.align || "left") + ";'>-</div>"
		}
	 




		if ((data && data.is_group == 1) || (data && data.is_total_row == 1)) {

			value = $(`<span>${value}</span>`);

			var $value = $(value).css("font-weight", "bold");


			value = $value.wrap("<p></p>").parent().html();
		}


		return value;
	},

};



function setLinkField() {
	const property = frappe.query_report.get_filter_value("property")
	if (property) {
		 
		
		// frappe.query_report.get_filter('room_type').df.get_query = function () {
		// 	return {
		// 		filters: {
		// 			"property": property
		// 		}
		// 	};
		// };

		 
	}

}