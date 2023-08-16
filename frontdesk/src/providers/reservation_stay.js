import Enumerable from 'linq'
import { FrappeApp } from 'frappe-js-sdk';
import { ref, computed, useRouter } from '@/plugin';
import moment from '@/utils/moment.js';
const frappe = new FrappeApp();
const db = frappe.db();
const call = frappe.call();
const router = useRouter()


export default class ReservationStay {
	constructor() {
		this.loading = ref(false)
		this.loadingSummary = ref(false)
		this.stay = {}
		this.reservationStay = ref({})
		this.guest = ref({})
		this.masterGuest = ref({})
		this.reservation = ref({})
		this.reservationStayNames = ref([])
		this.stay_summary = ref([])
		this.folios = ref([])
		this.selectedFolio = ref({})
		this.folioTransactions = ref([])
		this.selectedFolioTransactions = ref([])
		this.selectedRoomRates =[]
		this.reservationStatusDelete = ['No Show', 'Void', 'Cancelled']
		this.folio_summary = ref([])
		this.room_rates = ref([])
		this.is_page = false

	}

	getReservationDetail = async (name, showLoading=true) => {
		this.loading.value = showLoading

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

	getReservationStay(name) {


		db.getDoc("Reservation Stay", name).
			then((doc) => {
				this.reservationStay = doc


			})

	}


	getChargeSummary = async (name) => {
		this.loadingSummary = true
		call.get("edoor.api.reservation.get_reservation_charge_summary", {
			reservation_stay: name
		}).then((result) => {

			this.stay_summary.value = result.message
			this.loadingSummary = false
		}).
			catch((error) => {
				this.loadingSummary = false
				throw new Error(error.exception || error.message)
			})
	}


	getStayName(current_name, isNext = 1) {
		const current_index = this.reservationStayNames.indexOf(current_name)
		const new_index = current_index + isNext

		if (new_index == this.reservationStayNames.length || new_index < 0) {
			return null
		} else {
			return this.reservationStayNames[new_index]
		}
	}

	canNavigateNext(name) {

		return !(this.reservationStayNames.indexOf(name) < this.reservationStayNames.length - 1 && this.reservationStayNames.length > 1)

	}

	canNavigatePrevious(name) {
		return !(this.reservationStayNames.indexOf(name) > 0 && this.reservationStayNames.length > 1)
	}

	totalCredit = computed(() => {
		const setting = JSON.parse(localStorage.getItem("edoor_setting"))

		if (this.folioTransactions.value) {
			if (setting.folio_transaction_style_credit_debit == 1) {
				return this.folioTransactions.value.reduce((n, d) => n + (d.credit || 0), 0)
			} else {
				return this.folioTransactions.value.reduce((n, d) => n + (d.type == "Credit" ? Math.abs((d.amount || 0)) : 0), 0)
			}
		}
		return 0

	})

	totalDebit = computed(() => {
		const setting = JSON.parse(localStorage.getItem("edoor_setting"))

		if (this.folioTransactions.value) {
			if (setting.folio_transaction_style_credit_debit == 1) {
				return this.folioTransactions.value.reduce((n, d) => n + (d.debit || 0), 0)
			} else {
				return Math.abs(this.folioTransactions.value.reduce((n, d) => n + (d.type == "Debit" ? (d.amount || 0) : 0), 0))
			}



		}
		return 0

	})


	onLoadReservationFolios(reservation_stay = null) {
	
		
		return new Promise((resolve, reject) => {
			db.getDocList('Reservation Folio', {
				fields: ["name", "status", "is_master", "rooms", "note", "room_types", "guest", "guest_name", "phone_number", "email", "photo", "status", "balance"],
				filters: [['reservation_stay', '=', reservation_stay ? reservation_stay : this.reservationStay?.name]],
				limit: 1000
			})
				.then((doc) => {
					this.folios = doc
					resolve(doc)

				}).catch((err) => {
					reject(err)
				})
		});
	}


	onLoadFolioTransaction(data) {
		const setting = JSON.parse(localStorage.getItem("edoor_setting"))
		if (data?.name) {

			if (setting?.folio_transaction_style_credit_debit == 1) {
				call.get('edoor.api.reservation.get_folio_transaction', {
					transaction_type: "Reservation Folio",
					transaction_number: data.name
				})
					.then((result) => {
						this.folioTransactions = result.message
						// this.selectedFolio.total_credit =this.folioTransactions.reduce((n, d) => n + (d.credit || 0), 0)
						// this.selectedFolio.total_debit =this.folioTransactions.reduce((n, d) => n + (d.debit || 0), 0)
						// this.selectedFolio.balance =this.selectedFolio.total_debit -  this.selectedFolio.total_credit 

						this.selectedFolio = data

					})
			} else {
				db.getDocList("Folio Transaction", {
					fields: [
						"name",
						'posting_date',
						"room_number",
						"parent_reference",
						"type",
						"account_code",
						"account_name",
						"quantity",
						"input_amount",
						"price",
						"amount",
						"discount_amount",
						"total_tax",
						"total_amount",
						"bank_fee_amount",
						"note",
						"creation",
						"owner",
						"modified",
						"modified_by",
						"show_print_preview",
						"print_format",
						"is_auto_post",
						"allow_enter_quantity"
					],
					filters: [["transaction_number", "=", data.name],["transaction_type", "=", "Reservation Folio"]],
					limit: 1000
				}).then((result) => {

					const folio_transaction = Enumerable.from(result).orderBy("$.posting_date").thenBy("name").toArray()
					folio_transaction.forEach(r => {
						r.quantity = r.allow_enter_quantity == 1? r.quantity:0;
						r.total_amount = r.type == "Credit" ? (r.total_amount - r.bank_fee_amount) * -1 : r.total_amount
						r.amount = r.type == "Credit" ? r.amount * -1 : r.amount
						r.price = r.type == "Credit" ? (r.price + r.bank_fee_amount) * -1 : r.price
					});
					this.folioTransactions = folio_transaction
					this.selectedFolio = data


				})


			}
			this.getFolioSummary(data.name)
		}

	}

	getFolioSummary(folio_number) {
		call.get("edoor.api.reservation.get_folio_summary_by_transaction_type", {
			transaction_type: "Reservation Folio",
			transaction_number: folio_number
		}).then((result) => {
			this.folio_summary = result.message
		}).
			catch((error) => {
				throw new Error(error.exception || error.message)
			})
	}

	getRoomRate(reservation_stay) {

		db.getDocList('Reservation Room Rate', {
			filters: [['reservation_stay', '=', reservation_stay]],
			fields: ["*"],
			orderBy: {
				field: 'date',
				order: 'asc',
			},
			limit: 1000
		}).then((doc) => {
			this.room_rates = doc
		})

	}

	canCheckIn() {
		const working_day = JSON.parse(localStorage.getItem("edoor_working_day"))
		
		return (this.reservationStay?.reservation_status == 'Reserved' && this.reservationStay.arrival_date <= working_day.date_working_day ) || 
				(this.reservationStay?.is_reserved_room ==1 && this.reservationStay.arrival_date <= working_day.date_working_day && this.reservationStay.departure_date >= working_day.date_working_day )
	}

	clear() {
		this.loading = ref(false)
		this.stay = {}
		this.reservationStay.value = ref({})
		this.guest = ref({})
		this.masterGuest.value = ref({})
		this.reservation.value = ref({})
		this.reservationStayNames.value = ref([])
		this.stay_summary.value = ref([])

		this.reservation.value = ref({})

	 
		this.selectedRoomRates = []
		this.folioTransactions.value = ref([])
		this.selectedFolioTransactions.value = ref([])

		//clear state key seletion of folio transaction
		 
		const state =JSON.parse( sessionStorage.getItem("folo_transaction_credit_debit_table_state"))
		if(state){
			state.selection=[]
			sessionStorage.setItem("folo_transaction_credit_debit_table_state", JSON.stringify(state))
	
		}
		

		 
	 
	}

}