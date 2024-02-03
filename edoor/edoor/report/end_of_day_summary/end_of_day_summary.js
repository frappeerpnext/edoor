// Copyright (c) 2024, Tes Pheakdey and contributors
// For license information, please see license.txt

frappe.query_reports["End of Day Summary"] = {
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
			"fieldname": "group_by_ledger_name",
			"label": __("Group By Ledger Name"),
			"fieldtype": "Check",
			default:true,
			hide_in_filter:1,
			"on_change": function (query_report) {},
		},
		{
			"fieldname": "show_account_code",
			"label": __("Show Account Code"),
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
		const origninal_value = value || 0
		value = default_formatter(value, row, column, data);
		 

		value = value.toString().replace("style='text-align: right'", "style='text-align: " + column.align + "'");
		if (!value.toString().includes("text-align")){
			value = "<div style='text-align:" + (column.align || "left") + ";'>" + value + "</div>"
		}
		
		if (
			(column.fieldtype || "") == "Int" ||
			((column.fieldtype || "") == "Percent") ||
			((column.fieldtype || "") == "Currency")
		) {
			if (origninal_value == 0) {
				return "<div style='text-align:" + (column.align || "left") + ";'>-</div>"
			}
		}

		var parser = new DOMParser(); // create a DOMParser object
		var doc = parser.parseFromString(value, "text/html"); // parse the string into a document object
		var element = doc.querySelector("a"); // get the element by selector
		if (data && data.indent==0 ) {
			
			if(element){

				value =$(`<span>${element.dataset.value}</span>`);  
			}else {
				
				value = $(`<span>${value}</span>`);
			}
			 
				var $value = $(value).css("font-weight", "bold");
				value = $value.wrap("<p></p>").parent().html();
			 
		
		}else if (data && data.indent==1 ) {
			
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
