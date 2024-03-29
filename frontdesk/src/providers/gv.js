 
import NumberFormat from 'number-format.js'
import moment from "../utils/moment.js";
import {ref} from 'vue'
export default class Gv {
	constructor() {
		this.setting = {}
		this.countries = []
		this.loading = false 
		this.cashier_shift={}
		this.working_day = {}		
	}

	handleServerMessage(message){ 
		const frappe = inject('$frappe')
 
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
		return NumberFormat('#,##0.#0',value || 0)
	}
	currencyFormat(value){
		const currencyDefualt = {pos_currency_format : '$ #,###,##0.00', precision: 2}
		const currency = ref()
		if (this.setting.currency && this.setting.currency.pos_currency_format){
			currency.value = this.setting.currency
		}
		else{
			currency.value = currencyDefualt

		}
		const result = ref(0)
		if ((typeof value) == 'number') {
			result.value =   Number(value.toFixed(currency.value.precision));
		} 
		return NumberFormat(currency.value.pos_currency_format, result.value)
		 
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
	keyword(keyword){
		if(keyword){
			let replaced = keyword.replace(/[+`"|\\'\[\]\(\)%\{\}\-*;,^=/]/g, " ")
			return replaced.trim().split(/[\s,\t,\n]+/).join(' ')
		}
		return ""
	}
	isNotEmpty(obj, except_properties = '', except_object= {}){
		 
		var notEmpty = 0
		if(Object.keys(obj).length > 0){ 
			Object.entries(obj).forEach(([key, value]) => {
				if(except_object[key] != value){
					if((!except_properties.split(',').filter(r=>r == key).length > 0) && (value != '' && value != undefined && value != null && String(value) != '{}' && String(value) != '[]')){
						notEmpty ++;
					}
				}
				
			});
		}
		
		return notEmpty > 0;
		
	}
	search(data=[], keyword='', properties){
		if(data.length > 0 && !properties){
			properties = String(Object.keys(data[0]))
		}
		return data.filter(function(r){
			var value = ''
			properties.trim().split(',').forEach(p => {
				value = value + String(r[p] || '') + ' '
			}); 
			return value.toLowerCase().includes((keyword).toLowerCase()) || ""
		})
	}
	getCustomPrintFormat(name){
		 
		const setting = JSON.parse(  localStorage.getItem("edoor_setting"))
		if(setting?.custom_print_format){
			const custom = setting?.custom_print_format?.filter(r=>r.name==name)
		 
			if(custom && custom.length>0){
				return  encodeURIComponent( custom[0].print_format)
			}
		}
	
		return encodeURIComponent(name) 
	}

	generateGuid() {
		return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
		  var r = Math.random() * 16 | 0,
			  v = c === 'x' ? r : (r & 0x3 | 0x8);
		  return v.toString(16);
		});
	  }
	  
}