<template>
    <ComOverlayPanelContent title="Change Pax" :loading="isLoading" @onSave="onSave" @onCancel="emit('onClose')">
        <Message v-if="stay.reservation_status=='In-house'">{{ $t("Change pax is affect to future stay only") }}</Message>
        <div class="wp-number-cus my-2">
        <div class="flex flex-col">
        <label>{{$t('Adults')}}</label>
        <InputNumber v-model="stay.adult" inputId="stacked-buttons" showButtons :min="1" :max="100"
            class="child-adults-txt" />
        </div>
        <div class="">
        <h2> {{$t('Children')}} </h2>
        <div class="grid">
                <div class="col-6 flex flex-column" v-for="v in list_occupancy_code">
                    <label>{{ $t(v.title) }}</label>
                    <InputNumber v-model="stay.child" inputId="stacked-buttons" showButtons :min="0" :max="100"
                        class="child-adults-txt" />
                </div>
        </div>
        {{ list_occupancy_code }}
        </div>
        
       
        </div>
    </ComOverlayPanelContent>
</template>     
<script setup>

import { ref, inject,postApi,onMounted,getApi,getDocList } from "@/plugin"
import ComOverlayPanelContent from '@/components/form/ComOverlayPanelContent.vue';
import {i18n} from '@/i18n';
import Message from "primevue/message";
const { t: $t } = i18n.global;
const emit = defineEmits(['onClose'])
const rs = inject('$reservation_stay');
const isLoading = ref(false)
const stay = ref(JSON.parse(JSON.stringify(rs.reservationStay)))
const list_occupancy_code = ref([])
const onSave = () => {
    isLoading.value = true;
 
    postApi("reservation.change_pax",{data:{
        stay_name:stay.value.name,
        adult:stay.value.adult,
        child:stay.value.child
    }}).then(result=>{
        
      
        isLoading.value = false;
        rs.reservationStay.adult = stay.value.adult
        rs.reservationStay.child = stay.value.child
        
       
        window.postMessage({action:"ReservationList"},"*")
        window.postMessage({action:"ReservationStayList"},"*")
        window.postMessage({action:"ReservationStayDetail"},"*")
        window.postMessage({action:"ReservationDetail"},"*")
        emit("onClose")
        

    }).catch((ex) => {
        isLoading.value = false;
    })
    
}
async function loadOccupancyCodes() {


    
  const occupancyCodes = await getDocList("Occupancy Code", {
    fields: ["name", "title"],
    filters: { is_child: 1 }
  })
  const occupancyStayCodes = await getDocList("Reservation Stay Occupancy", {
    fields: ["name","occupancy_code","total"],
    filters: { reservation_stay: stay.value.name }
  })
  console.log(occupancyCodes)
  let allowedCodes = []
  allowedCodes = await getApi(
  'reservation.get_room_type_occupancy_codes',
  { room_type_id: stay.value.stays[0]?.room_type_id }
)
  
  allowedCodes = allowedCodes.message || []
  const allowedSet = new Set(allowedCodes.map(c => c.name))
    list_occupancy_code.value = occupancyCodes
  .filter(o => allowedSet.has(o.occupancy_code)) 
  .map(o => ({ 
    ...o, 
    value:0
  }))
  
}
onMounted(async () => {
  await loadOccupancyCodes()
})


</script>
