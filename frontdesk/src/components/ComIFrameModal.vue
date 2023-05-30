<template>
    <iframe style="height: 500px;" width="100%" :src="url"></iframe>
</template>
<script setup>
import { ref, onMounted, inject } from "@/plugin"
const dialogRef = inject("dialogRef");

const setting = JSON.parse(localStorage.getItem("edoor_setting"))
const serverUrl = window.location.protocol + "//" + window.location.hostname + ":" + setting.backend_port;
const url = ref("")

onMounted(() => {
    if (!dialogRef) {
        alert("no dialog")
    } else {
        let view = ""
        let show_toolbar = 0
       
        if(!dialogRef.value.data.view){
            url.value = serverUrl + "/printview?doctype=" + dialogRef.value.data.doctype + "&name=" + dialogRef.value.data.name + "&format=" + dialogRef.value.data.report_name + "&no_letterhead=0&letterhead=No%20Letterhead&settings=%7B%7D&_lang=en&view=ui&show_toolbar=0" 
       
        }else {
            url.value = serverUrl + "/printview?doctype=" + dialogRef.value.data.doctype + "&name=" + dialogRef.value.data.name + "&format=" + dialogRef.value.data.report_name + "&no_letterhead=0&letterhead=No%20Letterhead&settings=%7B%7D&_lang=en"
       
        }

        const params = dialogRef.value.data.extra_params
        if (params) {
            params.forEach(p => {
                url.value = url.value + "&" + p.key + "=" + p.value
            });
        }
    }
});
</script> 