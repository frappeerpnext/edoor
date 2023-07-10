<template>
    <ComSelect doctype="Letter Head" v-if="show_letter_head" class="my-2"/>
  
    <iframe @load="onIframeLoaded()" id="iframe" style="min-height: 500px;" width="100%" :src="url"></iframe>
     
</template>
<script setup>
import { ref, onMounted, inject } from "@/plugin"
 
const dialogRef = inject("dialogRef");

const setting = JSON.parse(localStorage.getItem("edoor_setting"))
const serverUrl = window.location.protocol + "//" + window.location.hostname + ":" + setting.backend_port;
const url = ref("")
const show_letter_head = ref(false)
function onIframeLoaded(){
    const iframe = document.getElementById("iframe");

   iframe.height = iframe.contentWindow.document.body.scrollHeight;
}

onMounted(() => {
    if (!dialogRef) {
        alert("no dialog")
    } else {
        
        
        let show_toolbar = dialogRef.value.data.show_toolbar ||  1
      
       
        if(dialogRef.value.data.view){
            url.value = serverUrl + "/printview?doctype=" + dialogRef.value.data.doctype + "&name=" + dialogRef.value.data.name + "&format=" + dialogRef.value.data.report_name + "&no_letterhead=0&letterhead=No%20Letterhead&settings=%7B%7D&_lang=en&view=ui&show_toolbar=0" 
       
        }else {
            url.value = serverUrl + "/printview?doctype=" + dialogRef.value.data.doctype + "&name=" + dialogRef.value.data.name + "&format=" + dialogRef.value.data.report_name + "&no_letterhead=0&letterhead=No%20Letterhead&settings=%7B%7D&_lang=en&show_toolbar=1"
       
        }

        const params = dialogRef.value.data.extra_params
        if (params) {
            params.forEach(p => {
                url.value = url.value + "&" + p.key + "=" + p.value
            });
        }
 
        show_letter_head.value = dialogRef.value.data.show_letter_head || false


    }
});
</script> 