 
import NumberFormat from 'number-format.js'
import moment from "../utils/moment.js";
export default class Gv {
	constructor() {
		this.setting = {}
		this.countries = []
		this.loading = false 
		this.cashier_shift={}		
	}

	handleServerMessage(message){ 
		const frappe = inject('$frappe')
		console.log(frappe)
	}
	showErrorMessage(error){ 
	 
		const _server_messages = JSON.parse(error._server_messages)
 
		if (_server_messages){
			let messages = []
			_server_messages.forEach(r => {
				messages.push(JSON.parse(r).message)
			});
			
			const message = messages.join("<br/>")
			window.postMessage('show_alert|' + message, '*')
		}
		
		
		
		
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
	timeFormat(datetime) { 
		return moment(datetime, "HH:mm:ss").format("h:mm A")
	}
	dateApiFormat(date){
		return moment(date).format("yyyy-MM-DD")
	}
	getRateBeforeTax(amount, tax_rule, tax_1_rate, tax_2_rate, tax_3_rate){
		amount=amount || 0
	 
		const t1_r = (tax_1_rate || 0) / 100
		const t2_r = (tax_2_rate ||  0)  / 100
		const t3_r = (tax_3_rate || 0)  / 100
		
		let tax_1_amount = 0
		let tax_2_amount = 0
		let tax_3_amount = 0
		let price = 0

		let t1_af_disc = tax_rule.calculate_tax_1_after_discount
		let t2_af_disc = tax_rule.calculate_tax_2_after_discount
		let t2_af_add_t1 = tax_rule.calculate_tax_2_after_adding_tax_1
		let t3_af_disc	= tax_rule.calculate_tax_3_after_discount
		let t3_af_add_t1 =  tax_rule.calculate_tax_3_after_adding_tax_1
		let t3_af_add_t2 =   tax_rule.calculate_tax_3_after_adding_tax_2


		let tax_rate_con = 0
 

		tax_rate_con = (1 + t1_r + t2_r 
							+ (t1_r * t2_af_add_t1 * t2_r) 
							+ t3_r + (t1_r * t3_af_add_t1 * t3_r) 
							+ (t2_r * t3_af_add_t2 * t3_r)
							+ (t1_r * t2_af_add_t1 * t2_r * t3_af_add_t2 * t3_r))


    
		tax_rate_con = tax_rate_con || 0

		price = amount /  tax_rate_con
		 
		return  price
	 
	}
}