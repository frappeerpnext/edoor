
import { getApi } from '@/plugin';
export default class Reservation {
	constructor() {	
		this.loading = false
		this.reservationStays = []
		this.reservation = {}
		this.masterGuest = {}
	}	

	LoadReservation(name) {
		this.loading = true
		getApi("reservation.get_reservation_detail", {
			name: name
		}).then((result) => {
			this.reservation = result.message.reservation
			this.reservationStays = result.message.reservation_stays
			this.masterGuest = result.message.master_guest
			this.loading = false
		}).catch((err)=>{
			this.loading = false
		})
	}
}