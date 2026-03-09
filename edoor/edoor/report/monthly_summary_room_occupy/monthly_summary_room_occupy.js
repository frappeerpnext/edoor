// Copyright (c) 2024, Tes Pheakdey and contributors
// For license information, please see license.txt

frappe.query_reports["Monthly Summary Room Occupy"] = {
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
			"fieldname": "row_group",
			"label": __("Group By"),
			"fieldtype": "Select",
			"options": "Business Source\nBusiness Source Type\nReservation Type\nGuest\nGuest Type\nRoom\nRoom Type",
			"default": "Business Source",
			"on_change": function (query_report) { },
			hide_in_filter: 1,
		},
		{
			"fieldname": "building",
			"label": __("Building"),
			"fieldtype": "Link",
			"options": "Building",
			"on_change": function (query_report) { },
		},
	],
	onload: function (report) {
		report.page.add_inner_button("Preview Report", function () {
			frappe.query_report.refresh();
		});

		setLinkField()


	},
};
function setLinkField() {
	const property = frappe.query_report.get_filter_value("property")
	if (property) {
		const business_source_filter = frappe.query_report.get_filter('building');
		business_source_filter.df.get_query = function () {
			return {
				filters: {
					"property": property
				}
			};
		};

	}

}