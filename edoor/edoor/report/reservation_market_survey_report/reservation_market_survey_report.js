frappe.query_reports["Reservation Market Survey Report"] = {

   "filters": [
    {
        fieldname: "property",
        label: "Property",
        fieldtype: "Link",
        options: "Business Branch",
        default: frappe.defaults.get_user_default("business_branch"),
        reqd: 1,
        on_change: function (query_report) {
            setLinkField();
        },
    },
    {
        fieldname: "chart_type",
        label: __("Chart Type"),
        fieldtype: "Select",
        options: "\ndonut\nbar\nline\npie",
        default: "donut", 
        reqd: 1, 
        on_change: function(query_report) {
            query_report.refresh();
        }
    },    
    {
        fieldname: "view_by",
        label: __("View By"),
        fieldtype: "Select",
        options: "\nHow do you find us?\nPurpose of Visit",
        default: "How do you find us?",
        reqd: 1,
        on_change: function(query_report) {
            query_report.refresh();
        }
    },
	{
		fieldname: "start_arrival_date",
		label: __("Start Arrival Date"),
		fieldtype: "Date",
		reqd: 0,
		default: frappe.datetime.add_months(frappe.datetime.now_date(), -1),
		on_change: function(query_report) {
			query_report.refresh();
		}
	},
	{
		fieldname: "end_arrival_date",
		label: __("End Arrival Date"),
		fieldtype: "Date",
		reqd: 0,
		default: frappe.datetime.now_date(),
		on_change: function(query_report) {
			query_report.refresh();
		}
	}
]
,
onload: function(report) {
	report.page.add_inner_button ("Preview Report", function () {
		frappe.query_report.refresh();
	});
	setLinkField()
}
,

	"formatter": function(value, row, column, data, default_formatter) {
        value = default_formatter(value, row, column, data);
        if (data && data.reservation_name === "Total") {
            return `<div style="font-weight: bold;">${value}</div>`;
        }

        return value;
    }
};
