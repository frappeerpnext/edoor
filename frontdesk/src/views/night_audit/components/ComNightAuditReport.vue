<template >
    <div> 
        <div class="primary_message">
            <h2 class="text-4xl">Congratulation!</h2>
            <p>Night audit process executed successfully.</p>
            <p>The system date has been updated to July 20, 2023. Kindly provide the printed report to your supervisor.</p>
        </div>
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
    </div>   
</template>
<script setup> 
import ComReportTree from "@/views/report/components/ComReportTree.vue"
import ComReportFilter from "@/views/report/components/ComReportFilter.vue"
import Splitter from 'primevue/splitter';
import SplitterPanel from 'primevue/splitterpanel';
</script> 