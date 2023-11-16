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
const color = ref(reservation.value.group_color)
function onSave(){
    loading.value = true
    postApi('reservation.update_group_color',
        {
            data: {
                reservation:reservation.value.name, 
                group_color:color.value || ''
            }
        }).then((r)=>{
            rs.reservation = r.message
            loading.value = false
            rs.LoadReservation(reservation.value.name, false);
            emit('onClose')
    }).catch(()=>{
        loading.value = false
    })
}
</script>
