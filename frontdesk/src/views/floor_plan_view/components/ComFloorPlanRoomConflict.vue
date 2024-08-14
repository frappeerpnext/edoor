<template>
  <div class="line-height-1 text-white p-2">
      <div v-tippy="{ content:'Room Conflict', placement: 'left' }" class="flex absolute right-1 top-1">
          <i   class="pi pi-exclamation-circle text-xl" />
      </div>
      <div class="text-lg  font-medium">{{ room?.room_type_alias }} - {{ room.room_number }}</div>
      <div>
        <div  
    
    @mouseenter="(event) => showTooltip(event, d)"
 @click="onViewReservationStay(d.reservation_stay)"  class="mt-1 border-round-sm p-2 cursor-pointer relative" v-for="d in room.stay" :key="d.stay_room_id" :style="{ background: d.status_color || '#ccc' }" >
      {{ d.guest_name }}
      <div class="flex absolute right-1 top-1">
<div v-tippy="{ content: 'Arrival', placement: 'left' }" v-if="d?.is_arrival" style="background-color: #4299e1;" class="text-center border-1 overflow-hidden border-round-lg p-1">
  <ComIcon   icon="iconArrival" height="12px" />
</div>
<div v-tippy="{ content: 'Departure', placement: 'left' }" v-if="d?.is_departure" style="background-color: #878787;" class="text-center border-1 overflow-hidden border-round-lg p-1">
  <ComIcon   icon="icondeparture" height="12px" />
</div>
<div v-tippy="{ content: 'Stay Over', placement: 'left' }" v-if="d?.is_stay_over" style="background-color: #00b3b6;" class="text-center border-1 overflow-hidden border-round-lg p-1">
  <ComIcon   icon="iconstayover" height="12px" />
</div>
      </div>
      <div class="mt-1">
        <i v-tippy="{ content: d?.reservation_type, placement: 'left' }" :class="d?.reservation_type == 'FIT' ? 'pi-user' : 'pi-users'" class="pi me-1"></i>  
              <span>{{d?.adult}}</span>/<span>{{d?.child}}</span> 
              <span class="my-2">
                |
              </span>
              
              <i class="pi pi-calendar me-1"></i>  
              <span>{{d?.room_nights}}</span> 
          </div> 
        </div>
      </div>
</div> 
</template>
<script setup>
import { useTippy } from "vue-tippy";
import { h, ref } from "@/plugin"

import ComTooltip from "@/views/floor_plan_view/components/ComTooltip.vue"
const props = defineProps({
    stay: {
      type: Object,
      required: true
    },
    room: {
      type: Object,
      required: true
    }
  });
  function onViewReservationStay(reservation) {
      window.postMessage('view_reservation_stay_detail|' + reservation, '*')
}
const tippy = ref([])
function showTooltip(event,stay) {
  
  if (!props.editMode ) {
    tippy.value = useTippy(event.target, {
      content: h(ComTooltip, { data: [stay] }),
      interactive: true, 
      maxWidth: 'none',
    });
  }
  return;
}




</script>
<style scoped>
 .tippy-content {
  z-index: 999999 !important;
}
</style>