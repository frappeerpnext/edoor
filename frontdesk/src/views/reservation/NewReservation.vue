<template>
    <div class="n__re-custom grid">
        <div class="col">
            <div class="bg-card-info border-round-xl p-3 h-full">
                <div class="">
                    <div>
                        <label>Reservation Date<span class="sup-rq-custom">*</span></label><br />
                        <Calendar class="p-inputtext-sm w-full" v-model="doc.reservation.reservation_date"
                            placeholder="Reservation Date" dateFormat="dd-mm-yy" showButtonBar />
                    </div>
                    <div class="pt-2">
                        <label>Internal Ref. No</label><br />
                        <InputText type="text" class="p-inputtext-sm w-full" placeholder="Internal Ref. Number"
                            v-model="doc.reservation.internal_reference_number" />
                    </div>
                    <div class="grid pt-2 m-0">
                        <div class="arr_wfit col px-0">
                            <label>Arrival</label><br />
                            <Calendar class="p-inputtext-sm depart-arr w-full border-round-xl"
                                v-model="doc.reservation.arrival_date" placeholder="Arrival Date"
                                @date-select="onDateSelect" dateFormat="dd-mm-yy" showButtonBar />
                        </div>
                        <div class="night__wfit col-fixed px-0">
                            <div>
                                <label class="hidden">Room Night</label><br />
                            </div>
                            <ComReservationInputNight v-model="doc.reservation.room_night" @onUpdate="onRoomNightChanged" />
                        </div>
                        <div class="arr_wfit col px-0">
                            <label>Departure</label><br />
                            <Calendar class="p-inputtext-sm depart-arr w-full" v-model="doc.reservation.departure_date"
                                placeholder="Departure Date" @date-select="onDateSelect" dateFormat="dd-mm-yy"
                                :minDate="departureMinDate" />
                        </div>
                    </div>
                </div>

                <div class="">
                    <div class="grid">
                        <div class="col">
                            <div class="pt-2">
                                <label>Business Source</label><br />
                                <ComAutoComplete v-model="doc.reservation.business_source" placeholder="Business Source"
                                    doctype="Business Source" class="auto__Com_Cus w-full" />
                            </div>
                        </div>
                        <div class="col">
                            <div class="pt-2">
                                <label>Rate Type</label><br />
                                <ComAutoComplete v-model="doc.reservation.rate_type" placeholder="Rate Type"
                                    doctype="Rate Type" class="auto__Com_Cus w-full" />
                            </div>
                        </div>
                    </div>
                    <div class="grid pt-2">
                        <div class="col">
                            <label>Adults</label><br />
                            <InputNumber v-model="doc.reservation.adult" inputId="stacked-buttons" showButtons :min="1"
                                :max="100" class="w-full" />
                        </div>
                        <div class="col">
                            <label>Children</label><br />
                            <InputNumber v-model="doc.reservation.child" inputId="stacked-buttons" showButtons :min="0"
                                :max="100" class="w-full" />
                        </div>
                        <div class="col-fixed" style="width: 100px">
                            <label>Total Pax</label><br>
                            <div class="p-inputtext-pt text-center border-0 h-12">{{ total_pax }}</div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        <div class="col">
            <div class="bg-card-info border-round-xl p-3 h-full">
                <h1 class="text-lg line-height-4 font-bold mb-3">Guest Information</h1>
                <div>
                    <div class="w-full n__re-custom">
                        <label>Search Guest</label>
                        <ComAutoComplete v-model="doc.reservation.guest" class="pb-2" placeholder="Guest" doctype="Customer"
                            @onSelected="onSelectedCustomer" />
                        <div class="grid">
                            <div class="col-12 pt-2">
                                <label>Guest Name</label><br />
                                <InputText type="text" class="p-inputtext-sm h-12 w-full" placeholder="Guest Name"
                                    v-model="doc.guest_info.customer_name_en" />
                            </div>
                            <div class="col-4 pt-2">
                                <label>Guest Type</label><br />
                                <ComAutoComplete v-model="doc.guest_info.customer_group" class="w-full"
                                    placeholder="Guest Type" doctype="Customer Group" />
                            </div>
                            <div class="col-4 pt-2">
                                <label>Gender</label><br />
                                <Dropdown v-model="doc.guest_info.gender" :options="gender_list" placeholder="Gender"
                                    class="w-full" />
                            </div>
                            <div class="col-4 pt-2">
                                <label>Country</label><br />
                                <ComAutoComplete v-model="doc.guest_info.country" class="w-full" placeholder="Country"
                                    doctype="Country" />
                            </div>
                            <div class="col-4 pt-1">
                                <label>Phone Number</label><br />
                                <InputText type="text" class="p-inputtext-sm w-full" placeholder="Phone Number"
                                    v-model="doc.guest_info.phone_number" />
                            </div>
                            <div class="col-4 pt-1">
                                <label>Email Address</label><br />
                                <InputText type="text" class="p-inputtext-sm w-full" placeholder="Email Address"
                                    v-model="doc.guest_info.email_address" />
                            </div>
                            <div class="col-4 pt-1">
                                <label>Identity Type</label><br />
                                <ComAutoComplete v-model="doc.guest_info.identity_type" class="w-full"
                                    placeholder="Identity Type" doctype="Identity Type" />
                            </div>
                            <div class="col-4 pt-1">
                                <label>ID/Passport Number</label><br />
                                <InputText type="text" class="p-inputtext-sm w-full" placeholder="ID/Passport Number"
                                    v-model="doc.guest_info.id_card_number" />
                            </div>
                            <div class="col-4 pt-1">
                                <label>ID Expire Date</label><br />
                                <Calendar class="p-inputtext-sm w-full" v-model="doc.guest_info.expired_date"
                                    placeholder="ID Expire Date" dateFormat="dd-mm-yy" />
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    <div class="bg-card-info border-round-xl mt-3 p-3 add-room-reserv">
        <div class="grid" v-for="(  d, index  ) in   doc.reservation_stay  " :key="index">
            <div class="col">
                <div class="font-medium" v-if="index == 0">Room Type</div>
                <Dropdown v-model="d.room_type_id" :options="room_types" optionValue="name" optionLabel="room_type"
                    placeholder="Select Room Type" class="w-full" />
            </div>
            <div class="col">
                <div class="font-medium" v-if="index == 0">Room Name</div>
                <Dropdown v-model="d.room_id" :options="rooms.filter((r) => r.room_type_id == d.room_type_id)"
                    optionValue="name" optionLabel="room_number" placeholder="Select Room" showClear filter
                    class="w-full" />
            </div>
            <div class="col">
                <div class="font-medium" v-if="index == 0">Rate</div>
                <InputText type="text" class="p-inputtext-sm w-full" placeholder="Rate" v-model="d.rate" />
            </div>
            <div class="col-fixed" style="width:150px">
                <div class="font-medium" v-if="index == 0">Total Nights</div>
                <div class="p-inputtext-pt text-center border-0 h-12">{{ doc.reservation.room_night }}</div>
            </div>
            <div class="col-fixed" style="width:150px">
                <div class="font-medium" v-if="index == 0">Amount</div>
                <div class="p-inputtext-pt text-center border-0 h-12">{{ (doc.reservation.room_night ?? 0) * (d.rate ??
                    0)
                }}</div>
            </div>
            <div class="col-1">
                <div class="flex justify-end w-full h-12" v-if="index != 0">
                    <Button icon="pi pi-trash" @click="deleteResRoom" class="tr-h__custom text-3xl h-full"
                        aria-label="Filter" />
                </div>
            </div>
        </div>
        <Button @click="onAddRoom" class="px-4 border-round-xl border-0">Add Room</Button><br />
    </div>
    <!-- <hr class="my-3"> -->
    <div class="mt-3">
        <div>
            <label>Note</label><br />
            <Textarea v-model="doc.reservation.note" rows="5" placeholder="Note" cols="30" class="w-full border-round-xl" />
        </div>
    </div>
    <div class="flex justify-end w-full mt-1">
        <Button class="h-12 border-round-xl border-0" @click="onSave">Save</Button>
    </div>
</template>
<script setup>
import Calendar from 'primevue/calendar';
import ComReservationInputNight from './components/ComReservationInputNight.vue';
import { ref, inject, computed, onMounted } from "@/plugin"
import { useToast } from "primevue/usetoast";
const dialogRef = inject("dialogRef");
const toast = useToast();
const frappe = inject('$frappe')
const db = frappe.db();
const call = frappe.call();
const moment = inject("$moment")
const socket = inject("$socket")

// const roomNightValue = ref(doc.reservation.room_night + "Nights")

const property = JSON.parse(localStorage.getItem("edoor_property"))
const room_types = ref([])
const rooms = ref([])
const working_day = ref({})

const doc = ref({
    reservation: {
        doctype: "Reservation",
        property: property.name,
        reservation_type: "FIT",
        arrival_time: '12:00:00',
        departure_time: '12:00:00',
        adult: 1,
        child: 0,
        reservation_status: 'Reserved'
    },
    guest_info: {
        "doctype": "Customer",
        "gender": "Not Set"
    },
    reservation_stay: [{ rate: 0 },]
})

const gender_list = ["Not Set", "Male", "Female"]

const total_pax = computed(() => {
    return doc.value.reservation.adult + doc.value.reservation.child;
})

const departureMinDate = computed(() => {
    return moment(doc.value.reservation.arrival_date).add(1, "days").toDate();
})

const onDateSelect = (date) => {


    doc.value.reservation.room_night = moment(doc.value.reservation.departure_date).diff(moment(doc.value.reservation.arrival_date), 'days')
    getRoomType()
    getRooms()
}


const getRoomType = () => {
    call.get("edoor.api.reservation.check_room_type_availability", {
        property: property.name,
        start_date: moment(doc.value.reservation.reservation_date).format("yyyy-MM-DD"),
        end_date: moment(doc.value.reservation.departure_date).format("yyyy-MM-DD")
    })
        .then((result) => {
            room_types.value = result.message;
            console.log(result)
        })
}

const getRooms = () => {

    call.get("edoor.api.reservation.check_room_availability", {
        property: property.name,
        start_date: moment(doc.value.reservation.arrival_date).format("yyyy-MM-DD"),
        end_date: moment(doc.value.reservation.departure_date).format("yyyy-MM-DD")
    })
        .then((result) => {

            rooms.value = result.message;
            console.log("room", result)
        })
}

function onSelectedCustomer(event) {

    db.getDoc('Customer', event.value)
        .then((d) => doc.value.guest_info = d)
        .catch((error) => console.error(error));
}

const onRoomNightChanged = (event) => {
    console.log(event)
    doc.value.reservation.departure_date = moment(doc.value.reservation.arrival_date).add(event, "Days").toDate()
    getRoomType()
    getRooms()
}

const onAddRoom = () => {
    doc.value.reservation_stay.push(
        {
            // room_type_id: "RT-0005",
            // room_type: null,
            // room_id: "RM-0039",
            // room_number: null,
            rate: 0

        }
    )
}


const onSave = () => {
    const data = JSON.parse(JSON.stringify(doc.value))

    if (data.reservation.reservation_date) data.reservation.reservation_date = moment(data.reservation.reservation_date).format("yyyy-MM-DD")
    if (data.reservation.arrival_date) data.reservation.arrival_date = moment(data.reservation.arrival_date).format("yyyy-MM-DD")
    if (data.reservation.departure_date) data.reservation.departure_date = moment(data.reservation.departure_date).format("yyyy-MM-DD")
    if (data.guest_info.expired_date) data.guest_info.expired_date = moment(data.guest_info.expired_date).format("yyyy-MM-DD")


    call.get('edoor.api.reservation.add_new_fit_reservation', {
        doc: data
    })
        .then((result) => {

            toast.add({ severity: 'success', summary: 'Add New Reservation', detail: "Add new reservation successfully", life: 3000 })
            socket.emit("RefresheDoorDashboard", property.name);
            dialogRef.value.close(result.message);


        })
        .catch((error) => {

            const errors = error.exception.split(":")
            toast.add({ severity: 'error', summary: errors[0], detail: error.exception.replace(errors[0] + ":", ""), life: 3000 })
        });
}

onMounted(() => {
    call.get("edoor.api.frontdesk.get_working_day", {
        property: property.name
    }).then((result) => {
        working_day.value = (result.message)
        doc.value.reservation.reservation_date = moment(working_day.value.date_working_day).toDate()

        if (!dialogRef) {
            doc.value.reservation.arrival_date = moment(working_day.value.date_working_day).toDate()
            doc.value.reservation.departure_date = moment(working_day.value.date_working_day).add(1, 'days').toDate()

            getRoomType()
            getRooms()
        } else {
            console.log(dialogRef.value.data)
            if (dialogRef.value.data?.arrival_date) {
                doc.value.reservation.arrival_date = dialogRef.value.data.arrival_date
                doc.value.reservation.departure_date = dialogRef.value.data.departure_date
                doc.value.reservation_stay[0].room_type_id = dialogRef.value.data.room_type_id
                doc.value.reservation_stay[0].room_id = dialogRef.value.data.room_id
            } else {
                doc.value.reservation.arrival_date = moment(working_day.value.date_working_day).toDate()
                doc.value.reservation.departure_date = moment(working_day.value.date_working_day).add(1, 'days').toDate()

            }

            getRoomType()
            getRooms()
        }


        doc.value.reservation.room_night = moment(doc.value.reservation.departure_date).diff(moment(doc.value.reservation.arrival_date), 'days')

    })
});


</script>