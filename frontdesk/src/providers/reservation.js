
import { getApi, ref,computed } from '@/plugin';

export default class Reservation {
	constructor() {
		this.loading = false
		this.reservationStays = []
		this.reservation = {}
		this.masterGuest = {}
		this.roomList = []
		this.selecteds = []
		this.reservationSummary = ref([])
		this.depositTransactions =[]
		this.selecteddepositTransactions =[]
	}

	LoadReservation(name, showLoading = true) {
		this.loading = showLoading
		this.selecteds = []
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
				const data = this.reservationStays.filter(r => r.reservation_status == f.name)
				if (data.length > 0) {
					data.forEach((d) => {
						list.push(d)
					})
				}

			});
			this.roomList = list;
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
				getApi("reservation.get_folio_transaction",{"reservation":name,account_category:"Deposit"})
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

	


		clear(){
			this.loading = false
			this.reservationStays = []
			this.reservation = {}
			this.masterGuest = {}
			this.reservationSummary.value = []
			this.depositTransaction = []
		}
	}