// Copyright (c) 2023, Tes Pheakdey and contributors
// For license information, please see license.txt

frappe.query_reports["Reservation List Report"] = {
	// "onload": function(frm) {
	// 	frm.page.add_inner_button(__("Print"), function() {
	// 		let dialog = frappe.ui.get_print_settings(
	// 			false,
	// 			(print_settings) => this.print_report(print_settings),
	// 			"Default Letter Head",
	// 			this.get_visible_columns()
	// 		);
	// 		this.add_portrait_warning(dialog);
	// 	});
	// },
	"filters": [
		{
			"fieldname": "filter_date_by",
			"label": __("Filter Date By"),
			"fieldtype": "Select",
			"options": "Arrival Date\nDeparture Date\nReservation\nStay Date",
			default:"Arrival Date",
			
		},
		{
			"fieldname":"start_date",
			"label": __("Start Date"),
			"fieldtype": "Date",
			default:frappe.datetime.get_today(),
			"reqd": 1
		},
		{
			"fieldname":"end_date",
			"label": __("End Date"),
			"fieldtype": "Date",
			default:frappe.datetime.get_today(),
			"reqd": 1
		},
		{
			"fieldname": "property",
			"label": __("Property"),
			"fieldtype": "Link",
			"options":"Business Branch",
			"reqd": 1
			
		} ,
		{
			"fieldname": "reservation",
			"label": __("Reservation"),
			"fieldtype": "Link",
			"options":"Reservation",
		} ,
		{
			"fieldname": "reservation_type",
			"label": __("Reservation Type"),
			"fieldtype": "Select",
			"options":"\nFIT\nGIT",
		} ,
		 
		{
			"fieldname": "business_source",
			"label": __("Business Source"),
			"fieldtype": "Link",
			"options":"Business Source",
		} ,
		{
			"fieldname": "guest",
			"label": __("Guest"),
			"fieldtype": "Link",
			"options":"Customer",
			
		}, 
		{
			"fieldname": "reservation_status",
			"label": __("Reservation Status"),
			"fieldtype": "MultiSelectList",
			get_data: function(txt) {
				return frappe.db.get_link_options('Reservation Status', txt);
			},
	
			
		},
		{
			"fieldname": "group_by",
			"label": __("Group By"),
			"fieldtype": "Select",
			"options": "\nArrival Date\nDeparture Date\nReservation Date\nReservation\nGuest\nReservation Type\nRoom Type\nBusiness Source\nBusiness Source Type\nNationality\nRate Type\nReservation Status",
			hide_in_filter:1
 
		},
		{
			"fieldname": "chart_type",
			"label": __("Chart Type"),
			"fieldtype": "Select",
			"options": "None\nbar\nline\npie",
			"default":"bar",
			hide_in_filter:1
		},
		{
			"fieldname": "is_active_reservation",
			"label": __("Is Active Reservation"),
			"fieldtype": "Check",
			default:true,
			hide_in_filter:1
		},
		{
			"fieldname": "order_by",
			"label": __("Order By"),
			"fieldtype": "Select",
			"options": "Last Update On\nCreated On\nReservation\nReservation Stay\nArrival Date\nDeparture Date\nRoom Type\nReservation Status",
			default:"Last Update On",
			hide_in_filter:1
		},
		{
			"fieldname": "sort_order",
			"label": __("Sort Order"),
			"fieldtype": "Select",
			"options": "ASC\nDESC",
			default:"ASC",
			hide_in_filter:1
		},
		{
			"fieldname": "summary_filter",
			"label": __("Summary By"),
			"fieldtype": "Select",
			"options": "\nArrival Date\nDeparture Date\nReservation Date\nReservation\nReservation Stay\nGuest\nReservation Type\nRoom Type\nBusiness Source\nBusiness Source Type\nNationality\nRate Type\nReservation Status",
			hide_in_filter:1
		},

	],
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
 