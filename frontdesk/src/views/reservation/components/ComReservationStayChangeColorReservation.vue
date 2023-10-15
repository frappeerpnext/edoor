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
const rs = inject('$reservation_stay');
const gv = inject('$gv');
const loading = ref(false)
const stay = ref(JSON.parse(JSON.stringify(rs.reservationStay)))
const color = ref(stay.value.reservation_color)
function onSave(){
    if(!stay.value.is_active_reservation){
        gv.toast('warn','Cannot change color on unactive reservation.')
        return
    }
    loading.value = true
    stay.value.reservation_color = color.value || ''
    postApi('reservation.update_reservation_color',{data: stay.value}).then((r)=>{
        rs.reservationStay = r.message
        loading.value = false
        window.socket.emit("Dashboard", rs.reservationStay.property)
        window.socket.emit("ReservationStayList", { property:window.property_name})
        window.socket.emit("ReservationStayDetail", { reservation_stay:window.reservation_stay})
        emit('onClose')
    }).catch(()=>{
        loading.value = false
    })
}
</script>
