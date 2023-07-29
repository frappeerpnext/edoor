<template>
    <ComOverlayPanelContent title="Change Color" :loading="loading" @onSave="onSave" @onCancel="emit('onClose')">
        <div>
            <ComColorPicker v-model="color"/>
        </div>
    </ComOverlayPanelContent>
</template>     
<script setup>
import { ref, useToast, inject, postApi } from "@/plugin"
import ComOverlayPanelContent from '@/components/form/ComOverlayPanelContent.vue';
const emit = defineEmits(['onClose'])
const rs = inject('$reservation_stay');
const loading = ref(false)
const stay = ref(JSON.parse(JSON.stringify(rs.reservationStay)))
const color = ref(stay.value.reservation_color)
function onSave(){
    loading.value = true
    stay.value.reservation_color = color.value
    postApi('reservation.update_reservation_color',{data: stay.value}).then((r)=>{
        rs.reservationStay = r.message
        loading.value = false
        emit('onClose')
    }).catch(()=>{
        loading.value = false
    })
}
</script>
