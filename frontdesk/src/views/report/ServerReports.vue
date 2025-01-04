<template>
    
        <Splitter class="mb-5" state-key="report_spliter_state" state-storage="local">
            <SplitterPanel :size="25" class="pa-4 left-side-panel overflow-y-auto">
                <ComReportTree   @onSelectReport="onSelectReport" />
            </SplitterPanel>

            <SplitterPanel :size="75" class="pa-4">
             
                <div id="main_server_report_viewer"></div>

            </SplitterPanel>
        </Splitter>
 
</template>
<script setup>
import { ref, onMounted, inject,onUnmounted } from "@/plugin"
import ComReportTree from "@/views/report/components/ComReportTree.vue"
 
import Splitter from 'primevue/splitter';
import SplitterPanel from 'primevue/splitterpanel';
import {i18n} from '@/i18n';
const { t: $t } = i18n.global;

 
const setting = window.setting
 
const gv = inject("$gv")

 
const selectedReport = ref()
 

function onSelectReport(p) { 

    selectedReport.value = p
    let report_params = [
        {name: 'printed_by', values: [window.user.full_name] },
        {name: 'property', values: [window.property_name] },
        {name: 'start_date', values: ['2024-12-01'] },
        {name: 'end_date', values: ['2025-12-01'] },
    ] 


    $("#main_server_report_viewer").boldReportViewer({
        reportServerUrl:window.setting.server_report_url,
        reportServiceUrl: window.setting.report_service_url,
        reportPath: selectedReport.value.server_report_path,
        serviceAuthorizationToken: "bearer " + window.setting.embed_code,
        parameters: report_params,
        zoomFactor: 1.25,
        reportLoaded: function(event) {
            setTimeout(() => {
                let property  = document.querySelector("#main_server_report_viewer_Param_101")
             
            }, 5000);
          
        }
    });
 
    
} 

     
 

onMounted(() => {
    
});

onUnmounted(() => {
    
})


</script> 
<style scoped>
 

</style>
