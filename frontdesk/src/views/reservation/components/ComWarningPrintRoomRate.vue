<template>
  
    <Message severity="warn" v-if="display!='toast'">
        <h1>Attention!</h1>
        <p>
            This reservation has been mark room rate as hidden. Please ensure that this rate is not printed to the guest.
        </p>
    </Message>

</template>
<script setup>
import { ref,  onMounted,useToast } from "@/plugin"
const toast = useToast();
const props = defineProps({
    display:String
})
const doc = ref()
onMounted(() => {
   
        if (props.display=="toast" ){
            toast.add({ severity: 'warn', summary: "Attention", detail: "This reservation has been mark room rate as hidden. Please ensure that this rate is not printed to the guest.", life: 1000*15 })
            
        }
 
})
</script>