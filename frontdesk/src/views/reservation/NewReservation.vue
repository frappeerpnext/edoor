<template>
    <div>
        <h1>Add New Reservation</h1>
        {{ working_day }}
        <h1>Select Customer </h1>
        <ComAutoComplete v-model="doc.reservation.guest" placeholder="Guest" doctype="Customer"
            @onSelected="onSelectedCustomer" />
        <hr>
        <h1>New Guest Info</h1>
        <InputText type="text" class="p-inputtext-sm" placeholder="Guest Name" v-model="doc.guest_info.customer_name_en" />

        <ComAutoComplete v-model="doc.guest_info.customer_group" placeholder="Guest Type" doctype="Customer Group" />
        <Dropdown v-model="doc.guest_info.gender" :options="gender_list" placeholder="Gender" />


        <ComAutoComplete v-model="doc.guest_info.country" placeholder="Country" doctype="Country" />
        <InputText type="text" class="p-inputtext-sm" placeholder="Phone Number" v-model="doc.guest_info.phone_number" />
        <InputText type="text" class="p-inputtext-sm" placeholder="Email Address" v-model="doc.guest_info.email_address" />


        <ComAutoComplete v-model="doc.guest_info.identity_type" placeholder="Identity Type" doctype="Identity Type" />

        <InputText type="text" class="p-inputtext-sm" placeholder="ID/Passport Number"
            v-model="doc.guest_info.id_card_number" />

        <Calendar class="p-inputtext-sm" v-model="doc.guest_info.expired_date" placeholder="ID Expire Date"
            dateFormat="dd-mm-yy" />


        <hr style="margin: 10px;">
        <h1>Stay Information</h1>
        <hr style="margin: 10px;">
        <InputText type="text" class="p-inputtext-sm" placeholder="Reference Number"
            v-model="doc.reservation.reference_number" />


        <ComAutoComplete v-model="doc.reservation.business_source" placeholder="Business Source"
            doctype="Business Source" />
        <ComAutoComplete v-model="doc.reservation.rate_type" placeholder="Rate Type" doctype="Rate Type" />
        <Calendar class="p-inputtext-sm" v-model="doc.reservation.reservation_date" placeholder="Reservation Date"
            dateFormat="dd-mm-yy" />
        <Calendar class="p-inputtext-sm" v-model="doc.reservation.arrival_date" placeholder="Arrival Date"
            @date-select="onDateSelect" dateFormat="dd-mm-yy" />
        <Calendar class="p-inputtext-sm" v-model="doc.reservation.departure_date" placeholder="Departure Date"
            @date-select="onDateSelect" dateFormat="dd-mm-yy" :minDate="departureMinDate" />
        <InputNumber v-model="doc.reservation.adult" inputId="stacked-buttons" showButtons :min="1" :max="100" />
        <InputNumber v-model="doc.reservation.child" inputId="stacked-buttons" showButtons :min="1" :max="100" />

        Total Pax: {{ total_pax }}
        <br />

        <hr style="margin: 10px;">
        <h1>Rooom</h1>
        <table>
            <tr>
                <th>Room Type</th>
                <th>Room</th>
                <th>Rate</th>
                <th>Room Nights</th>
                <th>Amount</th>
            </tr>
            <tr v-for="(d, index) in doc.reservation_stay" :key="index">
                <td>
                    <Dropdown v-model="d.room_type_id" :options="room_types" optionValue="name" optionLabel="room_type"
                        placeholder="Select Room Type" class="w-full md:w-14rem" />
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
                    <InputText type="text" class="p-inputtext-sm" placeholder="Room Nights" v-model="d.room_night" />
                </td>
                <td>
                    <InputText type="text" class="p-inputtext-sm" placeholder="Total Amount" v-model="d.total_amount" />
                </td>



            </tr>
        </table>
        <Button @click="onSave">Save</Button>
        <Button @click="onAddRoom">Add</Button>
        <hr />
        {{ doc }}
    </div>
</template>
<script setup>
import Calendar from 'primevue/calendar';
import { ref, inject, computed, onMounted } from "@/plugin"
import { useToast } from "primevue/usetoast";
const dialogRef = inject("dialogRef");
const toast = useToast();
const frappe = inject('$frappe')
const db = frappe.db();
const call = frappe.call();
const moment = inject("$moment")
const socket = inject("$socket")

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
        {
            room_type_id: "RT-0005",
            room_type: null,
            room_id: "RM-0039",
            room_number: null,
            rate: 150

        }
    ]
})

const gender_list = ["Not Set", "Male", "Female"]

const total_pax = computed(() => {
    return doc.value.reservation.adult + doc.value.reservation.child;
})

const departureMinDate = computed(() => {
    return moment(doc.value.reservation.arrival_date).add(1, "days").toDate();
})

const onDateSelect = (date) => {
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
        start_date: moment(doc.value.reservation.reservation_date).format("yyyy-MM-DD"),
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
            console.log(error)
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
        doc.value.reservation.arrival_date = moment(working_day.value.date_working_day).toDate()
        doc.value.reservation.departure_date = moment(working_day.value.date_working_day).add(1, 'days').toDate()

        getRoomType()
        getRooms()

    })
});


</script>