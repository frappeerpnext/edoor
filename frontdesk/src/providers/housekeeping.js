import { inject } from "vue"
import { FrappeApp } from 'frappe-js-sdk';
import {toaster} from "../plugin/toast"
const frappe = new FrappeApp();
const db = frappe.db();

export default class Housekeeping {
	constructor() {
		this.view_type ="table"//table, kanban
		this.room_list = []
		this.filter = {}
		this.selectedRooms = []
		this.selectredRow = {}
		
	}

	loadData() {
		let filters = []
		if (this.filter.selected_room_type && this.filter.selected_room_type.length > 0) {
			filters.push(["room_type_id", 'in', this.filter.selected_room_type])

		}
		
		if (this.filter.selected_housekeeping_status && this.filter.selected_housekeeping_status.length > 0) {
			filters.push(["housekeeping_status", 'in', this.filter.selected_housekeeping_status])
		}

		
		if (this.filter.selected_building && this.filter.selected_building.length > 0) {
			filters.push(["building", 'in', this.filter.selected_building])
		}

		if (this.filter.selected_floor && this.filter.selected_floor.length > 0) {
			filters.push(["floor", 'in', this.filter.selected_floor])
		}

		if (this.filter.selected_room_type_group && this.filter.selected_room_type_group.length > 0) {
			filters.push(["room_type_group", 'in', this.filter.selected_room_type_group])
		}

		if (this.filter.selected_housekeeper && this.filter.selected_housekeeper.length > 0) {
			filters.push(["housekeeper", 'in', this.filter.selected_housekeeper])
		}

		db.getDocList('Room', {
			fields: ['name', "room_type_id", "room_type", "room_number", "housekeeping_status", "status_color", "housekeeper"],
			filters: filters,
			limit: 1000,
		})
			.then((docs) => {
				 
				this.room_list =  docs
				console.log(this.room_list)
			}
			)
			.catch((error) => console.error(error));

	}

	updateRoomStatus(room_name, status_name){
		db.updateDoc('Room', room_name, {
			housekeeping_status: status_name,
		  })
		.then((doc) => { 
			this.loadData()
			toaster('success','Updated Successful')
		})
		.catch((error) => console.error(error));
	}
}
