import { FrappeApp } from 'frappe-js-sdk'; 
import { getApi,postApi } from '@/plugin';
import moment from "../utils/moment";
const frappe = new FrappeApp();
const db = frappe.db();
export default class Housekeeping {
constructor() {
	this.view_type ="table"//table, kanban
	this.room_list = [] 
	this.selectedRooms = []
	this.selectredRow = {}
	this.reservationStay = {}
	this.loading = false
	this.property = JSON.parse(localStorage.getItem("edoor_property"))
	this.moment = moment
	this.filter = {}
	this.room_block = undefined
	this.pageState = {
		order_by: "modified", 
		order_type: "desc", 
		page: 0, 
		rows: 20, 
		totalRecords: 0, 
		activePage: 0
	}
}
 
loadData(show_loading=true) {
	this.loading = show_loading
	return new Promise((resolve, reject) => {
		let filters = JSON.parse(JSON.stringify(this.filter))
		if(filters.selected_date){
			filters.selected_date = this.moment(filters.selected_date).format("yyyy-MM-DD")
		}

		postApi("housekeeping.get_room_list",{
            filter: {
				'date': filters.selected_date || '',
				'property':this.property.name,
				'room_type_id':filters.selected_room_type || [],
				'housekeeping_status':filters.selected_housekeeping_status || [],
				'building':filters.selected_building || '',
				'floor':filters.selected_floor || '',
				'room_type_group':filters.selected_room_type_group || '',
				'housekeeper':filters.selected_housekeeper || '',
				'keyword':filters.keyword || '',
			}
		},"",false)
			.then((result) => {
                this.room_list = result.message
				this.pageState.totalRecords = result.message.length
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

