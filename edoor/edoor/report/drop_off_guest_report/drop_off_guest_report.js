// Copyright (c) 2023, Tes Pheakdey and contributors
// For license information, please see license.txt

frappe.query_reports["Drop-off Guest Report"] = {
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
		{
			"fieldname":"end_date",
			"label": __("End Date"),
			"fieldtype": "Date",
			default:frappe.datetime.get_today(),
			"reqd": 1,
			"on_change": function (query_report) {},
		},
		{
			"fieldname": "business_source",
			"label": __("Business Source"),
			"fieldtype": "Link",
			"options":"Business Source",
			"on_change": function (query_report) {},
		} ,
		{
			"fieldname": "room_types",
			"label": __("Room Type"),
			"fieldtype": "MultiSelectList",
			get_data: function(txt) {
				property= frappe.query_report.get_filter_value("property");
				return frappe.db.get_link_options('Room Type', txt,filters={
					property:property
				});
			},
			"on_change": function (query_report){}
		},
		{
			"fieldname": "show_in_group_by",
			"fieldtype":"Select",
			"label": __("Group By"),
			"on_change": function (query_report){ },
			"hide_in_filter": 1,
			"options":"\nreservation\nroom_types\ndeparture_date\nbusiness_source"
			
		},
		{
			"fieldname": "show_columns",
			"label": __("Show Columns"),
			"fieldtype": "MultiSelectList",
			"on_change": function (query_report) { },
			"hide_in_filter": 1,
		},
		{
			"fieldname": "show_summary",
			"label": __("Show Summary"),
			"fieldtype": "Check",
			default:true,
			hide_in_filter:1,
			"on_change": function (query_report) {},
		},
		{
			"fieldname": "show_in_summary",
			"label": __("Show in Summary"),
			"fieldtype": "MultiSelectList",
			"on_change": function (query_report) { },
			"hide_in_filter": 1,
		},
		
	],
	onload: function(report) {
		report.page.add_inner_button ("Preview Report", function () {
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
		const room_type_filter = frappe.query_report.get_filter('room_types');
		room_type_filter.df.get_query = function () {
			return {
				filters: {
					"property": property
				}
			};
		};
		const business_source_filter = frappe.query_report.get_filter('business_source');
		business_source_filter.df.get_query = function () {
			return {
				filters: {
					"property": property
				}
			};
		};

	}

	frappe.call({
		method: "edoor.api.utils.get_report_config",

		args: {
			property: property,
			report: "Drop-off Guest Report"
		},
		callback: function (r) {
			const show_columns = frappe.query_report.get_filter('show_columns');
			show_columns.df.options = r.message.report_fields.map(x => {
				return {
					value: x.fieldname,
					description: x.label
				}
			})

			const show_in_summary = frappe.query_report.get_filter('show_in_summary');
			show_in_summary.df.options = r.message.report_fields.filter(y=>y.show_in_summary==1).map(x => {
				return {
					value: x.fieldname,
					description: x.label
				}
			})
			// const show_in_group_by = frappe.query_report.get_filter('show_in_group_by');
			// show_in_group_by.df.options = r.message.report_fields.filter(y=>y.show_in_group_by==1).map(x => {
			// 	return {
			// 		value: x.fieldname,
			// 		description: x.label
			// 	}
			// })
		},
		error: function (r) {
			frappe.throw(_("Please update report configuration"))
		},
	});


}
