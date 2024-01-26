// Copyright (c) 2024, Tes Pheakdey and contributors
// For license information, please see license.txt

frappe.query_reports["Housekeeping Room Status Report"] = {
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
			"fieldname": "room_types",
			"label": __("Room Type"),
			"fieldtype": "MultiSelectList",
			get_data: function(txt) {
				return frappe.db.get_link_options('Room Type', txt);
			},
		},
		{
			"fieldname": "building",
			"label": __("Building"),
			"fieldtype": "MultiSelectList",
			get_data: function(txt) {
				return frappe.db.get_link_options('Building', txt);
			},
		},
		{
			"fieldname": "floor",
			"label": __("Floor"),
			"fieldtype": "MultiSelectList",
			get_data: function(txt) {
				return frappe.db.get_link_options('Floor', txt);
			},
		},
		{
			"fieldname": "housekeeper",
			"label": __("Housekeeper"),
			"fieldtype": "MultiSelectList",
			get_data: function(txt) {
				return frappe.db.get_link_options('Housekeeper', txt);
			},
		},
		{
			"fieldname": "housekeeping_status",
			"label": __("Housekeeping Status"),
			"fieldtype": "MultiSelectList",
			get_data: function(txt) {
				return frappe.db.get_link_options('Housekeeping Status', txt);
			},
		},
		{
			"fieldname": "order_by",
			"label": __("Order By"),
			"fieldtype": "Select",
			"options": "Last Update On\nCreated On\nReservation\nReservation Stay\nArrival Date\nDeparture Date\nBusiness Source\nRoom Type\nReservation Status",
			default:"Last Update On",
			hide_in_filter:1,
			"on_change": function (query_report) {},
		},
		{
			"fieldname": "sort_order",
			"label": __("Sort Order"),
			"fieldtype": "Select",
			"options": "ASC\nDESC",
			default:"ASC",
			hide_in_filter:1,
			"on_change": function (query_report) {},
		},
		{
			"fieldname": "show_summary",
			"label": __("Show Summary"),
			"fieldtype": "Check",
			default:true,
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
	"formatter": function(value, row, column, data, default_formatter) {
		
		value = default_formatter(value, row, column, data);
		var parser = new DOMParser(); // create a DOMParser object
		var doc = parser.parseFromString(value, "text/html"); // parse the string into a document object
		var element = doc.querySelector("a"); // get the element by selector
		if (data && data.is_group==1) {
			
 
			if(element){

				value =$(`<span>${element.dataset.value}</span>`);  
			}else {
				
				value = $(`<span>${value}</span>`);
			}
			
			

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

}
