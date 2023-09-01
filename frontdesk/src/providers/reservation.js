
import { getApi, ref,computed } from '@/plugin';
import moment from "../utils/moment.js";
export default class Reservation {
	constructor() {
		this.loading = false
		this.reservationStays = []
		this.reservation = {}
		this.masterGuest = {}
		this.roomList = []
		this.filterStatusRooms = []
		this.selecteds = []
		this.reservationSummary = ref([])
		this.depositTransactions =[]
		this.selecteddepositTransactions =[]
		this.room_rates = []
		this.selectedRoomRates = []

	}

	LoadReservation(name, showLoading = true) {
		this.loading = showLoading
		this.selecteds = []
		this.filterStatusRooms = []
		getApi("reservation.get_reservation_detail", {
			name: name || this.reservation?.name
		}).then((result) => {
			this.reservation = result.message.reservation
			this.reservationStays = result.message.reservation_stays
			this.masterGuest = result.message.master_guest
			this.getRoomList()
			this.loading = false
		}).catch((err) => {
			this.loading = false
		})
	}

	getRoomList(filter = null) {
		if (filter && filter.length > 0) {
			var list = []
			filter.forEach(f => {
				const data = ref([])
				if(f.name == 'require_pickup' || f.name == 'require_drop_off'){
					data.value = this.reservationStays.filter(r => r[f.name] == true)
				}else{
					data.value = this.reservationStays.filter(r => r.reservation_status == f.name)
				}
				
				if (data.value.length > 0) {
					data.value.forEach((d) => {
						list.push(d)
					})
				}

			});
			const unique = [...new Set(list.map(item => item.name))];
			var result = []
			unique.forEach(r=>{
				result.push(list.find(l=>l.name == r))
			});
			this.roomList = result
		} else {
			this.roomList = this.reservationStays
		}
	}

	getChargeSummary = async (name = null) => {
		this.loadingSummary = true
		getApi("reservation.get_reservation_charge_summary", {
			reservation: name ?? this.reservation.name
		}).then((result) => {

			this.reservationSummary.value = result.message

		})
	}


	getDepositTransaction(name) {
		const setting = JSON.parse(localStorage.getItem("edoor_setting"))
		if (name) {
			if (setting?.folio_transaction_style_credit_debit == 1) {
				getApi("reservation.get_folio_transaction",{"transaction_number":name,"transaction_type":"Reservation"})
				.then((result)=>{
					this.depositTransactions =result.message
				 
				})
			}
		}
	}

	getDepositBalance(){
		if(this.depositTransactions){
			return this.depositTransactions.reduce((n, d) => n + (d.debit || 0), 0) -  this.depositTransactions.reduce((n, d) => n + (d.credit || 0), 0)
		}
		return 0
	}

	getRoomRate(reservation) {

		getApi('reservation.get_reservation_room_rate', {
			reservation:reservation
		}).then((result) => {
			
			this.room_rates = result.message
			this.room_rates.forEach(r=>r.date_search = moment(r.date).format("DD-MM-YYYY"))
		})

	}



		clear(){
			this.loading = false
			this.reservationStays = []
			this.reservation = {}
			this.masterGuest = {}
			this.reservationSummary.value = []
			this.depositTransaction = []
			this.room_rates = []
			this.selectedRoomRates = []
		}
	}