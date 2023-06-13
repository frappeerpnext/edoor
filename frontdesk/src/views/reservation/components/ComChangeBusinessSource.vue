<template>
    <ComOverlayPanelContent title="Change Business Source" :loading="isLoading" @onSave="onSave" @onCancel="emit('onClose')">
        <div class="my-2">
        <ComAutoComplete v-model="businessSource" placeholder="Business Source" doctype="Business Source"
            class="auto__Com_Cus w-full" />
        </div>
    </ComOverlayPanelContent>
</template>     
<script setup>
import { ref, inject,updateDoc } from "@/plugin"
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

})

const businessSource = ref(props.businessSource)


const isLoading = ref(false)

function onSave() {

    isLoading.value = true
    updateDoc('Reservation', props.reservation, {
        business_source: businessSource.value,
    })
    .then((doc) => {
      
        emit('onSave',doc)
    })
    .catch((error)=>{
        isLoading.value = false      
    })
}
</script>
