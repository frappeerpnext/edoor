import { inject } from "vue"
export default class Gv {
	constructor() {
		this.setting = {},
		this.countries = [],
		this.loading = false 
	}

	handleServerMessage(message){ 
		const frappe = inject('$frappe')
		console.log(frappe)
	}
}