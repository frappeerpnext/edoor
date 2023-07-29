<template>
    <ComOverlayPanelContent title="Change Color" :loading="loading" @onSave="onSave" @onCancel="emit('onClose')">
        <div> 
            <ComColorPicker v-model="color"/>
        </div>
    </ComOverlayPanelContent>
</template>     
<script setup>
import { ref, inject, postApi } from "@/plugin"
import ComOverlayPanelContent from '@/components/form/ComOverlayPanelContent.vue';
const emit = defineEmits(['onClose'])
const rs = inject('$reservation');
const loading = ref(false)
const reservation = ref(JSON.parse(JSON.stringify(rs.reservation)))
const color = ref(reservation.value.reservation_color)
function onSave(){
    loading.value = true
    reservation.value.reservation_color = color.value 
    postApi('reservation.update_reservation_color',{data: reservation.value}).then((r)=>{
        rs.reservation = r.message
        loading.value = false
        emit('onClose')
    }).catch(()=>{
        loading.value = false
    })
}
</script>
