// Copyright (c) 2024, Tes Pheakdey and contributors
// For license information, please see license.txt

frappe.query_reports["Room Revenue Detail Report"] = {
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
		// {
		// 	"fieldname": "show_in_summary",
		// 	"label": __("Summary Field"),
		// 	"fieldtype": "MultiSelectList",
		// 	get_data: function(txt) {
		// 		return [
		// 			{"value":"total_record","description":"Total Room",name:"Total Room",fieldtype:"Int", width:100,align:"center"},
		// 			{"value":"room_charge","description":"Total Room Revenue",name:"Total Room Revenue",fieldtype:"Currency", width:100,align:"center"},
		// 			{"value":"room_charge_adjustment","description":"Total Room Adj",fieldtype:"Currency",name:"Total Room Adj", width:100,align:"center"},
		// 			{"value":"other_room_charge","description":"Total Other Room Revenue",name:"Total Other Room Revenue",fieldtype:"Currency", width:100,align:"center"},
		// 			{"value":"service_charge","description":"Total Service Charge",name:"Total Service Charge",fieldtype:"Currency", width:100,align:"right"},
		// 			{"value":"tax","description":"Total Tax",name:"Total Tax",fieldtype:"Currency", width:100 ,align:"right"},
		// 			{"value":"occupy","description":"Total Occ.",name:"BalTotal Occ.ance",fieldtype:"Currency", width:100,align:"right"},
		// 		]
		// 	},
		// 	hide_in_filter:1,
		// 	"on_change": function (query_report) {},
		// },
		{
			"fieldname": "chart_type",
			"label": __("Chart Type"),
			"fieldtype": "Select",
			"options": "None\nbar\nline\npie", 
			hide_in_filter:1,
			"on_change": function (query_report) {},
		},
		{
			"fieldname": "view_chart_by",
			"label": __("View Chart By"),
			"fieldtype": "Select",
			"options": "\nRoom\nRoom Type",
			hide_in_filter:1,
			"on_change": function (query_report) {},
		},
		{
			"fieldname": "chart_series",
			"label": __("Chart Series"),
			"fieldtype": "MultiSelectList",
			get_data: function(txt) {
				return [
					{"value":"Room Revenue","description":"Room Revenue",fieldtype:"Currency", align:"center"},
					{"value":"Room Adj","description":"Room Adj",fieldtype:"Currency",align:"center"},
					{"value":"Other Room Revenue","description":"Other Room Revenue",fieldtype:"Currency", align:"center"},
					{"value":"Service Charge","description":"Service Charge",fieldtype:"Currency", align:"right"},
					{"value":"Tax","description":"Tax",fieldtype:"Currency",align:"right"},
					{"value":"Total Revenue","description":"Total Revenue",fieldtype:"Currency",align:"right"},
					{"value":"Occupy","description":"Occupy",fieldtype:"Currency", align:"right"},
					{"value":"ADR","description":"ADR",fieldtype:"Currency", align:"right"},
				]
			},
			hide_in_filter:1,
			"on_change": function (query_report) {},
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



		if ((data && data.indent == 0) || (data && data.is_total_row == 1)) {

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
			report: "Room Charge Posting Report"
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
