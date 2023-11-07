// Copyright (c) 2023, Tes Pheakdey and contributors
// For license information, please see license.txt

let reservation_status = []
let room_block_color="red"

frappe.query_reports["Monthly Availability Chart"] = {
	onload:function(frm){
		frappe.db.get_list("Reservation Status",{fields:["name","alias","color"]}).then((r)=>{
			reservation_status = r
			
		})

		frappe.db.get_single_value("eDoor Setting","room_block_color").then(r=>{
			room_block_color = r
		})
	},
	"filters": [
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
			"fieldname": "room_type",
			"label": __("Room Type"),
			"fieldtype": "MultiSelectList",
			get_data: function(txt) {
				return frappe.db.get_link_options('Room Type', txt);
			},
			
		},
		{
			"fieldname": "chart_type",
			"label": __("Chart Type"),
			"fieldtype": "Select",
			"options": "None\nbar\nline\npie",
			hide_in_filter:1
		},
		{
			"fieldname": "chart_option",
			"label": __("Chart Option"),
			"fieldtype": "Select",
			"options": "\nOccpancy By Month\nDate\nRoom Type\nRoom",
			hide_in_filter:1
		},
	]
	,
	"formatter": function(value, row, column, data, default_formatter) {
 
	value = default_formatter(value, row, column, data);
	
		if(data.indent==2 && column.is_date==1){
			if(value){
				let status = reservation_status.filter(r=>r.alias==value)
				
				let color = ""
				if (status.length>0){
					color = status[0].color
					
				}else {
					color = room_block_color
				}

				value = $(`<span>${value}</span>`);
				var $value = $(value).css("background",color)
				.css("height", "28px")
				.css("width","50px")
				.css("display","block")
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
