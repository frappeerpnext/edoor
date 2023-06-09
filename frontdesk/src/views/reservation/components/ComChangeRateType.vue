<template>
    <ComOverlayPanelContent title="Change Rate Type" :loading="isLoading" @onSave="onSave" @onCancel="emit('onClose')">
        <div class="my-3">
        <ComSelect v-model="rateType" placeholder="Rate Type" doctype="Rate Type"
            class="auto__Com_Cus w-full" />
        <br>
        <Checkbox v-model="applyToAllStay" :binary="true"/>
        <span>Apply to all stay</span><br>
        <Checkbox v-model="regenerateNewRate" :binary="true"/>
        <span>Regenerate New Rate</span>
        <Message severity="warn" v-if="regenerateNewRate">Generate new rate will be affect only active reservation and future stay</Message>
        </div>
    </ComOverlayPanelContent>
</template>     
<script setup>
import { ref, inject,updateDoc,useToast } from "@/plugin"
import ComOverlayPanelContent from '@/components/form/ComOverlayPanelContent.vue';
import Checkbox from 'primevue/checkbox';
import Message from 'primevue/message';
const frappe = inject('$frappe');
const call = frappe.call();
const toast = useToast()

const emit = defineEmits(['onClose','onSave'])
const props = defineProps({
    rate_type: {
        type: String,
        default: ''
    },
    reservation: {
        type: String,
        default: ''
    },
    reservation_stay: {
        type: String,
        default: ''
    },

})

const rateType = ref(props.rate_type);
const applyToAllStay = ref(false);
const regenerateNewRate = ref(false);

const isLoading = ref(false)

function onSave() {
    isLoading.value = true  
    call
    .post('edoor.api.reservation.change_rate_type',{
        reservation_stay : props.reservation_stay,
        rate_type : rateType.value,
        apply_to_all_stay : applyToAllStay.value,
        regenerate_new_rate : regenerateNewRate.value
    })
    .then((result) => {
        emit('onSave',result.message)
        toast.add({ severity: 'success', summary: 'Change Rate Type', detail: "Change rate type successfully", life: 3000 })
    })
    .catch((error) => {
        isLoading.value = false      
    })
}
</script>
