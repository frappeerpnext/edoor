<template>
  <ComOverlayPanelContent :style="{width: isMobile ? '100%' : '40rem'}" :loading="loading" @onSave="onSave" @onCancel="onClose">
   <div class="grid py-2 wp-number-cus">
      <div class="col-6">
        <label>Arrival Time</label>
        <Calendar selectOtherMonths class="w-full" v-model="data.arrival_time" timeOnly />
      </div>
      <div class="col-6">
        <label>Departure Time</label>
        <Calendar selectOtherMonths class="w-full" v-model="data.departure_time" timeOnly />
      </div>
    </div>
  </ComOverlayPanelContent>
</template>
<script setup>
import { ref, inject, postApi, useToast } from "@/plugin"

const isMobile = ref(window.isMobile)
const rs = inject("$reservation")
const moment = inject("$moment")
const loading = ref(false)
const emit = defineEmits("onClose")
const toast = useToast();
const workingDay = JSON.parse(localStorage.getItem("edoor_working_day"))
const data = ref({
  min_date: workingDay.date_working_day,
  can_arrival: (moment(workingDay.date_working_day).isAfter(rs.reservation.arrival_date) ? true : false),
  arrival_time: moment(rs.reservation.arrival_date + " " + rs.reservation.arrival_time).toDate(),
  departure_time: moment(rs.reservation.departure_date + " " + rs.reservation.departure_time).toDate(),
  generate_new_stay_rate_by: "stay_rate"
})
data.value.room_nights = moment(data.value.departure_date).diff(moment(data.value.arrival_date), 'days')

function onClose() {
  emit('onClose')
}
function onSave() {
  loading.value = true
  const active_reservations = rs.roomList.filter(r => r.is_active_reservation == 1 && r.allow_user_to_edit_information == 1)

  if (active_reservations.length == 0) {
    toast.add({ severity: 'warn', summary: "Change Stay", detail: "There is no active reservation to change stay", life: 5000 })
    loading.value = false
    return
  }
  postApi("group_operation.group_change_arrival_time", {
    data: {
      reservation: rs.reservation.name,
      arrival_time: moment(data.value.arrival_time).format('HH:mm:ss'),
      departure_time:moment(data.value.departure_time).format('HH:mm:ss'),
      
    }
  }).then((result) => {
    loading.value = false
        emit("onClose" ) 
        window.postMessage({action:"Reports"},"*")
        window.postMessage({action:"ComIframeModal"},"*")
        window.postMessage({"action":"Dashboard"},"*")
        window.postMessage({"action":"ReservationStayDetail"},"*")
        window.postMessage({"action":"ReservationDetail"},"*") 
  }).catch((err) => {
    loading.value = false
  })


}
</script>