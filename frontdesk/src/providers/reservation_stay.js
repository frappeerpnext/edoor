
import { FrappeApp } from 'frappe-js-sdk';
import { ref,useRouter } from '@/plugin';
const frappe = new FrappeApp();
const db = frappe.db();
const call = frappe.call();
const router = useRouter()

export default class ReservationStay {
	constructor() {
		this.loading = ref(false)
		this.stay = {}
		this.reservationStay = ref({})
		this.guest = ref({})
		this.masterGuest = ref({})
		this.reservation = ref({})
		this.reservationStayNames = ref([])
	}


	getReservationDetail = async (name) => {

		this.loading.value = true

		call.get("edoor.api.reservation.get_reservation_stay_detail", {
			name: name
		}).then((result) => {

			this.reservation.value = result.message.reservation
			this.reservationStay.value = result.message.reservation_stay
			this.reservationStayNames.value = result.message.reservation_stay_names
			this.guest.value = result.message.guest
			this.masterGuest.value = result.message.master_guest
			this.loading.value = false

		}).catch((error) => {
			this.loading.value = false
		})

	}


	getStayName(current_name, isNext=1){
		const current_index = this.reservationStayNames.indexOf(current_name)
		const new_index = current_index + isNext
		 
		if(new_index== this.reservationStayNames.length || new_index<0 ){
			return null
		}else {
			return  this.reservationStayNames[new_index]
		}
	}

	canNavigateNext(name){
	 
		 return !(this.reservationStayNames.indexOf(name) < this.reservationStayNames.length -1 &&  this.reservationStayNames.length>1)
	 
	}
	
	canNavigatePrevious(name){
		return !(this.reservationStayNames.indexOf(name) >0 &&  this.reservationStayNames.length>1)
	}





}