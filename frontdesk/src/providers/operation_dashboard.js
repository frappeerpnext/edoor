import { getApi } from '@/plugin';
export default class OperationDashboard {
constructor() {
	this.page_title = "Operation Dashboard"
	this.current_date= new Date()
	this.refresh_token= ""//we use this to raise refresh to current page using this layout
	this.loading = false
	this.all_reservation_data = {
		date:new Date(),
		data:[]
	},
	this.current_route = ""
}

 
  
}

