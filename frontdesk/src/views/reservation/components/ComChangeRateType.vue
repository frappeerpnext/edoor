<template>
    <ComOverlayPanelContent style="min-width:15rem;" title="Change Rate Type" :loading="isLoading" @onSave="onSave" @onCancel="emit('onClose')">
        <div class="my-2" style="min-width:10rem;">
        <ComSelect v-model="rateType" placeholder="Rate Type" doctype="Rate Type"
            class="auto__Com_Cus w-full" />
        <div class="flex gap-2 flex-col mt-3">
            <div class="flex gap-2">
        <Checkbox inputId="apply-all" v-model="applyToAllStay" :binary="true"/>
        <label for="apply-all" class="cursor-pointer">Apply to All Stay</label>       
            </div>
            <div class="flex gap-2">
        <Checkbox inputId="apply-all-stay" v-model="regenerateNewRate" :binary="true"/>
        <label for="apply-all-stay" class="cursor-pointer">Regenerate New Rate</label>     
            </div>
        <Message severity="warn" v-if="regenerateNewRate">Generate new rate will be affect only active reservation and future stay</Message>
        </div>
        </div>
    </ComOverlayPanelContent>
</template>     
<script setup>
import { ref, inject,useToast,postApi } from "@/plugin"
import ComOverlayPanelContent from '@/components/form/ComOverlayPanelContent.vue';
import Checkbox from 'primevue/checkbox';
import Message from 'primevue/message';

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
const property = JSON.parse(localStorage.getItem("edoor_property"))
const isLoading = ref(false)

function onSave() {
    isLoading.value = true  
 
    postApi('reservation.change_rate_type',{
        property:property.name,
        reservation_stay : props.reservation_stay,
        reservation: props.reservation,
        rate_type : rateType.value,
        apply_to_all_stay : applyToAllStay.value,
        regenerate_new_rate : regenerateNewRate.value
    })
    .then((result) => {
        emit('onSave',result.message)
    })
    .catch((error) => {
        isLoading.value = false      
    })
}
</script>
