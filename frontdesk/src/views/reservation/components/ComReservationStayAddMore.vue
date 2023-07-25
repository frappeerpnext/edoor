<template>
    <ComDialogContent @onOK="onSave" :loading="isSaving" hideButtonClose>
        <div class="bg-card-info border-round-xl mt-2 p-3 add-room-reserv">
            <div class="n__re-custom"> 
                <table class="w-full">
                    <thead>
                        <tr>
                            <th class="text-left pr-2">
                                <label>Arrival Data<span class="text-red-500">*</span></label>
                            </th>
                            <th class="text-left px-2">
                                <label>Departure Data<span class="text-red-500">*</span></label>
                            </th>
                            <th>
                                <label class="text-center px-2">Nights</label>
                            </th>
                            <th class="text-left px-2">
                                <label>Room Type<span class="text-red-500">*</span></label>
                            </th>
                            <th class="text-left px-2">
                                <label class="px-2">Room Name</label>
                            </th>
                            <th class="text-right px-2">
                                <label>Rate</label>
                            </th>
                            <th>
                                <label class="text-center ">Adults</label>
                            </th>
                            <th>
                                <label class="text-center">Children</label>
                            </th>
                            
                            <th class="text-right px-2">
                                <label>Amount</label>
                            </th>
                            <th class="w-0"></th>
                        </tr>
                    </thead>
                    <tbody>  
                        <tr v-for="(d, index) in list" :key="index"> 
                            <td class="pr-2 w-10rem"> 
                                <Calendar inputClass="w-7rem" showIcon v-model="d.arrival_date" :max-date="new Date(moment(d.departure_date))" :min-date="new Date(moment(rs.reservation.arrival_date))" @update:modelValue="onStartDate($event,d)" dateFormat="dd-mm-yy" class="w-full"/>
                            </td>
                            <td class="px-2 w-10rem"> 
                                <Calendar inputClass="w-7rem" showIcon v-model="d.departure_date"  :min-date="new Date(moment(d.arrival_date).add(1,'days'))" @update:modelValue="onEndDate($event, d)" dateFormat="dd-mm-yy" class="w-full"/>
                            </td>
                            <td class="px-2 w-5rem">
                                <InputNumber v-model="d.room_nights" @update:modelValue="onNight($event,d)" inputId="stacked-buttons" showButtons :min="1" class="w-full nig_in-put"/>
                            </td>
                            <td class="px-2 w-15rem">
                                <ComSelectRoomTypeAvailability v-model="d.room_type_id" @onSelected="onSelectRoomType($event,d)" :start-date="d.arrival_date" :end-date="d.departure_date"/>
                            </td>
                            <td class="px-2 w-10rem">
                                <ComSelectRoomAvailability showClear v-model="d.room_id" :except="list.map(r => r.room_id).join(',')" :start-date="d.arrival_date" :end-date="d.departure_date" :roomType="d.room_type_id" />
                            </td>
                            <td class="p-2 text-right w-10rem">
                                <button @click="onOpenChangeRate($event, d)" class="text-right w-full color-purple-edoor text-md font-italic ">
                                    <span class="link_line_action"><CurrencyFormat :value="d.rate" /></span>
                                </button>
                            </td>
                            <td class="px-2 w-5rem">
                                <InputNumber v-model="d.adult" style="width: -webkit-fill-available;" inputClass="w-5rem" inputId="stacked-buttons" showButtons :min="1" :max="100"/>
                            </td>
                            <td class="px-2 w-5rem">
                                <InputNumber v-model="d.child" style="width: -webkit-fill-available;" inputClass="w-5rem" inputId="stacked-buttons" showButtons :min="0" :max="100"/>
                            </td> 
                            <td class="px-2 w-10rem">
                                <div class="p-inputtext-pt w-full float-right text-end border-1 border-white h-12">
                                    <CurrencyFormat  :value="(d.room_nights ?? 0) * (d.rate ?? 0)" />
                                </div>
                            </td>
                            <td v-if="list.length > 1" class="pl-2 text-end">
                                <Button icon="pi pi-trash" @click="onDeleteStay(index)" class="tr-h__custom text-3xl h-12" aria-label="Filter" />
                            </td>
                        </tr>
                    </tbody>
                </table>
            </div>
            <div class="mt-3 flex justify-end">
                <Button @click="onAddRoom" class="dialog_btn_transform conten-btn py-4">
                    <img :src="IconAddRoom" class="btn-add_comNote__icon me-1"/>
                    Add Room
                </Button>
            </div>
        </div>
        <OverlayPanel ref="op">
            <ComReservationStayChangeRate v-model="rate" @onClose="onClose" @onUseRatePlan="onUseRatePlan" @onChangeRate="onChangeRate"/>
        </OverlayPanel>
    </ComDialogContent>
</template>
<script setup>
import ComReservationStayChangeRate from "./ComReservationStayChangeRate.vue"
import IconAddRoom from '@/assets/svg/icon-add-plus-sign-purple.svg';
import { ref, inject, postApi, onMounted } from "@/plugin"
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
const edoor_working_day = JSON.parse(localStorage.getItem("edoor_working_day"))
const rooms = ref([])
const working_day = ref({})
const selectedStay = ref({})
const rate = ref(0)
const op = ref();

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
    
    list.value.push(
        { 
            arrival_date: list.value[list.value.length - 1].arrival_date,
            departure_date: list.value[list.value.length - 1].departure_date,
            room_nights: list.value[list.value.length - 1].room_nights,
            adult: list.value[list.value.length - 1].adult,
            child: list.value[list.value.length - 1].child,
            room_type_id: list.value[list.value.length - 1].room_type_id,
            rate: list.value[list.value.length - 1].rate,
            is_manual_rate: list.value[list.value.length - 1].is_manual_rate
        }
    )
}


const onSave = () => { 
    if(list.value.filter(r=>r.room_type_id == "").length > 0){
        gv.toast('warn',"Please select room type.")
        return
    }
    isSaving.value = true
    let data = JSON.parse(JSON.stringify(list.value))
    data = data.map((r)=>{
        return {
            ...r,
            departure_date: gv.dateApiFormat(r.departure_date),
            arrival_date: gv.dateApiFormat(r.arrival_date)
        }
    }) 
    postApi("reservation.stay_add_more_rooms",{reservation: rs.reservation.name,data:data}).then((r)=>{
        
        if(r){
            isSaving.value = false
            rs.LoadReservation(rs.reservation.name)
            dialogRef.value.close()
        }
        
    }).catch((er)=>{
        isSaving.value = false
    })
}
const onSelectRoomType = ($event,selected) => {
    selected.original_rate = $event.rate
    if(!selected.is_manual_rate){
        selected.rate = $event.rate
    }
}

const onDeleteStay = (index) => {
    list.value.splice(index, 1);
}
const onOpenChangeRate = (event, selected) => {
    rate.value = selected.rate
    selectedStay.value = selected
    op.value.toggle(event);
}
const onChangeRate = () => {
    selectedStay.value.rate = rate.value
    selectedStay.value.is_manual_rate = true
    const index = list.value.indexOf(selectedStay.value)
    op.value.hide();
}

const onUseRatePlan = () => {
    const index = list.value.indexOf(selectedStay.value)
    list.value[index].is_manual_rate = false
    list.value[index].rate = list.value[index].original_rate
    op.value.hide();
}
function onClose(){
    op.value.hide()
}
function onNight(newValue, selected){
    selected.departure_date = moment(selected.arrival_date).add(newValue,'days').toDate()
}
function onEndDate(newValue, selected){
    const index = list.value.indexOf(selected)
    selected.departure_date = moment(newValue).toDate()
    selected.room_nights = moment(selected.departure_date).diff(moment(list.value[index].arrival_date), 'days')
 
}
function onStartDate(newValue, selected){
    if(moment(newValue).isSame(selected.departure_date) || moment(newValue).isAfter(selected.departure_date)){
        selected.departure_date = moment(newValue).add(1,'days').toDate()
    }
    selected.room_nights = moment(selected.departure_date).diff(moment(newValue), 'days')
}

onMounted(() => {
    if(rs.reservation){
        const arrival_date = ref(moment(rs.reservation.arrival_date).toDate())
        if(moment(arrival_date.value).isSame(edoor_working_day.date_working_day) || moment(arrival_date.value).isBefore(edoor_working_day.date_working_day)){
            arrival_date.value = moment(edoor_working_day.date_working_day).toDate()
        }
        const departure_date = ref(moment(rs.reservation.departure_date).toDate())
        if(moment(departure_date.value).isSame(arrival_date.value) || moment(departure_date.value).isBefore(arrival_date.value)){
            departure_date.value = moment(arrival_date.value).add(1, 'days').toDate()
        }
        doc.value.arrival_date = arrival_date.value
        doc.value.departure_date = departure_date.value
        doc.value.room_nights = moment(departure_date.value).diff(moment(arrival_date.value), 'days')
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