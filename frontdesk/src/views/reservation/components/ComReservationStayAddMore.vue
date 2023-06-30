<template>
    <ComDialogContent @onOK="onSave" :loading="isSaving" hideButtonClose>
        <div class="bg-card-info border-round-xl mt-2 p-3 add-room-reserv">
            <div class="n__re-custom">
                {{ list }}
                <table class="w-full">
                    <thead>
                        <tr>
                            <th class="text-left">
                                <label>Arrival Data<span class="text-red-500">*</span></label>
                            </th>
                            <th class="text-left">
                                <label>Departure Data<span class="text-red-500">*</span></label>
                            </th>
                            <th class="text-left">
                                <label>Room Type<span class="text-red-500">*</span></label>
                            </th>
                            <th class="text-left">
                                <label class="px-2">Room Name</label>
                            </th>
                            <th class="text-right">
                                <label class="px-2">Rate</label>
                            </th>
                            <th>
                                <label class="text-center px-2">Adults</label>
                            </th>
                            <th>
                                <label class="text-center px-2">Children</label>
                            </th>
                            <th>
                                <label class="text-center px-2">Total Nights</label>
                            </th>
                            <th class="text-right">
                                <label class="px-2">Amount</label>
                            </th>

                        </tr>
                    </thead>
                    <tbody> 
                        <tr v-for="(d, index) in list" :key="index">
                            <td class="px-2 w-14rem">
                                <Calendar showIcon v-model="d.arrival_date"  :min-date="d.arrival_date" @update:modelValue="onStartDate($event,d)" dateFormat="dd-mm-yy" class="w-full"/>
                            </td>
                            <td class="px-2 w-14rem">
                                {{ d.departure_date }}
                                <Calendar showIcon v-model="d.departure_date"  :min-date="new Date(moment(rs.reservation.arrival_date).add(1,'days'))" @update:modelValue="onEndDate($event, d)" dateFormat="dd-mm-yy" class="w-full"/>
                            </td>
                            <td>
                                <InputNumber v-model="d.room_nights" @update:modelValue="onNight($event,d)" inputId="stacked-buttons" showButtons :min="1" class="w-full nig_in-put"/>
                            </td>
                            <td class="pr-2">
                                <ComSelectRoomTypeAvailability v-model="d.room_type_id" @onSelected="onSelectRoomType" :start-date="d.arrival_date" :end-date="d.departure_date"/>
                            </td>
                            <td class="p-2"> 
                                <ComSelectRoomAvailability showClear v-model="d.room_id" :start-date="d.arrival_date" :end-date="d.departure_date" :roomType="d.room_type_id" />
                            </td>
                            <td class="p-2 w-12rem text-right">
                                <span @click="onOpenChangeRate($event, d)" class="text-right w-full color-purple-edoor text-md font-italic ">
                                    <span class="link_line_action"><CurrencyFormat :value="d.rate" /></span>
                                </span>
                            </td>
                            <td class="p-2 w-5rem">
                                <InputNumber v-model="d.adult" inputId="stacked-buttons" showButtons :min="1" :max="100"
                                    class="child-adults-txt" />
                            </td>
                            <td class="p-2 w-5rem">
                                <InputNumber v-model="d.child" inputId="stacked-buttons" showButtons :min="0" :max="100"
                                    class="child-adults-txt" />
                            </td> 
                            <td class="p-2 w-10rem">
                                <div class="p-inputtext-pt text-end border-1 border-white h-12">
                                    <CurrencyFormat :value="(d.room_nights ?? 0) * (d.rate ?? 0)" />
                                </div>
                            </td>
                            <td v-if="doc.length > 1" class="pl-2 text-end"><Button icon="pi pi-trash"
                                    @click="onDeleteStay(index)" class="tr-h__custom text-3xl h-12" aria-label="Filter" />
                            </td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>
        <OverlayPanel ref="op">
            <ComReservationStayChangeRate v-model="rate" @onClose="onClose" @onUseRatePlan="onUseRatePlan" @onChangeRate="onChangeRate"/>
        </OverlayPanel>
    </ComDialogContent>
</template>
<script setup>
import ComReservationStayChangeRate from "./ComReservationStayChangeRate.vue"
 
import { ref, inject, computed, onMounted } from "@/plugin"
import { useToast } from "primevue/usetoast";
const dialogRef = inject("dialogRef");
const toast = useToast();
const frappe = inject('$frappe')
const db = frappe.db();
const call = frappe.call();
const moment = inject("$moment")
const socket = inject("$socket")
const rs = inject("$reservation")
const isSaving = ref(false)
const gv = inject("$gv")

const property = JSON.parse(localStorage.getItem("edoor_property"))
const room_types = ref([])
const rooms = ref([])
const working_day = ref({})
const selectedStay = ref({})
const rate = ref(0)
const op = ref();
const onOpenChangeRate = (event, stay) => {
    selectedStay.value = stay
    rate.value = JSON.parse(JSON.stringify(stay)).rate
    op.value.toggle(event);
}
const doc = ref({
        adult: 1,
        child: 0,
        room_type_id: '',
        room_id: '',
        rate: 0,
        is_manual_rate: false,
        departure_date:new Date(),
        arrival_date: new Date(),
        room_nights: 0
})
const list = ref([])

 
const onAddRoom = () => {
    rs.reservationStays.push(
        {
            // room_type_id: "RT-0005",
            // room_type: null,
            // room_id: "RM-0039",
            // room_number: null,

            adult: rs.reservationStays[rs.reservationStays.length - 1].adult,
            child: rs.reservationStays[rs.reservationStays.length - 1].child,
            // room_type_id: rs.reservationStays[rs.reservationStays.length - 1].room_type_id,
            rate: rs.reservationStays[rs.reservationStays.length - 1].rate,
            is_manual_rate: false

        }
    )
}


const onSave = () => {
    isSaving.value = true
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
            isSaving.value = false


        })
        .catch((error) => {

            const errors = error.exception.split(":")
            toast.add({ severity: 'error', summary: errors[0], detail: error.exception.replace(errors[0] + ":", ""), life: 3000 })
            isSaving.value = false
        });
}

const OnSelectRoom = () => {
    rooms.value.forEach(r => {
        r.selected = 0
    });

    rs.reservationStays.forEach(r => {
        let room = rooms.value.find(x => x.name == r.room_id)
        if (room) {
            room.selected = 1
        }
    });

}
const onSelectRoomType = (stay) => {

    stay.room_id = null
    OnSelectRoom()
    updateRate()
}

const onDeleteStay = (index) => {
    rs.reservationStays.splice(index, 1);
}

const updateRate = () => {
    rs.reservationStays.filter(r => (r.is_manual_rate || false) == false).forEach(s => {
        const room_type = room_types.value.find(r => r.name == s.room_type_id)


        if (room_type) {

            s.rate = room_type.rate

        }

    });
}

const onChangeRate = () => {
 
    selectedStay.value.rate = rate.value
    selectedStay.value.is_manual_rate = true
    op.value.hide();
}

const onUseRatePlan = () => {

    selectedStay.value.is_manual_rate = false;
    updateRate()
    op.value.hide();
}
function onClose(){
    op.value.hide()
}
function onNight(newValue, selected){ 
    // console.log(newValue)
    // selected.departure_date = moment(selected.arrival_date).add(newValue,'days').toDate()
}
function onEndDate(newValue, selected){
    selected.departure_date = new Date(newValue)
    console.log(selected.departure_date)
    // selected.room_nights = moment(selected.arrival_date).diff(moment(newValue), 'days')
}
function onStartDate(newValue, selected){
    
    // selected.room_nights = moment(newValue).diff(moment(selected.departure_date), 'days')
}

onMounted(() => {
    if(rs.reservation){
        doc.value.arrival_date = new Date(rs.reservation.arrival_date)
        doc.value.departure_date = new Date(rs.reservation.departure_date)
        doc.value.room_nights = moment(doc.value.departure_date).diff(moment(doc.value.arrival_date), 'days')
    }
    list.value.push(doc.value)
})
</script>
<style>
.ch__rate_nres input{
    text-align: right !important;
    font-size: 1.1rem;
    height: 3rem;
}
.p-button.p-component .p-button-icon{
    font-weight: 600;
    font-size: 1.25rem;
}

</style>