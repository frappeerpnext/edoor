 
// Copyright (c) 2022, Frappe Technologies and contributors
// For license information, please see license.txt
/* eslint-disable */
frappe.query_reports["Guest Ledger Report"] = {

	"filters": [
		{
			fieldname: "property",
			label: "Property",
			fieldtype: "Link",
			options:"Business Branch",
			default:frappe.defaults.get_user_default("business_branch") ,
			"reqd": 1,
			"on_change": function (query_report) {
				setLinkField()
			},
		},
		{
			"fieldname":"start_date",
			"label": __("Start Date"),
			"fieldtype": "Date",
			default:frappe.datetime.get_today(),
			"reqd": 1,
			"on_change": function (query_report) {},
		},
		// {
		// 	"fieldname":"end_date",
		// 	"label": __("End Date"),
		// 	"fieldtype": "Date",
		// 	default:frappe.datetime.get_today(),
		// 	"reqd": 1,
		// 	"on_change": function (query_report) {},
		// },

		{
			"fieldname": "reservation",
			"label": __("Reservation"),
			"fieldtype": "Link",
			"options":"Reservation",
			"on_change": function (query_report) {},
		} ,
		
		{
			"fieldname": "reservation_stay",
			"label": __("Reservation Stay"),
			"fieldtype": "Link",
			"options":"Reservation Stay",
			"on_change": function (query_report) {},
		} ,
		{
			"fieldname": "business_source",
			"label": __("Business Source"),
			"fieldtype": "Link",
			"options":"Business Source",
			"on_change": function (query_report) {},
		} ,
		{
			"fieldname": "guest",
			"label": __("Guest"),
			"fieldtype": "Link",
			"options":"Customer",
			"on_change": function (query_report) {},
		}, 
		{
			"fieldname": "reservation_status",
			"label": __("Reservation Status"),
			"fieldtype": "Link",
			"options":"Reservation Status",
			"on_change": function (query_report) {},
		}, 
		{
			"fieldname": "is_master",
			"label": __("Show Master Folio Only"),
			"fieldtype": "Check",
			"on_change": function (query_report) {},
		} 

	],
	onload: function(report) {
		report.page.add_inner_button ("Preview Report", function () {
			frappe.query_report.refresh();
		});
		setLinkField()
		 
	},
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

function setLinkField() {
	const property = frappe.query_report.get_filter_value("property")
	if (property) {
		const business_source_filter = frappe.query_report.get_filter('business_source');
		business_source_filter.df.get_query = function () {
			return {
				filters: {
					"property": property
				}
			};
		};
		//set filter reservation
		frappe.query_report.get_filter('reservation').df.get_query = function () {
			return {
				filters: {
					"property": property
				}
			};
		};

		//set filter for stay
		frappe.query_report.get_filter('reservation_stay').df.get_query = function () {
			return {
				filters: {
					"property": property
				}
			};
		};

	}

} 