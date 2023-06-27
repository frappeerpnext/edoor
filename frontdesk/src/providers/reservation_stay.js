import Enumerable from 'linq'
import { FrappeApp } from 'frappe-js-sdk';
import { ref, computed, useRouter } from '@/plugin';
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
		this.reservationStatusDelete = ['No Show','Void','Cancelled']
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
		if (this.folioTransactions.value) {

			return this.folioTransactions.value.reduce((n, d) => n + (d.credit || 0), 0)


		}
		return 0

	})

	totalDebit = computed(() => {
		if (this.folioTransactions.value) {

			return this.folioTransactions.value.reduce((n, d) => n + (d.debit || 0), 0)


		}
		return 0

	})


	onLoadReservationFolios() {
		return new Promise((resolve, reject) => {
			db.getDocList('Reservation Folio', {
				fields: ["name", "status", "is_master", "rooms", "room_types", "guest", "guest_name", "phone_number", "email", "photo", "status","balance"],
				filters: [['reservation_stay', '=', this.reservationStay?.name]],
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
			this.selectedFolio = data
			 if (setting?.folio_transaction_stype_credit_debit == 1) {
				call.get('edoor.api.reservation.get_folio_transaction', {
					folio_number: data.name
				})
					.then((result) => {

						this.folioTransactions = result.message
					})
			}else{
				db.getDocList("Folio Transaction",{
					fields:[
							"name",
							'posting_date',
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
						],
					filters:[["folio_number","=",data.name]],
					limit:1000
				}).then((result)=>{
					
					const folio_transaction =  Enumerable.from(result).orderBy("$.posting_date").thenBy("name").toArray()
					folio_transaction.forEach(r => {
						r.total_amount = r.type=="Credit"?(r.total_amount - r.bank_fee_amount)  *-1:r.total_amount
						r.amount = r.type=="Credit"?r.amount*-1:r.amount
						r.price = r.type=="Credit"?(r.price + r.bank_fee_amount ) *-1:r.price
					});
					this.folioTransactions = folio_transaction

				})
					
				
			}
		}
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
	}

}