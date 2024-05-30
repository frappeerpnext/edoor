<template>
    <ComOverlayPanelContent title="Change Pax" :loading="isLoading" @onSave="onSave" @onCancel="emit('onClose')">
        
        <div class="wp-number-cus flex gap-3 my-2">
        <div class="flex flex-col">
        <label>{{$t('Adults')}}</label>
        <InputNumber v-model="stay.adult" inputId="stacked-buttons" showButtons :min="1" :max="100"
            class="child-adults-txt" />
        </div>
        <div class="flex flex-col">
        <label>{{$t('Children')}}</label>
        <InputNumber v-model="stay.child" inputId="stacked-buttons" showButtons :min="0" :max="100"
            class="child-adults-txt" />
        </div>
       
        </div>
    </ComOverlayPanelContent>
</template>     
<script setup>

import { ref, inject,postApi } from "@/plugin"
import ComOverlayPanelContent from '@/components/form/ComOverlayPanelContent.vue';
import {i18n} from '@/i18n';
const { t: $t } = i18n.global;
const emit = defineEmits(['onClose'])
const rs = inject('$reservation_stay');
const isLoading = ref(false)
const stay = ref(JSON.parse(JSON.stringify(rs.reservationStay)))
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



</script>
