// Copyright (c) 2023, Tes Pheakdey and contributors
// For license information, please see license.txt

frappe.query_reports["Manager Flash Report"] = {
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
			"fieldname": "date",
			"label": __("Date"),
			"fieldtype": "Date",
			default:frappe.datetime.get_today(),
			"reqd": 1,
			"on_change": function (query_report) { },
		}        

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
				return "-"
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
		const business_source_filter = frappe.query_report.get_filter('business_source');
		business_source_filter.df.get_query = function () {
			return {
				filters: {
					"property": property
				}
			};
		};
		//room type
		const room_type_filter = frappe.query_report.get_filter('room_type');
		room_type_filter.df.get_query = function () {
			return {
				filters: {
					"property": property
				}
			};
		};

		//set option for show fields




		frappe.call({
			method: "edoor.api.utils.get_report_config",

			args: {
				property: property,
				report: "Revenue and Occupancy Summary Report"
			},
			callback: function (r) {
				const show_columns = frappe.query_report.get_filter('show_columns');
				show_columns.df.options = r.message.report_fields.map(x => {
					return {
						value: x.fieldname,
						description: x.label
					}
				})
				const show_chart_series = frappe.query_report.get_filter('show_chart_series');
				show_chart_series.df.options = r.message.report_fields.filter(y=>y.show_in_chart==1).map(x => {
					return {
						value: x.fieldname,
						description: x.label
					}
				})
				
				const show_summary_field = frappe.query_report.get_filter('show_summary_field');
				show_summary_field.df.options = r.message.report_fields.filter(y=>y.show_in_chart==1).map(x => {
					return {
						value: x.fieldname,
						description: x.label
					}
				})
				
			},
			error: function (r) {
				frappe.throw(_("Please update report configuration"))
			},
		});

	}

}