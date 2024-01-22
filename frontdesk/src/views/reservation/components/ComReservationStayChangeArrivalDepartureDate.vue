<template>
    <ComOverlayPanelContent title="Change Date" style="width: 40rem;" :loading="loading" @onSave="onSave" @onCancel="onClose">
        <div class="grid py-2 wp-number-cus">
            <div class="col-6">
                <label>Arrival Date</label>
                <Calendar panelClass="no-btn-clear" showButtonBar hideOnDateTimeSelect :disabled="(stay.can_arrival) || (rs.reservationStay.reservation_status == 'In-house')" selectOtherMonths showIcon v-model="stay.arrival_date"  :min-date="new Date(moment(stay.min_date))" @update:modelValue="onStartDate" dateFormat="dd-mm-yy" class="w-full"/>
            </div>
            <div class="col-6">
                <label>Arrival Time</label>
                <Calendar panelClass="no-btn-clear" showButtonBar :disabled="(rs.reservationStay.reservation_status == 'In-house')" selectOtherMonths class="w-full" v-model="stay.arrival_time" timeOnly />
            </div>
            <div class="col-6">
                <label>Departure Date</label>
                <Calendar panelClass="no-btn-clear" showButtonBar selectOtherMonths hideOnDateTimeSelect showIcon v-model="stay.departure_date"  :min-date="new Date(moment(stay.arrival_date).add(1,'days'))" @update:modelValue="onEndDate" dateFormat="dd-mm-yy" class="w-full"/>
            </div>
            <div class="col-6">
                <label>Departure Time</label>
                <Calendar panelClass="no-btn-clear" showButtonBar selectOtherMonths class="w-full" v-model="stay.departure_time" timeOnly /> 
            </div>
            <div class="col-6">
                <label>Nights</label>
                <InputNumber v-model="stay.room_nights" @update:modelValue="onNight($event)" inputId="stacked-buttons" showButtons :min="1" class="w-full nig_in-put"/>
            </div>
        </div>
    </ComOverlayPanelContent>
</template>
<script setup>
import { ref,inject,postApi } from '@/plugin'
const moment = inject("$moment")
const rs = inject("$reservation_stay")
const gv = inject("$gv")
const emit = defineEmits("onClose")
const workingDay = JSON.parse(localStorage.getItem("edoor_working_day"))
const loading = ref(false)
const stay = ref({
    room_nights: rs.reservationStay.room_nights,
    min_date: workingDay.date_working_day,
    can_arrival: (moment(workingDay.date_working_day).isAfter(rs.reservationStay.arrival_date) ? true : false),
    arrival_date: moment(rs.reservationStay.arrival_date).toDate(),
    departure_date: moment(rs.reservationStay.departure_date).toDate(),
    arrival_time: moment(rs.reservationStay.arrival_date + " " +  rs.reservationStay.arrival_time).toDate(),
    departure_time:moment(rs.reservationStay.departure_date + " " +  rs.reservationStay.departure_time).toDate(),

})
function onClose(){
    emit('onClose')
}
function onNight(newValue){
    stay.value.departure_date = moment(stay.value.arrival_date).add(newValue,'days').toDate()
}
function onEndDate(newValue){
    stay.value.departure_date = moment(newValue).toDate()
    stay.value.room_nights = moment(stay.value.departure_date).diff(moment(stay.value.arrival_date), 'days') 
}
function onStartDate(newValue){
    if(moment(newValue).isSame(stay.value.departure_date) || moment(newValue).isAfter(stay.value.departure_date)){
        stay.value.departure_date = moment(newValue).add(1,'days').toDate()
    }
    stay.value.room_nights = moment(stay.value.departure_date).diff(moment(newValue), 'days')
}
function onSave(){
    const data = {
        reservation_stay: rs.reservationStay.name,
        arrival_date: gv.dateApiFormat(stay.value.arrival_date),
        departure_date: gv.dateApiFormat(stay.value.departure_date),
        arrival_time:moment(stay.value.arrival_time).format("HH:mm:ss"),
        departure_time:moment(stay.value.departure_time).format("HH:mm:ss"),

    }
    loading.value = true
    postApi("reservation.change_reservation_stay_min_max_date",data).then((r)=>{
        if(r.message){
            loading.value = false
            rs.getReservationDetail(r.message.name)
            window.postMessage({"action":"Dashboard"},"*")
            window.postMessage({action:"ReservationList"},"*")
            window.postMessage({action:"ReservationStayList"},"*")
            window.postMessage({action:"ReservationStayDetail"},"*")
            window.socket.emit("ReservationDetail", rs.reservationStay.reservation)
            window.postMessage({action:"Frontdesk"},"*")
            window.postMessage({action:"Reports"},"*")
            setTimeout(function(){
                window.socket.emit("ComIframeModal", window.property_name)
            }, 3000)
  
            onClose()
        }    
    }).catch((err)=>{
        loading.value = false
    })
}
</script>