// Copyright (c) 2023, Tes Pheakdey and contributors
// For license information, please see license.txt

frappe.query_reports["Trail Balance Report"] = {
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
		{
			"fieldname": "ledger_types",
			"label": __("Ledger Type"),
			"fieldtype": "MultiSelectList",
			"options":[
				{value:"Reservation Folio","description": "Guest Ledger"},
				{value:"Desk Folio","description": "Desk Folio"},
				{value:"Deposit Ledger","description": "Deposit Ledger"},
				{value:"City Ledger","description": "City Ledger"},
				{value:"Payable Ledger","description": "Payable Ledger"},
				{value:"Cashier Shift","description": "Food & Beverage"},
			],
			"on_change": function (query_report) { },
			"hide_in_filter": 1,
		},
		
		{
			"fieldname": "guest",
			"label":"Guest",
			"fieldtype":"Link",
			"options": "Customer",
			"on_change": function (query_report) { },
		},
		{
			"fieldname": "city_ledger",
			"label":"City Ledger",
			"fieldtype":"Link",
			"options": "City Ledger",
			"on_change": function (query_report) { },
		},

		{
			"fieldname": "reservation",
			"label":"Reservation",
			"fieldtype":"Link",
			"options": "Reservation",
			"on_change": function (query_report) { },
		},
		{
			"fieldname": "reservation_stay",
			"label":"Reservation Stay",
			"fieldtype":"Link",
			"options": "Reservation Stay",
			"on_change": function (query_report) { },
		},
		{
			"fieldname": "show_account_code",
			"label": __("Show Account Code"),
			"fieldtype": "Check",
			"default": 1,
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
			"fieldname": "show_package_breakdown",
			"label": __("Show Package Breakdown"),
			"fieldtype": "Check",
			"default":1,
			hide_in_filter:1,
			"on_change": function (query_report) {},
		},
		{
			"fieldname": "show_all_breakdown",
			"label": __("Show All Breakdown"),
			"fieldtype": "Check",
			"default":0,
			hide_in_filter:1,
			"on_change": function (query_report) {},
		},

		{
			"fieldname": "group_by_ledger_type",
			"label": __("Group by Ledger Type"),
			"fieldtype": "Check",
			"default": 0,
			hide_in_filter: 1,
			"on_change": function (query_report) { },
		},
		
		// {
		// 	"fieldname": "chart_type",
		// 	"label": __("Chart Type"),
		// 	"fieldtype": "Select",
		// 	"options": "None\nbar\nline\npie",
		// 	"default": "bar",
		// 	hide_in_filter: 1,
		// 	"on_change": function (query_report) { },
		// }

	],
	onload: function (report) {
		report.page.add_inner_button("Preview Report", function () {
			frappe.query_report.refresh();
		});

		setLinkField()


	},
	"formatter": function (value, row, column, data, default_formatter) {
		const origninal_value = value || 0
		value = default_formatter(value, row, column, data);



		value = value.toString().replace("style='text-align: right'", "style='text-align: " + column.align + "'");


		if (
			(column.fieldtype || "") == "Int" ||
			((column.fieldtype || "") == "Percent") ||
			((column.fieldtype || "") == "Currency")
		) {
			if (origninal_value == 0) {
				return "<div style='text-align:" + (column.align || "left") + ";'>-</div>"
			}
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
		const reservation = frappe.query_report.get_filter('reservation');
		reservation.df.get_query = function () {
			return {
				filters: {
					"property": property
				}
			};
		};
		

		const reservation_stay = frappe.query_report.get_filter('reservation_stay');
		reservation_stay.df.get_query = function () {
			return {
				filters: {
					"property": property
				}
			};
		};
		
		frappe.query_report.get_filter('city_ledger').df.get_query = function () {
			return {
				filters: {
					"property": property
				}
			};
		};

		 
	}

}