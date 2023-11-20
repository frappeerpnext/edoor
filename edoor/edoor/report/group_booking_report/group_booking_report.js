// Copyright (c) 2023, Tes Pheakdey and contributors
// For license information, please see license.txt

frappe.query_reports["Group Booking Report"] = {
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
			"fieldname": "summary_filter",
			"label": __("Summary By"),
			"fieldtype": "Autocomplete",
			// "options": "\nArrival Date\nDeparture Date\nReservation Date\nReservation\nReservation Stay\nGuest\nReservation Type\nRoom Type\nBusiness Source\nBusiness Source Type\nNationality\nRate Type\nReservation Status",
			get_data:function(txt) {
				return [
					{"value":"arrival_date","description":"Arrival Date","fieldtype":"Date","width":250},
					{"value":"departure_date","description":"Departure Date","fieldtype":"Date","width":250},
					{"value":"reservation_date","description":"Reservation Date" ,"fieldtype":"Date","width":250},
					{"value":"business_source","description":"Business Source","fieldtype":"Data","width":250},
					{"value":"business_source_type","description":"Business Source Type","fieldtype":"Data","width":250},
					{"value":"nationality","description":"Nationality","fieldtype":"Data","width":250},
					{"value":"reservation","description":"Reservation","fieldtype":"Data","width":250},
					{"value":"reservation_type","description":"Reservation Type","fieldtype":"Data","width":250},
					{"value":"room_type","description":"Room Type","fieldtype":"Data","width":250},
					{"value":"guest","description":"Guest","fieldtype":"Data","width":250},
					{"value":"rate_type","description":"Rate Type","fieldtype":"Data","width":250},
					{"value":"reservation_status","description":"Reservation Status","fieldtype":"Data","width":250},
				]
			},
			hide_in_filter:1
		},
		{
			"fieldname": "summary_fields",
			"label": __("Summary Field"),
			"fieldtype": "MultiSelectList",
			get_data: function(txt) {
				return [
					{"value":"total_record","description":"Total Room",name:"Total Room",fieldtype:"Int", width:100,align:"center"},
					{"value":"room_nights","description":"Room Nights",name:"Room Nights",fieldtype:"Int", width:100,align:"center"},
					{"value":"adult","description":"Adult",fieldtype:"Int",name:"Adult", width:100,align:"center"},
					{"value":"child","description":"Child",name:"Child",fieldtype:"Int", width:100,align:"center"},
					{"value":"total_debit","description":"Total Debit",name:"Total Debit",fieldtype:"Currency", width:100,align:"right"},
					{"value":"total_credit","description":"Total Credit",name:"Total Credit",fieldtype:"Currency", width:100 ,align:"right"},
					{"value":"balance","description":"Balance",name:"Balance",fieldtype:"Currency", width:100,align:"right"},
				]
			},
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
			"fieldname": "chart_type",
			"label": __("Chart Type"),
			"fieldtype": "Select",
			"options": "None\nbar\nline\npie",
			hide_in_filter:1
		},
		{
			"fieldname": "view_chart_by",
			"label": __("View Chart By"),
			"fieldtype": "Select",
			"options": "\nArrival Date\nDeparture Date\nReservation Date\nReservation\nGuest\nReservation Type\nRoom Type\nBusiness Source\nBusiness Source Type\nNationality\nRate Type\nReservation Status",
			hide_in_filter:1
		},
		{
			"fieldname": "chart_series",
			"label": __("Chart Series"),
			"fieldtype": "MultiSelectList",
			get_data: function(txt) {
				return [
					{"value":"Total Debit","description":"Total Debit",fieldtype:"Currency","precision":2},
					{"value":"Total Credit","description":"Total Credit",fieldtype:"Currency","precision":2},
					{"value":"Balance","description":"Balance",fieldtype:"Currency","precision":2},
					{"value":"Adult","description":"Adult",fieldtype:"Int"},
					{"value":"Child","description":"Child",fieldtype:"Int"},
					{"value":"Pax","description":"Pax",fieldtype:"Int"},
					{"value":"Room Nights","description":"Room Nights",fieldtype:"Int"},
				]
			},
			hide_in_filter:1
		},
		
		
		{
			"fieldname": "order_by",
			"label": __("Order By"),
			"fieldtype": "Select",
			"options": "Last Update On\nCreated On\nReservation\nReservation Stay\nArrival Date\nDeparture Date\nBusiness Source\nRoom Type\nReservation Status",
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
			"fieldname": "show_summary",
			"label": __("Show Summary"),
			"fieldtype": "Check",
			default:true,
			hide_in_filter:1
		},

	],
};
