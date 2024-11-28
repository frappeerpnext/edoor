// Copyright (c) 2024, Tes Pheakdey and contributors
// For license information, please see license.txt


frappe.query_reports["Monthly Property Data Summary"] = {
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
			"on_change": function (query_report) { },
		},
		{
			"fieldname": "end_date",
			"label": __("End Date"),
			"fieldtype": "Date",
			default: new Date((new Date()).getFullYear(), (new Date()).getMonth() + 1, 0),
			"on_change": function (query_report) { },
			"reqd": 1
		},
		// {
		// 	"fieldname": "building",
		// 	"label": __("Building"),
		// 	"fieldtype": "Link",
		// 	"options": "Building",
		// 	"on_change": function (query_report) { },
		// },
		{
			"fieldname": "row_group",
			"label": __("Group By"),
			"fieldtype": "Select",
			"options": "Business Source\nBusiness Source Type\nReservation Type\nGuest Type\nNationality\nRoom\nRoom Type",
			"default": "Business Source",
			"on_change": function (query_report) { },
			hide_in_filter: 1,
		},
		{
			"fieldname": "column_group",
			"label": __("Column Group"),
			"fieldtype": "Select",
			"options": "Occupy\nRevenue\nADR",
			"default": "Occupy",
			"on_change": function (query_report) { },
			hide_in_filter: 1,
		},
		
		{
			"fieldname": "chart_type",
			"label": __("Chart Type"),
			"fieldtype": "Select",
			"options": "None\nbar\nline\npie\ndonut",
			"default": "line",
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
			"fieldname": "hide_empty_record",
			"label": __("Hide Empty Record"),
			"fieldtype": "Check",
			"default": 0,
			"on_change": function (query_report) { },
			hide_in_filter: 1,
		},
 
	],
	onload: function (report) {
		report.page.add_inner_button("Preview Report", function () {
			frappe.query_report.refresh();
		});

		setLinkField();




	},
	"formatter": function (value, row, column, data, default_formatter) {
		const origninal_value = value || 0
		value = default_formatter(value, row, column, data);



		value = value.toString().replace("style='text-align: right'", "style='text-align: " + column.align + "'");

 
			
		if (origninal_value == 0 || origninal_value == "0") {
			return "<div style='text-align:" + (column.align || "left") + ";'>-</div>"
		}
	 




		if ((data && data.is_group == 1) || (data && data.is_total_row == 1) || (data && data.is_occupancy_row == 1)) {

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