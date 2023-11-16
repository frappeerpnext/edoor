<template>

    <Badge :value="total"></Badge>
    
</template>
<script setup>
import { onMounted,ref,onUnmounted,getCount } from "@/plugin"
const props = defineProps({
    attacheds: [String,Array],
    doctype: String,
    doctypes:Array,
    docname:String
})
const total = ref(0)


function getTotalDocument(){ 
    let dataFilter = []
    let ref_doctypes = [props.doctype]
    ref_doctypes = ref_doctypes.concat(props.doctypes || [])

    dataFilter.push(['attached_to_doctype','in',ref_doctypes])
    dataFilter.push(['attached_to_name','in',props.attacheds])
    dataFilter.push(["custom_show_in_edoor","=",1])


    getCount('File', dataFilter, true)
  .then((count) =>  total.value = count)
  
}

const actionHandler = async function (e) {
 

       if (e.isTrusted ) {
        if(e.data.action=='refresh_document_count'){
            getTotalDocument()
        }
   }
}
onMounted(() => {
    window.addEventListener('message', actionHandler, false);
    if(props.attacheds){
        getTotalDocument()
    }
        
})
onUnmounted(() => {
    window.removeEventListener('message', actionHandler, false);
   
})

</script>
 