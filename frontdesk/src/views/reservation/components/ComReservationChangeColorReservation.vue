<template>
    <ComOverlayPanelContent title="Change Color" :loading="loading" @onSave="onSave" @onCancel="emit('onClose')">
        <div> 
            <ComColorPicker v-model="color"/>
        </div>
    </ComOverlayPanelContent>
</template>     
<script setup>
import { ref, useToast, inject, updateDoc } from "@/plugin"
import ComOverlayPanelContent from '@/components/form/ComOverlayPanelContent.vue';
const emit = defineEmits(['onClose'])
const toast = useToast()
const rs = inject('$reservation');
const loading = ref(false)
const gv = inject('$gv');
const reservation = ref(JSON.parse(JSON.stringify(rs.reservation)))
const color = ref(reservation.value.reservation_color)
function onSave(){
    loading.value = true
    reservation.value.reservation_color = color.value
    reservation.value.update_reservation = 1
    updateDoc('Reservation',reservation.value.name,reservation.value).then((r)=>{
        rs.reservation = r
        loading.value = false
        emit('onClose')
    }).catch(()=>{
        loading.value = false
    })
}
</script>
