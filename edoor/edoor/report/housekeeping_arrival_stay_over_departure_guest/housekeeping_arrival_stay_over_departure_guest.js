// Copyright (c) 2023, Tes Pheakdey and contributors
// For license information, please see license.txt

frappe.query_reports["Housekeeping Arrival Stay Over Departure Guest"] = {
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
			"fieldname": "filter_by",
			"label": __("Filter By"),
			"fieldtype": "Select",
			"options": "Arrival Guest\nStay Over Guest\nDeparture Guest",
			default:"Arrival Guest",
			"on_change": function (query_report) {},
			
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
				return frappe.db.get_link_options('Room Type', txt);
			},
			// get_data: function(txt) {
			// 	return frappe.db.get_link_options('Room Type', txt).then((data) => {
			// 		// Modify the data to include both room_type_id and room_type_name
			// 		return data.map(item => ({ value: item.name, label: item.room_type }));
			// 	});
			// },
			"on_change": function (query_report){}
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
		if (data && data.indent==0) {
			
 
			if(element){

				value =$(`<span>${element.dataset.value}</span>`);  
			}else {
				
				value = $(`<span>${value}</span>`);
			}
			
			

				var $value = $(value).css("font-weight", "bold");
				value = $value.wrap("<p></p>").parent().html();
			 
		
		}else {
			if(column.fieldtype=="Link"){
				
				value = "<a target='_blank' href='" + column.url + "/" + element.getAttribute('data-value') + "'>" + element.getAttribute('data-value') + "</a>";

 
			}
			
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
