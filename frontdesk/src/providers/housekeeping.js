import { FrappeApp } from 'frappe-js-sdk'; 
import { getApi,postApi } from '@/plugin';
import moment from "../utils/moment";
const frappe = new FrappeApp();
const db = frappe.db();
export default class Housekeeping {
constructor() {
	this.view_type ="table"//table, kanban
	this.room_list = []
	this.filter = {}
	this.selectedRooms = []
	this.selectredRow = {}
	this.reservationStay = {}
	this.loading = false
	this.property = JSON.parse(localStorage.getItem("edoor_property"))
	this.moment = moment
}
 
loadData(show_loading=true) {
	this.loading = show_loading
	return new Promise((resolve, reject) => {
		if(this.filter.selected_date){
			this.filter.selected_date = this.moment(this.filter.selected_date).format("yyyy-MM-DD")
		}

		postApi("housekeeping.get_room_list",{
            filter: {
				'date': this.filter.selected_date || '',
				'property':this.property.name,
				'room_type_id':this.filter.selected_room_type || [],
				'housekeeping_status':this.filter.selected_housekeeping_status || [],
				'building':this.filter.selected_building || '',
				'floor':this.filter.selected_floor,
				'room_type_group':this.filter.selected_room_type_group,
				'housekeeper':this.filter.selected_housekeeper,
				'keyword':this.filter.keyword || ''
			}
		},"",false)
			.then((result) => {
                this.room_list =  result.message
                this.loading = false
                resolve(result)
            }
        )
        .catch((error) => {
            this.loading = false
            reject(error)
        });
		
	});
}

updateRoomStatus(room_name, status_name){
	db.updateDoc('Room', room_name, {
		housekeeping_status: status_name,
		})
	.then((doc) => { 
		this.loadData() 
	})
	.catch((error) => console.error(error));
}
}

