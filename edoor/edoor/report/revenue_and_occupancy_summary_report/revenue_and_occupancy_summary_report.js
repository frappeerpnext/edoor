// Copyright (c) 2023, Tes Pheakdey and contributors
// For license information, please see license.txt
 
frappe.query_reports["Revenue and Occupancy Summary Report"] = {
	"filters": [
		{
			fieldname: "property",
			label: "Property",
			fieldtype: "Link",
			options:"Business Branch",
			default:frappe.defaults.get_user_default("business_branch") ,
			"reqd": 1
		},
		{
			"fieldname":"start_date",
			"label": __("Start Date"),
			"fieldtype": "Date",
			default: new Date( (new Date()).getFullYear(), ( new Date()).getMonth(), 1),
			"reqd": 1
		},
		{
			"fieldname":"end_date",
			"label": __("End Date"),
			"fieldtype": "Date",
			default: new Date((new Date()).getFullYear(), (new Date()).getMonth() + 1, 0),
		
			"reqd": 1
		},
		{
			"fieldname": "customer_group",
			"label": __("Guest Type"),
			"fieldtype": "MultiSelectList",
			get_data: function(txt) {
				return frappe.db.get_link_options('Customer Group', txt);
			}
		},
		{
			"fieldname": "parent_row_group",
			"label": __("Parent Group By"),
			"fieldtype": "Select",
			"options": "\nCategory\nProduct Group\nRevenue Group\nBusiness Branch\nOutlet\nTable Group\nTable\nPOS Profile\nCustomer\nCustomer Group\nStock Location\nDate\n\Month\nYear\nSale Invoice\nWorking Day\nCashier Shift\nSale Type",
			
		},
		{
			"fieldname": "row_group",
			"label": __("Row Group By"),
			"fieldtype": "Select",
			"options": "Date\n\Month\nYear\nReservation Type\nBusiness Source\nRevenue Group\nBusiness Branch\nOutlet\nTable Group\nTable\nPOS Profile\nCustomer\nCustomer Group\nStock Location\nSale Invoice\nWorking Day\nCashier Shift\nSale Type",
			"default":"Date"
		},

		// {
		// 	"fieldname": "column_group",
		// 	"label": __("Column Group By"),
		// 	"fieldtype": "Select",
		// 	"options": "None\nDaily\nWeekly\nMonthly\nQuarterly\nHalf Yearly\nYearly",
		// 	"default":"None"
		// },
		{
			"fieldname": "chart_type",
			"label": __("Chart Type"),
			"fieldtype": "Select",
			"options": "None\nbar\nline\npie",
			"default":"bar",
			hide_in_filter:1
		}

	],
	"formatter": function(value, row, column, data, default_formatter) {
		const origninal_value = value  || 0
		 
		value = default_formatter(value, row, column, data);
		if ((column.fieldtype || "") == "Currency" ) 
		{
			if(origninal_value==0){
				return "<span style='float:right;'>-</span>"
			}
		}else if ((column.fieldtype || "") == "Int" ) 
		{
			if(origninal_value==0){
				return "<span style='float:right;'>-</span>"
			}
		}


		
		if ((data && data.is_group==1)) {
			
			value = $(`<span>${value}</span>`);

			var $value = $(value).css("font-weight", "bold");
			

			value = $value.wrap("<p></p>").parent().html();
		} 
	 
		
		return value;
	},
	
};

 