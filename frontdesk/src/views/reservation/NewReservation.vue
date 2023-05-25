<template>
    <div class="n__re-custom">
        <div class="grid">
            <div class="flex col">
                <div class="arr_wfit">
                    <label>Arrival Date</label><br />
                    <Calendar class="p-inputtext-sm depart-arr w-full" v-model="doc.reservation.arrival_date"
                        placeholder="Arrival Date" @date-select="onDateSelect" dateFormat="dd-mm-yy" />
                </div>
                <div class="night__wfit">
                    <label class="hidden">Room Night</label><br />
                    <ComReservationInputNight v-model="doc.reservation.room_night" @onUpdate="onRoomNightChanged" />
                </div>
                <div class="arr_wfit">
                    <label>Departure Date</label><br />
                    <Calendar class="p-inputtext-sm depart-arr w-full" v-model="doc.reservation.departure_date"
                        placeholder="Departure Date" @date-select="onDateSelect" dateFormat="dd-mm-yy"
                        :minDate="departureMinDate" />
                </div>
            </div>
            <div class="col">
                <label>Internal Ref. Number</label><br />
                <InputText type="text" class="p-inputtext-sm w-full" placeholder="Internal Ref. Number"
                    v-model="doc.reservation.internal_reference_number" />
            </div>
            <div class="col">
                <label>Reservation Date</label><br />
                <Calendar class="p-inputtext-sm w-full" v-model="doc.reservation.reservation_date"
                    placeholder="Reservation Date" dateFormat="dd-mm-yy" />
            </div>
        </div>
        <div>
            <label>Business Source</label><br />
            <ComAutoComplete v-model="doc.reservation.business_source" placeholder="Business Source"
                doctype="Business Source" />
        </div>
        <div>
            <label>Rate Type</label><br />
            <ComAutoComplete v-model="doc.reservation.rate_type" placeholder="Rate Type" doctype="Rate Type" />
        </div>
        <div>
            <label>Adult</label><br />
            <InputNumber v-model="doc.reservation.adult" inputId="stacked-buttons" showButtons :min="1" :max="100" />
        </div>
        <div>
            <label>Child</label><br />
            <InputNumber v-model="doc.reservation.child" inputId="stacked-buttons" showButtons :min="0" :max="100" />
        </div>
        <div>
            Total Pax: {{ total_pax }}
        </div>
        <!-- {{ working_day.date_working_day }} -->
        <!-- {{ working_day }} -->
        <label>Select Customer</label>
        <ComAutoComplete v-model="doc.reservation.guest" class="pb-2" placeholder="Guest" doctype="Customer"
            @onSelected="onSelectedCustomer" />
        <hr>

        <div class="py-2 clan-grid-set">
            <ComFieldset nameLegend='New guest info'>
                <h1>New Guest Info</h1>
                <div class="grid grid-rows-4 grid-flow-col gap-4">
                    <div>
                        <label>Guest Name</label>
                        <InputText type="text" class="p-inputtext-sm h-12" placeholder="Guest Name"
                            v-model="doc.guest_info.customer_name_en" />
                    </div>
                    <div>
                        <label>Guest Type</label>
                        <ComAutoComplete v-model="doc.guest_info.customer_group" placeholder="Guest Type"
                            doctype="Customer Group" />
                    </div>
                    <div>
                        <label>Gender</label>
                        <Dropdown v-model="doc.guest_info.gender" :options="gender_list" placeholder="Gender" />
                    </div>
                    <div>
                        <label>Country</label>
                        <ComAutoComplete v-model="doc.guest_info.country" placeholder="Country" doctype="Country" />
                    </div>
                    <div>
                        <label>Phone Number</label>
                        <InputText type="text" class="p-inputtext-sm" placeholder="Phone Number"
                            v-model="doc.guest_info.phone_number" />
                    </div>
                    <div>
                        <label>Email Address</label>
                        <InputText type="text" class="p-inputtext-sm" placeholder="Email Address"
                            v-model="doc.guest_info.email_address" />
                    </div>
                    <div>
                        <label>Identity Type</label>
                        <ComAutoComplete v-model="doc.guest_info.identity_type" placeholder="Identity Type"
                            doctype="Identity Type" />
                    </div>
                    <div>
                        <label>ID/Passport Number</label>
                        <InputText type="text" class="p-inputtext-sm" placeholder="ID/Passport Number"
                            v-model="doc.guest_info.id_card_number" />
                    </div>
                    <div>
                        <label>ID Expire Date</label>
                        <Calendar class="p-inputtext-sm" v-model="doc.guest_info.expired_date" placeholder="ID Expire Date"
                            dateFormat="dd-mm-yy" />
                    </div>
                </div>
            </ComFieldset>
            <div class="pt-2">
                <ComFieldset nameLegend='Stay information'>
                    <div class="grid grid-rows-4 grid-flow-col gap-4">
                        <div>
                            <label>Note</label>
                            <InputText type="text" class="p-inputtext-sm" placeholder="Note"
                                v-model="doc.reservation.note" />
                        </div>
                    </div>
                </ComFieldset>
            </div>
        </div>
        <div>
            <ComFieldset nameLegend='Room'>
                <table>
                    <tr>
                        <th>Room Type</th>
                        <th>Room</th>
                        <th>Rate</th>
                        <th>Room Nights</th>
                        <th>Amount</th>
                    </tr>
                    <tr v-for="(  d, index  ) in   doc.reservation_stay  " :key="index">
                        <td>
                            <Dropdown v-model="d.room_type_id" :options="room_types" optionValue="name"
                                optionLabel="room_type" placeholder="Select Room Type" class="w-full md:w-14rem" />
                        </td>

                        <td>

                            <Dropdown v-model="d.room_id" :options="rooms.filter((r) => r.room_type_id == d.room_type_id)"
                                optionValue="name" optionLabel="room_number" placeholder="Select Room" showClear filter
                                class="w-full md:w-14rem" />
                        </td>
                        <td>
                            <InputText type="text" class="p-inputtext-sm" placeholder="Rate" v-model="d.rate" />
                        </td>

                        <td>
                            {{ doc.reservation.room_night }}
                        </td>
                        <td>
                            {{ (doc.reservation.room_night ?? 0) * (d.rate ?? 0) }}
                        </td>



                    </tr>
                </table>
                Total Room Night: {{ doc.reservation.room_night * doc.reservation_stay.length }}
                Total Amount: {{ doc.reservation_stay.reduce((n, d) => n + d.rate * doc.reservation.room_night, 0) }}
            </ComFieldset>
        </div>



        <Button @click="onSave">Save</Button>
        <Button @click="onAddRoom">Add</Button>
        <hr />
        {{ doc }}
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
    reservation_stay: [
        {},]
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
            console.log(result)
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
            // rate: 150

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