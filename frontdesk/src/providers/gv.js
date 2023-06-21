 
import NumberFormat from 'number-format.js'
import moment from "../utils/moment.js";
export default class Gv {
	constructor() {
		this.setting = {},
		this.countries = [],
		this.loading = false 
		this.cashier_shift={}		
	}

	handleServerMessage(message){ 
		const frappe = inject('$frappe')
		console.log(frappe)
	}
	showErrorMessage(error){ 
		let exception = error.exception
		

		const replace_text = [
			{text:"frappe.exceptions.ValidationError:",value:""},
			{text:"frappe.exceptions.MandatoryError:",value:"Value required for "},
			{text:"ValueError:",value:"Invalid data input. "},
			{text:"frappe.exceptions.PermissionError: ",value:""},
			
			{text:"_",value:" "},
		]
		let message=exception
		if(exception){
			replace_text.forEach(t => {
				message =message.replaceAll(t.text,t.value) 	

			});
			
		}
		window.postMessage('show_alert|' + message, '*')
		
		
		
	}
	toast(type = 'alert', message){
		window.postMessage(`show_${type == 'warn' ? 'alert' : type}|` + message, '*')
	}
	numberFormat(value){
		return NumberFormat('#,##0.#0',value)
	}
	dateFormat(date) {
		return moment(date).format("DD-MM-YYYY")
	}
	datetimeFormat(datetime) {
		return moment(datetime).format("DD-MM-yy h:mm:ss A")
	}
	dateApiFormat(date){
		return moment(date).format("yyyy-MM-DD")
	}
}