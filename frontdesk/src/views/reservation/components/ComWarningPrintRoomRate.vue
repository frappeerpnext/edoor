<template>
  
    <Message severity="warn" v-if="doc && doc?.show_room_rate_in_guest_folio_invoice == 0 && display!='toast'">
        <h1>Attention!</h1>
        <p>
            This reservation is from {{ doc.business_source }}, and the room rate is hidden. Please ensure that this rate
            is not printed to the guest.
        </p>
    </Message>

</template>
<script setup>
import { ref, getDoc, onMounted,useToast } from "@/plugin"
const toast = useToast();
const props = defineProps({
    reservation: String,
    display:String
})
const doc = ref()
onMounted(() => {
    getDoc("Reservation", props.reservation).then(d => {
        
        doc.value = d
        if (props.display=="toast" && d.show_room_rate_in_guest_folio_invoice==0){
            toast.add({ severity: 'warn', summary: "Attention", detail: "This reservation is from " + d.business_source + ", and the room rate is hidden. Please ensure that this rate is not printed to the guest.", life: 1000*30 })
            
        }
    })
})
</script>