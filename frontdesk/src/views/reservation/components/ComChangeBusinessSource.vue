<template>
    <ComOverlayPanelContent title="Change Business Source" :loading="isLoading" @onSave="onSave" @onCancel="emit('onClose')">
        <div class="my-2">
        <ComAutoComplete v-model="businessSource" placeholder="Business Source" doctype="Business Source"
            class="auto__Com_Cus w-full" />
        </div>
        <div class="flex gap-2 my-2">
            <Checkbox inputId="apply-all-stay" v-model="regenerateNewRate" :binary="true" />
            <label for="apply-all-stay" class="cursor-pointer">Regenerate New Rate</label>
        </div>
        <Message severity="warn" v-if="regenerateNewRate">Generate new rate will be affect only active reservation,<br> future stay and room that use rate plan</Message> 

    </ComOverlayPanelContent>
</template>     
<script setup>
import { ref, inject,postApi } from "@/plugin"
import ComOverlayPanelContent from '@/components/form/ComOverlayPanelContent.vue';



const emit = defineEmits(['onClose','onSave'])
const props = defineProps({
    businessSource: {
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

const businessSource = ref(props.businessSource)
const regenerateNewRate= ref(false)

const isLoading = ref(false)

function onSave() {
    isLoading.value = true
    postApi('reservation.update_business_source',{
        business_source: businessSource.value,
        reservation:props.reservation,
        regenerate_rate:regenerateNewRate.value,
        reservation_stay: props.reservation_stay,
    })
    .then((doc) => {
        if(props.reservation_stay){ 
            emit('onSave',{reservation_stay:doc.message})
        }else {
            emit('onSave',{reservation:doc.message})
        }
    })
    .catch(()=>{
        isLoading.value = false      
    })
}
</script>
