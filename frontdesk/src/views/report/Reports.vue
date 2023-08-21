<template>
    <ComHeader isRefresh @onRefresh="onRefresh()">
        <template #start>
            <div class="flex">
                <div class="flex align-items-center">
                    <div @click="onRefresh()" class="text-2xl">Reports</div>
                </div>
            </div>
        </template>
    </ComHeader>
    <Splitter class="mb-5" state-key="report_spliter_state" state-storage="local">
        <SplitterPanel class="pa-4">
            <ComReportTree @onSelectReport="onSelectReport" />
        </SplitterPanel>

        <SplitterPanel class="pa-4">
            <div v-if="selectedReport" class="p-2">
                <ComReportFilter @onFilter="onFilter" :selectedReport="selectedReport" />
                <hr class="mt-2 mb-3"/>
                <!-- {{ url }}{{ selectedReport.report_name }} -->
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

    // iframe.style.minWidth ="0px"
    // iframe.style.minWidth = iframe.contentWindow.document.body.scrollWidth + 'px';

    // iframe.style.height = '0px';
    // iframe.style.height = iframe.contentWindow.document.body.scrollHeight + 'px';

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



onMounted(() => {

    loadIframe()

});




</script> 
<style scoped>
.full-height {
    height: 90vh;
}
</style>