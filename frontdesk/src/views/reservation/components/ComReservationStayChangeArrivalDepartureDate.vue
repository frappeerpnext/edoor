<template>
    <ComOverlayPanelContent title="Change Date" :loading="loading" @onSave="onSave" @onCancel="onClose">
        <div class="flex gap-2 my-2">
            <Calendar hideOnDateTimeSelect :disabled="stay.can_arrival" showIcon v-model="stay.arrival_date"  :min-date="new Date(moment(stay.min_date).add(1,'days'))" @update:modelValue="onStartDate" dateFormat="dd-mm-yy" class="w-full"/>
            <div>
                <InputNumber v-model="stay.room_nights" @update:modelValue="onNight($event)" inputId="stacked-buttons" showButtons :min="1" class="w-full nig_in-put"/>
            </div>
            <Calendar hideOnDateTimeSelect showIcon v-model="stay.departure_date"  :min-date="new Date(moment(stay.arrival_date).add(1,'days'))" @update:modelValue="onEndDate" dateFormat="dd-mm-yy" class="w-full"/>
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
    can_arrival: (moment(workingDay.date_working_day).isSame(rs.reservationStay.arrival_date) || moment(workingDay.date_working_day).isAfter(rs.reservationStay.arrival_date) ? true : false),
    arrival_date: moment(rs.reservationStay.arrival_date).toDate(),
    departure_date: moment(rs.reservationStay.departure_date).toDate()
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
        departure_date: gv.dateApiFormat(stay.value.departure_date)
    }
    loading.value = true
    postApi("reservation.change_reservation_stay_min_max_date",data).then((r)=>{
        console.log(r.message)
        if(r.message){
            loading.value = false
            rs.getReservationDetail(r.message.name)
            onClose()
        }
    }).catch((err)=>{
        loading.value = false
    })
}
</script>