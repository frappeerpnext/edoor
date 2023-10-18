<template>
    <ComHeader isRefresh @onRefresh="onRefresh()">
        <template #start>
            <div class="flex">
                <div class="flex align-items-center">
                    <div @click="onRefresh()" class="text-2xl">Reports</div>
                </div>
                <div class="flex align-items-right">
                    <SplitButton class="border-split-none" label="Print" icon="pi pi-print" @click="onPrint" />
                </div>
            </div>
    <!-- <div class="wrap-dialog iframe-modal">
        <div class="p-3 view-table-iframe-dialog" style="height: 85vh;">
            <div class="grid mb-3 ">
                <div class="col flex gap-2 ">
                    <div>
                        <div @click="onRefresh()" class="text-2xl">Reports</div>
                    </div>
                </div>
                <div class="col flex gap-2 justify-end">
                    <div v-if="(view||'')!='ui'">
                        <SplitButton class="spl__btn_cs sp" @click="onPrint" label="Print" icon="pi pi-print" :model="items" />
                        
                    </div>
                </div>
            </div> 
           
        </div>
    </div> -->
            
        </template>
    </ComHeader>
    <Splitter class="mb-5" state-key="report_spliter_state" state-storage="local">
        <SplitterPanel :size="25" class="pa-4">
            <ComReportTree @onSelectReport="onSelectReport" />
        </SplitterPanel>

        <SplitterPanel :size="75" class="pa-4">
            <div v-if="selectedReport" class="p-2">
                <ComReportFilter @onFilter="onFilter" :selectedReport="selectedReport" />
                <iframe @load="onIframeLoaded()" style="height:700px" id="iframe" width="100%" :src="url"></iframe>
            </div>
            <div v-else class="p-2 flex align-items-center h-100 justify-center">
                <p class="text-center text-2xl">Please select report</p>
            </div>
        </SplitterPanel>
    </Splitter>
</template>
<script setup>
import { ref, onMounted, inject } from "@/plugin"
import ComReportTree from "@/views/report/components/ComReportTree.vue"
import ComReportFilter from "@/views/report/components/ComReportFilter.vue"
import Splitter from 'primevue/splitter';
import SplitterPanel from 'primevue/splitterpanel';

const setting = JSON.parse(localStorage.getItem("edoor_setting"))
const serverUrl = window.location.protocol + "//" + window.location.hostname + ":" + setting.backend_port;
const url = ref("")
const gv = inject("$gv")



const selectedReport = ref()
const filters = ref({})

function onSelectReport(p) {
   
    selectedReport.value = p
    loadIframe()
}
function onFilter(f) {
    
    if (selectedReport.value) {
        filters.value = f

        loadIframe()
    }

}


function onIframeLoaded() {
    const iframe = document.getElementById("iframe");
    var contentWidth = iframe.contentWindow.document.body.scrollWidth;
    var windowWidth = window.innerWidth;


    if (iframe.contentWindow.document.body.scrollWidth < iframe.offsetWidth) {
        iframe.style.overflowX = 'hidden';
    } else {
        iframe.style.overflowX = 'auto';
    }
 
}



function loadIframe() {

    if (selectedReport.value) {
        url.value = serverUrl + "/printview?doctype=Business%20Branch&name=" + setting.property.name + "&format=" + gv.getCustomPrintFormat(selectedReport.value.report_name) + "&&settings=%7B%7D&show_toolbar=1"


        if (Object.keys(filters.value)) {
            Object.keys(filters.value).forEach(p => {
                if (filters.value[p]) {
                    url.value = url.value + "&" + p + "=" + filters.value[p]
                }
            });
        }

        url.value = url.value + "&refresh=" + (Math.random() * 16)
        
        document.getElementById("iframe").contentWindow.location.replace(url.value)
    }

}
function onPrint(){
    if (selectedReport.value) {
        url.value = serverUrl + "/printview?doctype=Business%20Branch&name=" + setting.property.name + "&format=" + gv.getCustomPrintFormat(selectedReport.value.report_name) + "&&settings=%7B%7D&show_toolbar=1"


        if (Object.keys(filters.value)) {
            Object.keys(filters.value).forEach(p => {
                if (filters.value[p]) {
                    url.value = url.value + "&" + p + "=" + filters.value[p]
                }
            });
        }

        url.value = url.value + "&trigger_print=1&refresh=" + (Math.random() * 16)
        
        document.getElementById("iframe").contentWindow.location.replace(url.value)
    }
}



onMounted(() => {

    loadIframe()

});




</script> 
<style scoped>
.full-height {
    height: 90vh;
}
</style>