<template>
  <ComDialogContent hideButtonClose :titleButtonOK="Ok" :hideIcon="false" :loading="loading" @onOK="onOK">
    {{ room }}
    <hr>
    <div v-for="(s, index) in unassignReservations" :key="index">
      {{ s }}
      {{ s.start_date }} => {{ s.end_date }} {{ s.reservation_stay }} {{ s.guest_name }}
      <Button @click="onSelect(s)">Select {{ s.selected }}</Button>
    </div>

  </ComDialogContent>
</template>

<script setup>
import { ref, inject, onMounted, getApi, postApi } from "@/plugin";
const room = ref({})
const unassignReservations = ref([])
const loading = ref(false);
const dialogRef = inject("dialogRef");
const gv = inject("$gv")
import { i18n } from "@/i18n";
const moment = inject("$moment")

const { t: $t } = i18n.global;
function onSelect(stay) {
  const existing_stay = unassignReservations.value.find(r => r.selected == 1)
  if (existing_stay) {
    existing_stay.selected = 0
  }
  stay.selected = 1

}
function getUnassignRoomData(date) {
  loading.value = true
  getApi("frontdesk.get_unassign_room_by_date", {
    filters: {
      date: date,
      property: window.property_name
    }
  }).then(result => {
    unassignReservations.value = result.message
    loading.value = false
  })
    .catch(error => {
      loading.value = false
    })
}

function onOK() {
  const stay = unassignReservations.value.find(r => r.selected == 1)
  if (!stay) {
    gv.toast('warn', $t("Please select a reservation to assign room"))

  }
  const data =
  {
    "room_type_id": room.value.room_type_id,
    "old_room_type_id": stay.room_type_id,
    "room_type": stay.room_type,
    "room_id": room.value.name,
    "start_date": stay.arrival_date,
    "end_date": stay.departure_date,
    "rate": stay.input_rate,
    "old_rate": stay.input_rate,
    "rate_type": stay.rate_type,
    "business_source": stay.business_source,
    "stay_room": stay.stay_room_id,
    "is_manual_rate": stay.is_manual_rate,
    "reservation_stay": stay.reservation_stay
  }

  loading.value = true 
  postApi("reservation.assign_room",{data:data}).then(result=>{
    loading.value = false
    window.postMessage({action:"FloorPlanView"},"*")
    dialogRef.value.close()

  }).catch(error=>{
    loading.value = false
  })

}

onMounted(() => {
  room.value = dialogRef.value.data.room

  getUnassignRoomData(dialogRef.value.data.date)
})



</script>