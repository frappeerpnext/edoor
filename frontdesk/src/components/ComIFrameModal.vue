<template>
    <div class="wrap-dialog iframe-modal" :class="{ 'full-height': dialogRef.data.fullheight }">
        <div class="p-3 view-table-iframe-dialog" style="height: 85vh;">
            <div class="grid mb-3 ">
                <div class="col flex gap-2 ">
                    <div v-if="show_letter_head">
                        <ComLetterHead v-model="letter_head" @onSelect="onSelectLetterHead" />
                    </div>
                    <div>
                        <InputText v-if="hasFilter('keyword')" type="text" class="p-inputtext-sm w-full w-12rem"
                            @input="reloadIframe" placeholder="Keyword" v-model="filters.keyword" :maxlength="50" />
                    </div>
                    <div>
                        <Calendar v-if="hasFilter('start_date')" :selectOtherMonths="true"
                            class="p-inputtext-sm w-full w-12rem" v-model="filters.start_date" placeholder="Start Date"
                            @date-select="reloadIframe" showButtonBar dateFormat="dd-mm-yy" showIcon
                            @clear-click="reloadIframe" />
                    </div>
                    <div>
                        <Calendar v-if="hasFilter('end_date')" :selectOtherMonths="true"
                            class="p-inputtext-sm w-full w-12rem" v-model="filters.end_date" placeholder="End Date"
                            @date-select="reloadIframe" showButtonBar @clear-click="reloadIframe" dateFormat="dd-mm-yy"
                            showIcon />
                    </div>
                    <div v-if="hasFilter('business_source')" class="w-12rem">
                        <ComAutoComplete v-model="filters.business_source" placeholder="Business Source"
                            @onSelected="reloadIframe" doctype="Business Source" class="auto__Com_Cus w-full" />
                    </div>
                    <div v-if="hasFilter('building')">
                        <ComSelect v-model="filters.building" @onSelected="reloadIframe" placeholder="Building"
                            doctype="Building" :filters="[['property', '=', property_name]]">
                        </ComSelect>
                    </div>
                    <div v-if="hasFilter('floor')">
                        <ComSelect v-model="filters.floor" @onSelected="reloadIframe" placeholder="Floor" doctype="Floor">
                        </ComSelect>
                    </div>
                    <div v-if="hasFilter('room_type_group')">
                        <ComSelect v-model="filters.room_type_group" @onSelected="reloadIframe"
                            placeholder="Room Type Group" doctype="Room Type Group"></ComSelect>
                    </div>
                    <div v-if="hasFilter('room_type')">
                        <ComSelect v-model="filters.room_type" extraFields="room_type" optionLabel="room_type"
                            optionValue="room_type" @onSelected="reloadIframe" placeholder="Room Type" doctype="Room Type"
                            :filters="[['property', '=', property_name]]"></ComSelect>
                    </div>
                    <div v-if="hasFilter('reservation_status')">
                        <ComSelect v-model="filters.reservation_status" placeholder="Reservation Status"
                            @onSelected="reloadIframe" doctype="Reservation Status" />
                    </div>
                    <div v-if="hasFilter('housekeeping_status')">
                        <ComSelect v-model="filters.housekeeping_status" placeholder="Housekeeping Status"
                            @onSelected="reloadIframe" doctype="Housekeeping Status" />
                    </div>
                    <div v-if="hasFilter('transportation_mode')">
                        <ComSelect v-model="filters.transportation_mode" placeholder="Transportation Mode"
                            @onSelected="reloadIframe" doctype="Transportation Mode" />
                    </div>
                    <div v-if="hasFilter('transportation_company')">
                        <ComSelect v-model="filters.transportation_mode" placeholder="Pickup Location"
                            @onSelected="reloadIframe" doctype="Transportation Company" />
                    </div>
                </div>
                <div class="col flex gap-2 justify-end">
                    <div v-if="(view || '') != 'ui'">
                        <ComPrintButton :url="url" @click="onPrint" />
                    </div>
                    <div>
                        <Button @click="loadIframe" icon="pi pi-refresh"
                            class="btn-size2 d-bg-set btn-inner-set-icon p-button-icon-only content_btn_b"></Button>
                    </div>
                </div>
            </div>
            <div class="widht-ifame">
                <iframe @load="onIframeLoaded()" style="min-height:100vh;" :id="iframe_id" width="100%" :src="url"></iframe>
            </div>
        </div>
    </div>
</template>
<script setup>
import { ref, onMounted, inject, onUnmounted } from "@/plugin"
const dialogRef = inject("dialogRef");
const serverUrl = window.location.protocol + "//" + window.location.hostname + ":" + window.setting.backend_port;
const url = ref("")
const show_letter_head = ref(false)
const letter_head = ref("");
const iframe_id = "iframe_" + Math.random().toString().replace(".", "_")
const moment = inject("$moment")
const filters = ref({})
const show_toolbar = ref(0)
const view = ref("")
const extra_params = ref([])
const filter_options = ref([]) // list array string like ["keyword","business_source","room_type"]
const gv = inject("$gv")
const property_name = ref(window.property_name)


function onSelectLetterHead(l) {
    letter_head.value = l
    loadIframe()
}
const hasFilter = ref((f) => {
    if (filter_options.value) {
        return filter_options.value.includes(f)
    }
    return false

});
function onIframeLoaded() {
    const iframe = document.getElementById(iframe_id);
    var contentWidth = iframe.contentWindow.document.body.scrollWidth;
    var windowWidth = window.innerWidth;
    if (iframe.contentWindow.document.body.scrollWidth < iframe.offsetWidth) {
        iframe.style.overflowX = 'hidden';
    } else {
        iframe.style.overflowX = 'auto';
    }
    iframe.style.minWidth = "0px"
    iframe.style.minWidth = iframe.contentWindow.document.body.scrollWidth + 'px';

    iframe.style.height = '0px';
    iframe.style.height = iframe.contentWindow.document.body.scrollHeight + 'px';
}
function loadIframe() {
    if (view.value) {
        url.value = serverUrl + "/printview?doctype=" + dialogRef.value.data.doctype + "&name=" + dialogRef.value.data.name + "&format=" + gv.getCustomPrintFormat(decodeURI(dialogRef.value.data.report_name)) + "&&settings=%7B%7D&_lang=en&letterhead=No Letterhead&show_toolbar=0&view=ui"

    } else {
        url.value = serverUrl + "/printview?doctype=" + dialogRef.value.data.doctype + "&name=" + dialogRef.value.data.name + "&format=" + gv.getCustomPrintFormat(decodeURI(dialogRef.value.data.report_name)) + "&&settings=%7B%7D&_lang=en&letterhead=" + letter_head.value + "&show_toolbar=0"
    }
    if (extra_params.value) {
        extra_params.value.forEach(p => {
            url.value = url.value + "&" + p.key + "=" + p.value
        });
    }
    let start_date = moment().add(-50, "years").format("YYYY-MM-DD")
    let end_date = moment().add(50, "years").format("YYYY-MM-DD")
    if (Object.keys(filters.value)) {
        Object.keys(filters.value).forEach(p => {

            if (filters.value[p]) {
                if (p == "start_date") {
                    start_date = moment(filters.value[p]).format("YYYY-MM-DD")
                } else if (p == "end_date") {
                    end_date = moment(filters.value[p]).format("YYYY-MM-DD")
                } else {
                    url.value = url.value + "&" + p + "=" + filters.value[p]
                }
            }
        });
    }
    url.value = url.value + "&start_date=" + start_date + "&end_date=" + end_date
    url.value = url.value + "&refresh=" + (Math.random() * 16)
    if (extra_params.value?.filter(r => r.key == 'date').length == 0) {

        url.value = url.value + "&date=" + window.current_working_date
    }
    document.getElementById(iframe_id).contentWindow.location.replace(url.value)
}
function onPrint() {
    document.getElementById(iframe_id).contentWindow.print()
}
const reloadIframe = debouncer(() => {
    loadIframe()
}, 500);

function debouncer(fn, delay) {
    var timeoutID = null;
    return function () {
        clearTimeout(timeoutID);
        var args = arguments;
        var that = this;
        timeoutID = setTimeout(function () {
            fn.apply(that, args);
        }, delay);
    };
}
onMounted(() => {
    window.socket.on("ComIframeModal", (arg) => {

        if (arg == window.property_name) {
            loadIframe()
        }
    })
    show_toolbar.value = dialogRef.value.data.show_toolbar || 1
    show_letter_head.value = dialogRef.value.data.show_letter_head || false
    view.value = dialogRef.value.data.view
    extra_params.value = dialogRef.value.data.extra_params
    filter_options.value = dialogRef.value.data.filter_options
    loadIframe()
});

onUnmounted(() => {
    window.socket.off("ComIframeModal")
})

</script> 
<style scoped>
.full-height {
    height: 90vh;
}
</style>