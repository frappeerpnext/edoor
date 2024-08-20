<template>
  <ComDialogContent hideButtonClose :titleButtonOK="Ok" :hideIcon="false"  @onOK="onOK">
    <Message>{{ $t('Please Select Stay For Assign To Room') }}  : {{room?.room_type}} - {{room?.room_number}}</Message>
    <hr class="my-2">
    <InputText type="text" v-model="keyword" class="p-inputtext-sm w-full" :placeholder="$t('Search Guest Name')" @input="onSearch" :maxlength="50" />
    <hr class="my-2"> 
    <div class="grid p-2 overflow-auto" :style="isMobile ? { height: '50vh' } : {}" :class="unassignReservations.filter(r => r.guest_name.toLowerCase().includes(keywordforsearch.toLowerCase())).length > 0 ? '' : 'justify-content-center'">
      <ComPlaceholder :text=" $t('No Guest')  + '  `  ' + keyword + '  `  '  +  $t('Name')" :loading="loading" :is-not-empty="unassignReservations.filter(r => r.guest_name.toLowerCase().includes(keywordforsearch.toLowerCase())).length > 0">
       
      <div  class="col-12 lg:col-3 p-1" v-for="(s, index) in  unassignReservations.filter(r => r.guest_name.toLowerCase().includes(keywordforsearch.toLowerCase()))" :key="index">

        <div @click="onSelect(s)" :class="s.selected ? 'border-green-400' : ''" class="border-2 w-full h-full bg-gray-100 border-round-lg p-2 cursor-pointer">
          <div class="bg-slate-200 p-2 font-medium text-center border-left-2">
          {{ s?.guest_name }}  
          </div>
          <table class="w-full">
            <ComStayInfoNoBox titleClass="bg-white" valueClass="bg-white" label="Reservation Stay" v-if="s.reservation" :value="s.reservation" />
            <ComStayInfoNoBox titleClass="bg-white" valueClass="bg-white" label="Room Type" v-if="s.room_type" :value="s.room_type" />
            <ComStayInfoNoBox titleClass="bg-white" valueClass="bg-white" label="Stay" v-if="s.reservation_stay" :value="s.reservation_stay" />
            <ComStayInfoNoBox titleClass="bg-white" valueClass="bg-white" label="Arrival" v-if="s?.arrival_date" :value="gv.dateFormat(s?.arrival_date)" />
            <ComStayInfoNoBox titleClass="bg-white" valueClass="bg-white" label="eparture" v-if="s?.departure_date" :value="gv.dateFormat(s?.departure_date)" />
            <ComStayInfoNoBox titleClass="bg-white" valueClass="bg-white" label="Business Source" v-if="s?.business_source" :value="s?.business_source" />
            <ComStayInfoNoBox titleClass="bg-white" valueClass="bg-white" label="Rate Type" v-if="s?.rate_type" :value="s?.rate_type" />
        </table>
            <Button class="mt-2 w-full text-center text-color bg-white" >
              <span class="w-full">Assign Stay To Room</span>
            </Button>
        </div>
            
      </div>
      </ComPlaceholder> 
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
const isMobile = ref(window.isMobile)
import { i18n } from "@/i18n";
const moment = inject("$moment")

const { t: $t } = i18n.global;
function debouncer(fn, delay) {

var timeoutID = null;
return function () {
    clearTimeout(timeoutID);
    var args = arguments;
    var that = this;
    timeoutID = setTimeout(function () {
        fn.apply(that, args);
    }, delay);
};
}

const keyword = ref(''); 
const keywordforsearch = ref(''); 
const onSearch = debouncer(() => {
  keywordforsearch.value = keyword.value
}, 500);
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