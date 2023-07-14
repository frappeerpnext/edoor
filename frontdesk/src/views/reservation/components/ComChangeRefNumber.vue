<template>
    <ComOverlayPanelContent title="Ref / Internal Number" :loading="isLoading" @onSave="onSave" @onCancel="emit('onClose')">
 
        <div class="flex gap-2 my-2">
            <InputText v-model="data.reference_number"/>
            <InputText v-model="data.internal_reference_number" />
        </div>
    </ComOverlayPanelContent>
</template>     
<script setup>

import { ref, inject, updateDoc,onMounted } from "@/plugin"
import ComOverlayPanelContent from '@/components/form/ComOverlayPanelContent.vue';
const emit = defineEmits(['onClose'])
const props = defineProps({
    doctype: String
})
const isLoading = ref(false)
const rs = inject('$reservation_stay');
const r = inject('$reservation');
const data = ref({})
onMounted(() => {
    if(props.doctype == 'Reservation Stay'){
        data.value = JSON.parse(JSON.stringify(rs.reservationStay))
    }else{
        data.value = JSON.parse(JSON.stringify(r.reservation))
    }
})



const onSave = () => {
    isLoading.value = true;
    console.log(data.value)
    updateDoc(props.doctype, data.value.name, data.value).then((doc) => {
        isLoading.value = false;
        emit("onClose", doc)
    }).catch((ex) => {
        isLoading.value = false;
    })
}



</script>
