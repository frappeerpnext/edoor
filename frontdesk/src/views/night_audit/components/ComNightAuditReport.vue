<template >
    <div>
        <div class="primary_message">
            <h2 class="text-4xl">Congratulation!</h2>
            <p>Night audit process executed successfully.</p>
            <p>The system date has been updated to {{ date }}. Kindly provide the printed report to your supervisor.</p>
        </div>
        <Splitter class="mb-5" state-key="report_spliter_state" state-storage="local">
            <SplitterPanel :size="25" class="pa-4">
                <div class="p-2">
                    <Button :class="{ active: activeButton === index }" class="night-audit-report-btn"
                        @click="onViewReport(d, activeButton = index)" v-for="(d, index) in report_list" :key="index">
                        {{ d.report_title }}
                    </Button>
                </div>
            </SplitterPanel>

            <SplitterPanel :size="75" class="pa-4">
                <div v-if="selectedReport" class="p-2">
                    <div class="flex justify-content-between mb-5">
                        <ComLetterHead v-model="letter_head" @onSelect="onSelectLetterHead" />
                        <div class="flex">
                            <div class="pr-2">
                                <ComPrintButton :url="url" @click="onPrint" />
                            </div>
                            <ComHeader isRefresh @onRefresh="showReport()" wrClass="p-0" />
                        </div>
                    </div>

                    <iframe @load="onIframeLoaded()" style="height:700px;" id="iframe_night_audit_report" width="100%"
                        :src="url"></iframe>
                </div>
                <div v-else class="p-2 flex align-items-center h-100 justify-center">
                    <p class="text-center text-2xl">Please select report</p>
                </div>
            </SplitterPanel>
        </Splitter>
    </div>
</template>
<script setup>
import { getDocList, ref, inject, onMounted } from "@/plugin"
import Splitter from 'primevue/splitter';
import SplitterPanel from 'primevue/splitterpanel';
const report_list = ref([])
const selectedReport = ref()
const date = ref()
const gv = inject("$gv")
const moment = inject("$moment")
const url = ref()
const activeButton = ref(0)
const letter_head = ref(window.setting.property.default_letter_head)
const working_day = JSON.parse(localStorage.getItem("edoor_working_day"))
function onViewReport(rpt, activeButton) {
    selectedReport.value = rpt
    showReport()
}


function onPrint() {
    const el = document.getElementById("iframe_night_audit_report")
    if (el) {
        el.contentWindow.print()
    }
}


function showReport() {
    const serverUrl = window.location.protocol + "//" + window.location.hostname + ":" + window.setting.backend_port;
    let date = window.current_working_date
    if (selectedReport.value.default_audit_date == 'Previous Audit Date') {
        date = moment(date).add(-1, 'Days').format("YYYY-MM-DD")
    }

    url.value = serverUrl + "/printview?doctype=Business%20Branch&name=" + window.property_name + "&format=" + gv.getCustomPrintFormat(decodeURI(selectedReport.value.report_name)) + "&&settings=%7B%7D&_lang=en&letterhead=" + letter_head.value + "&show_toolbar=0&start_date=" + date + "&end_date=" + date + "&" + selectedReport.value.default_filter

    const el = document.getElementById("iframe_night_audit_report")

    if (el) {
        el.contentWindow.location.replace(url.value)
    }
}

function onIframeLoaded() {
    //use to set auto heiht 

}

function onSelectLetterHead(d) {
    letter_head.value = d
    showReport()
}

onMounted(() => {
    date.value = moment(working_day.date_working_day).format("MMMM DD, YYYY")
    getDocList("System Report", {
        fields: ["*"],
        filters: [["parent_system_report", "=", 'Night Audit']],
        orderBy: {
            field: 'sort_order'
        },
        limit: 1000,
    }).then((data) => {
        report_list.value = data
        if (data.length > 0) {
            selectedReport.value = data[0]
            showReport()
        }
    })


})


</script> 
<style scoped>
.night-audit-report-btn {
    display: block;
    width: 100%;
    background: transparent;
    color: #000;
    border-radius: 0;
    border: 1px solid #dee2e6;
    margin-bottom: 4px;
    text-align: left;
}

.night-audit-report-btn.active {
    color: #4338CA;
    background: #EEF2FF;
}

.night-audit-report-btn:not(.active):hover {
    color: #495057;
    background: #e9ecef;
}</style>