<template>
    <div class="iframe-view">
    <TabView  lazy>
        
        <TabPanel header="General Information">
            
            <iframe @load="onIframeLoaded('general')" id="general" style="width: 100%;"
                :src="generalInfoUrl">
            </iframe>
        </TabPanel>
        <TabPanel header="Stay History">
            <iframe  @load="onIframeLoaded('stay_history')" id="stay_history" style="width: 100%;"
                :src="stayHistoryUrl">
            </iframe>
        </TabPanel>
        <TabPanel header="POS/Misc. Sale">
            <div style="margin-right:-1rem;">
            <iframe style="height:500px; width: 100%;"
                :src="posMiscSaleUrl">
            </iframe>
            </div>
        </TabPanel>

        <TabPanel header="Note">
            <iframe @load="onIframeLoaded('note')" id="note" style="width: 100%;"
                :src="noteUrl">

            </iframe>
        </TabPanel>
        <TabPanel header="Folio">
            <iframe @load="onIframeLoaded('Folio')" id="Folio" style="width: 100%;"
                :src="folioUrl">
            </iframe>
        </TabPanel>
    </TabView></div>
    <Button class="border-none" label="Edit Guest" icon="pi pi-user-edit" @click="onEditGuest"/>
</template>
<script setup>

import { inject, ref, onMounted,computed,useDialog } from '@/plugin'
import ComAddGuest from '@/views/guest/components/ComAddGuest.vue';
const dialogRef = inject("dialogRef");
const setting =JSON.parse( localStorage.getItem("edoor_setting"))
const serverUrl = window.location.protocol + "//" + window.location.hostname + ":" + setting.backend_port;
const dialog = useDialog()
const name = ref("")

function onIframeLoaded(id){
 
 const iframe = document.getElementById(id);
iframe.height = iframe.contentWindow.document.body.scrollHeight;

}

const generalInfoUrl =  computed(() => {
    let url = serverUrl +  "/printview?doctype=Customer&name=" + name.value + "&format=eDoor%20Guest%20Detail%20General%20Information&no_letterhead=1&letterhead=No%20Letterhead&settings=%7B%7D&_lang=en&view=ui&show_toolbar=0"
    return url
})
const stayHistoryUrl =  computed(() => {
    let url = serverUrl +  "/printview?doctype=Customer&name=" + name.value + "&format=eDoor%20Guest%20Stay%20History&no_letterhead=1&letterhead=No%20Letterhead&settings=%7B%7D&_lang=en&view=ui&show_toolbar=0"
    return url
})
const posMiscSaleUrl =  computed(() => {
    let url = serverUrl +  "/printview?doctype=Customer&name=" + name.value + "&format=eDoor%20Guest%20POS%2FMisc.%20Sale&no_letterhead=1&letterhead=No%20Letterhead&settings=%7B%7D&_lang=en&view=ui&show_toolbar=0"
    return url
})
const noteUrl =  computed(() => {
    let url = serverUrl +  "/printview?doctype=Customer&name=" + name.value + "&format=eDoor%20Guest%20Note&no_letterhead=1&letterhead=No%20Letterhead&settings=%7B%7D&_lang=en&view=ui&show_toolbar=0"
    return url
})
const folioUrl =  computed(() => {
    let url = serverUrl +  "/printview?doctype=Customer&name=" + name.value + "&format=eDoor%20Reservation%20Folio&no_letterhead=1&letterhead=Defualt%20Letter%20Head&settings=%7B%7D&_lang=en&view=ui&show_toolbar=0"
    return url
})
function onEditGuest() { 
    dialog.open(ComAddGuest, {
        props: {
            header: `Edit Guest`,
            style: {
                width: '50vw',
            },
            breakpoints: {
                '960px': '75vw',
                '640px': '90vw'
            },
            modal: true,
            closeOnEscape: false,
            position: 'top'
        },
        data:{
            name: name.value,
        },
    });  
}
onMounted(() => {
    if (dialogRef.value) {
        name.value = dialogRef.value.data.name;
    } else {
        alert(111)
    }
});

console.log(dialogRef)
</script>
<style scoped>
.iframe-view{
    overflow: auto !important;
    max-height: 550px !important;
    min-height: 550px !important;
    margin-right: -1rem;
    padding-right: 1rem !important;
}
</style>