
import { FrappeApp } from 'frappe-js-sdk';
const frappe = new FrappeApp();
const db = frappe.db();


export default class ReservationStay {
	constructor() {
		this.stay ={}
		this.reservationStay = {}	
		this.guest= {}	
		this.masterGuest = {}	
		this.reservation = {}	
	}	

	LoadReservationStay(name) {
		
		
	}
}