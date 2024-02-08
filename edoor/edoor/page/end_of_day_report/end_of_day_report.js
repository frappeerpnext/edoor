
frappe.pages['end-of-day-report'].on_page_load = function(wrapper) {
	new MyPage(wrapper);
}

MyPage = Class.extend({
	init: function(wrapper) {
		this.page = frappe.ui.make_app_page({
			parent: wrapper,
			title: 'End of Day Report',
			single_column: true
		});
		this.make();
		this.print = this.page.set_primary_action('Print', () => this.onPrint(), 'octicon octicon-plus')
		this.page.set_secondary_action('View Report', () => this.onViewReport(), 'octicon octicon-plus')
		
		this.property = this.page.add_field({
			label: 'Property',
			fieldtype: 'Link',
			fieldname: 'property',
			options:"Business Branch",
			change() {
				
				 alert(123)
			}
		});
		this.date = this.page.add_field({
			label: 'Date',
			fieldtype: 'Date',
			fieldname: 'date',
			options:"Date",
			change() {
				
				alert(123)
		   }
		});
		this.report_name = this.page.add_field({
			label: 'Report Name',
			fieldtype: 'Select',
			fieldname: 'report_name',
			options: [
				'End of Day Detail',
				'End of Day Summary',
			],
			
		});
		this.iframe = document.querySelector("#iframe_end_of_day_report")
		
		this.iframe.addEventListener('load', function() { 
			const iframe_report = document.querySelector("#iframe_end_of_day_report")
			iframe_report.style.height = iframe_report.contentWindow.document.body.scrollHeight + 'px';
		});
	},
	make: function() {
		$(frappe.render_template("end_of_day_report", this)).appendTo(this.page.main);
	},onViewReport:function(){
		let newUrl;
		if (this.report_name.get_value()=="End of Day Detail"){
			newUrl = "/printview?doctype=Business%20Branch&name=ESTC%20HOTEL&format=eDoor%20Working%20Day%20Transaction%20Detail%20Report&&settings=%7B%7D&show_toolbar=0&start_date=2024-01-31&group_by_ledger_type=1&show_account_code=1&_lang=en&refresh=2.886933436472656"
			this.iframe.src = newUrl;
		}else if (this.report_name.get_value()=="End of Day Summary"){
			newUrl = "/printview?doctype=Business%20Branch&name=ESTC%20HOTEL&format=eDoor%20Working%20Day%20Transaction%20Summary%20Report&&settings=%7B%7D&show_toolbar=0&start_date=2024-01-31&group_by_ledger_type=1&show_account_code=1&_lang=en&refresh=2.886933436472656"
			this.iframe.src = newUrl;
		}else{
			this.report_name = "End of Day Detail"
			this.iframe.src = this.iframe.src + "&refresh=" + (Math.random() * 16)
		}
		
		//const serverUrl = window.location.protocol + "//" + window.location.hostname + ":" + window.setting.backend_port;
		
		// iframe.contentWindow.location.replace(url.value)
	},
	onPrint: function(){
		alert("u print me!!")
	}
})


// frappe.pages['end-of-day-report'].on_page_load = function(wrapper) {
// 	var page = frappe.ui.make_app_page({
// 		parent: wrapper,
// 		title: 'End of Day Report',
// 		single_column: true
// 	});
// 	let filters={}
// 	let $btnViewReport = page.set_secondary_action('View Report', () => onViewReport(), 'octicon octicon-plus')
// 	let $btnPrintReport = page.set_primary_action('Print', () => onPrintReport(), 'octicon octicon-printer')




// 	function onViewReport(){
// 		alert(filters.property)
// 	}
	

// 	function onPrintReport(){
// 		alert(123)
// 	}


// }