<template>
    <Badge :value="total"></Badge>
</template>
<script setup>
import { onMounted,ref,onUnmounted,postApi } from "@/plugin"
const props = defineProps({
    attacheds: [String,Array]
})
const total = ref(0)
window.socket.on("RefreshData", (arg) => {
    if (arg.action== "refresh_document") {
        getTotalDocument()
    }
})

function getTotalDocument(){ 
    var attacheds = props.attacheds.join("','") 
    postApi("reservation.get_document_count",{attacheds: `'${attacheds}'`},'',false).then((r)=>{
        total.value = r.message
    })
}
onMounted(() => {
    if(props.attacheds){
        getTotalDocument()
    }
        
})

</script>
 