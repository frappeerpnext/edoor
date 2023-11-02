<template>
   <ComOverlayPanelContent style="width: 40rem;" :loading="loading" @onSave="onSave" @onCancel="onClose">
     
    <div class="grid py-2 wp-number-cus">
            <div class="col-6">
                <label>Arrival Date</label>
                <Calendar :selectOtherMonths="true" showIcon v-model="data.arrival_date"  :min-date="new Date(moment(data.min_date))" @update:modelValue="onStartDate" dateFormat="dd-mm-yy" class="w-full"/>
            </div>
            <div class="col-6">
                <label>Arrival Time</label>
                <Calendar selectOtherMonths class="w-full" v-model="data.arrival_time" timeOnly />
            </div>
            <div class="col-6">
                <label>Departure Date</label>
                <Calendar selectOtherMonths showIcon v-model="data.departure_date" :selectOtherMonths="true" :min-date="new Date(moment(data.arrival_date).add(1,'days'))" @update:modelValue="onEndDate" dateFormat="dd-mm-yy" class="w-full"/>
            </div>
            <div class="col-6">
                <label>Departure Time</label>
                <Calendar selectOtherMonths class="w-full" v-model="data.departure_time" timeOnly /> 
            </div>
            <div class="col-6">
                <label>Nights</label>
                <InputNumber v-model="data.room_nights" @update:modelValue="onNight($event)" inputId="stacked-buttons" showButtons :min="1" class="w-full nig_in-put"/>
            </div>
        </div>
    
   </ComOverlayPanelContent>
</template>
<script setup>
import {ref,inject,postApi} from "@/plugin"
const dialogRef = inject("dialogRef");
const socket = inject("$socket")
const rs = inject("$reservation")
const moment = inject("$moment")
const loading = ref(false)
const emit = defineEmits("onClose")
const gv = inject("$gv")
const workingDay = JSON.parse(localStorage.getItem("edoor_working_day"))
const data = ref({
    room_nights: rs.reservation.room_nights,
    min_date: workingDay.date_working_day,
    can_arrival: (moment(workingDay.date_working_day).isAfter(rs.reservation.arrival_date) ? true : false),
    arrival_date: moment(rs.reservation.arrival_date).toDate(),
    departure_date: moment(rs.reservation.departure_date).toDate(),
    arrival_time: moment(rs.reservation.arrival_date + " " +  rs.reservation.arrival_time).toDate(),
    departure_time:moment(rs.reservation.departure_date + " " +  rs.reservation.departure_time).toDate(),
})

function onClose(){
    emit('onClose')
}
function onNight(newValue){
    data.value.departure_date = moment(data.value.arrival_date).add(newValue,'days').toDate()
}
function onEndDate(newValue){
    newValue = moment.utc(moment(newValue).format("YYYY-MM-DD")).toDate()
        data.value.departure_date = newValue
    data.value.room_nights = moment(data.value.departure_date).diff(moment(data.value.arrival_date), 'days') 
}
function onStartDate(newValue){
    if(moment(newValue).isSame(data.value.departure_date) || moment(newValue).isAfter(data.value.departure_date)){
        data.value.departure_date = moment(newValue).add(1,'days').toDate()
    }
    data.value.room_nights = moment(data.value.departure_date).diff(moment(newValue), 'days')
}
function onSave(){
    loading.value = true
    postApi("reservation.group_change_stay",{
        data:{
            stays: rs.reservation.name,
            arrival_date: gv.dateApiFormat(data.value.arrival_date),
            departure_date: gv.dateApiFormat(data.value.departure_date),
            arrival_time:moment(data.value.arrival_time).format("HH:mm:ss"),
            departure_time:moment(data.value.departure_time).format("HH:mm:ss")
        }
    }
    ).then((r)=>{
        loading.value = false
        window.socket.emit("ReservationList", { property:window.property_name})
        window.socket.emit("ReservationDetail", window.reservation)
        window.socket.emit("Reports", window.property_name)
        // emit("onClose", r.message)

    }).catch((err)=>{
        loading.value = false
    })
}
</script>