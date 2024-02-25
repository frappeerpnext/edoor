// Copyright (c) 2023, Tes Pheakdey and contributors
// For license information, please see license.txt

let reservation_status = []
let room_block_color = "red"

frappe.query_reports["Monthly Availability Chart"] = {
	onload: function (report) {

		frappe.db.get_list("Reservation Status", { fields: ["name", "alias", "color"] }).then((r) => {

			reservation_status = r


		})

		frappe.db.get_single_value("eDoor Setting", "room_block_color").then(r => {
			room_block_color = r
		})
		report.page.add_inner_button("Preview Report", function () {
			frappe.query_report.refresh();
		});
		setLinkField()

	},
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
			default: frappe.datetime.get_today(),
			"reqd": 1,
			"on_change": function (query_report) { }
		},
		{
			"fieldname": "end_date",
			"label": __("End Date"),
			"fieldtype": "Date",
			default: frappe.datetime.get_today(),
			"reqd": 1,
			"on_change": function (query_report) { }
		},

		{
			"fieldname": "room_name_types",
			"label": __("Room Type"),
			"fieldtype": "MultiSelectList",
			get_data: function (txt) {
				return frappe.db.get_link_options('Room Type', txt);
			},
			"on_change": function (query_report) { }
		},
		{
			"fieldname": "chart_type",
			"label": __("Chart Type"),
			"fieldtype": "Select",
			"options": "None\nbar\nline\npie",
			hide_in_filter: 1,
			"on_change": function (query_report) { }
		},
		{
			"fieldname": "chart_option",
			"label": __("Chart Option"),
			"fieldtype": "Select",
			"options": "\nOccupancy by Month\nRoom Type\nRoom",
			hide_in_filter: 1,
			"on_change": function (query_report) { }
		},

	]
	,
	"formatter": function (value, row, column, data, default_formatter) {
		
		const origninal_value = value || 0
		value = default_formatter(value, row, column, data);

		if (
			(column.fieldtype || "") == "Int" ||
			((column.fieldtype || "") == "Percent") ||
			((column.fieldtype || "") == "Currency")
		) {
			if (origninal_value == 0) {
				return "<div style='text-align:" + (column.align || "left") + ";'>-</div>"
			}
		}



		if (data.indent == 2 && column.is_date == 1) {
			if (value) {
				let status = reservation_status.filter(r => r.alias == value)
				console.log(status)
				let color = ""
				if (status.length > 0) {
					color = status[0].color

				} else {
					color = room_block_color
				}

				value = $(`<span>${value}</span>`);
				var $value = $(value).css("background", color)
					.css("height", "28px")
					.css("width", "50px")
					.css("display", "block")
					.css("margin-top", "-5px")
					.css("margin-left", "-6px")
					.css("text-align", "center")
					.css("vertical-align", "middle");

				value = $value.wrap("<p></p>").parent().html();



			}

		}





		return value;
	},

};
function setLinkField() {
	const property = frappe.query_report.get_filter_value("property")
	if (property) {
		const room_type_filter = frappe.query_report.get_filter('room_name_types');
		room_type_filter.df.get_query = function () {
			return {
				filters: {
					"property": property
				}
			};
		};

	}

}
