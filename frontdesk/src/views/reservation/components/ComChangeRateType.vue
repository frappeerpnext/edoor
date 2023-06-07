<template>
    <ComOverlayPanelContent :loading="isLoading" @onSave="onSave" @onCancel="emit('onClose')">
        <h1>Change Rate Type</h1>
       
        <ComSelect v-model="ratetype" placeholder="Rate Type" doctype="Rate Type"
            class="auto__Com_Cus w-full" />
    </ComOverlayPanelContent>
</template>     
<script setup>
import { ref, inject,updateDoc } from "@/plugin"
import ComOverlayPanelContent from '@/components/form/ComOverlayPanelContent.vue';
const frappe = inject('$frappe');
const call = frappe.call();



const emit = defineEmits(['onClose','onSave'])
const props = defineProps({
    ratetype: {
        type: String,
        default: ''
    },
    reservation: {
        type: String,
        default: ''
    },

})
// const changrate={
//     reservation_stay:''
// }

const ratetype = ref(props.ratetype)


const isLoading = ref(false)

function onSave() {
    //call.post('edoor.api.reservation.change_rate_type',)
}
</script>
