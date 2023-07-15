<template>
    <div class="wrap-dialog" :class="{'full-height' : dialogRef.data.fullheight}">
        <div class="py-3 pl-3 view-table-iframe-dialog" style="height: 80vh;">
            <div class="flex gap-2 mb-3">
                <div v-if="show_letter_head">
                    <ComSelect v-model="letter_head" doctype="Letter Head" @change="loadIframe"/>
                </div>
                <div>
                    <InputText v-if="hasFilter('keyword')" type="text" class="p-inputtext-sm w-full" @input="reloadIframe"
                    placeholder="Keyword" v-model="filters.keyword" :maxlength="50" />
                </div>

                <div v-if="hasFilter('business_source')">
                    <ComAutoComplete v-model="filters.business_source" placeholder="Business Source" @onSelected="reloadIframe"
                        doctype="Business Source" class="auto__Com_Cus" />
                </div>

                <div v-if="hasFilter('building')">
                    <ComSelect v-model="filters.building" @onSelected="reloadIframe" placeholder="Building" doctype="Building"  :filters="[['property','=',setting?.property?.name]]">
                    </ComSelect>
                </div>
                
                <div v-if="hasFilter('floor')">
                    <ComSelect v-model="filters.floor" @onSelected="reloadIframe" placeholder="Floor" doctype="Floor">
                    </ComSelect>
                </div>

                <div v-if="hasFilter('room_type_group')">
                    <ComSelect v-model="filters.room_type_group" 
                        @onSelected="reloadIframe" placeholder="Room Type Group" doctype="Room Type Group"
                        
                        ></ComSelect>
                </div>


                <div v-if="hasFilter('room_type')">
                    <ComSelect v-model="filters.room_type" extraFields="room_type" optionLabel="room_type" optionValue="room_type"
                        @onSelected="reloadIframe" placeholder="Room Type" doctype="Room Type"
                        :filters="[['property','=',setting?.property?.name]]"
                        
                        ></ComSelect>
                </div>

                <div v-if="hasFilter('reservation_status')">
                    <ComSelect v-model="filters.reservation_status" placeholder="Reservation Status" @onSelected="reloadIframe"
                        doctype="Reservation Status"  />
                </div>
                <div v-if="hasFilter('housekeeping_status')">
                    <ComSelect v-model="filters.housekeeping_status" placeholder="Housekeeping Status" @onSelected="reloadIframe"
                        doctype="Housekeeping Status" />
                </div>
                
                <div v-if="hasFilter('transportation_mode')">
                    <ComSelect v-model="filters.transportation_mode" placeholder="Transportation Mode" @onSelected="reloadIframe"
                        doctype="Transportation Mode" />
                </div>
                
                <div v-if="hasFilter('transportation_company')">
                    <ComSelect v-model="filters.transportation_mode" placeholder="Pickup Location" @onSelected="reloadIframe"
                        doctype="Transportation Company" />
                </div>

                <div>
                    <!-- <Button class="border-none h-full" @click="loadIframe">Refresh</Button> -->
                    <Button @click="loadIframe" icon="pi pi-refresh" class="d-bg-set btn-inner-set-icon border-none h-full"></Button>
                </div>
            </div> 
            <iframe @load="onIframeLoaded()" id="iframe" width="100%" :src="url"></iframe>
        </div>
    </div>
</template>
<script setup>
import { ref, onMounted, inject,onUnmounted,useToast } from "@/plugin"

const dialogRef = inject("dialogRef");

const setting = JSON.parse(localStorage.getItem("edoor_setting"))
const serverUrl = window.location.protocol + "//" + window.location.hostname + ":" + setting.backend_port;
const url = ref("")
const show_letter_head = ref(false)
const letter_head = ref("");

const filters = ref({})
const show_toolbar = ref(0)
const view = ref("")
const extra_params = ref([])
const filter_options = ref([]) // list array string like ["keyword","business_source","room_type"]
const toast = useToast()

const socket = inject("$socket");
 

socket.on("RefresheDoorDashboard", (arg) => {
 
    if(arg == setting.property.name){
        
        loadIframe()
    }    
    
})

letter_head.value = setting.property.default_letter_head

const hasFilter = ref((f) => {
    if (filter_options.value) {
        return filter_options.value.includes(f)
    }
    return false

});


function onIframeLoaded() {
    const iframe = document.getElementById("iframe");
    iframe.height = iframe.contentWindow.document.body.scrollHeight;
    
}

function loadIframe() {
 
    if (view.value) {
        url.value = serverUrl + "/printview?doctype=" + dialogRef.value.data.doctype + "&name=" + dialogRef.value.data.name + "&format=" + dialogRef.value.data.report_name +  "&&settings=%7B%7D&_lang=en&letterhead=No Letterhead&show_toolbar=0&view=ui"

    } else {
        url.value = serverUrl + "/printview?doctype=" + dialogRef.value.data.doctype + "&name=" + dialogRef.value.data.name + "&format=" + dialogRef.value.data.report_name +  "&&settings=%7B%7D&_lang=en&letterhead=" + letter_head.value + "&show_toolbar=1"
    }


    if (extra_params.value) {
        extra_params.value.forEach(p => {
            url.value = url.value + "&" + p.key + "=" + p.value
        });
    }

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

    show_toolbar.value = dialogRef.value.data.show_toolbar || 1
    show_letter_head.value = dialogRef.value.data.show_letter_head || false
    view.value = dialogRef.value.data.view
  
    extra_params.value = dialogRef.value.data.extra_params
    filter_options.value = dialogRef.value.data.filter_options
    loadIframe()

});

onUnmounted(() => {
    socket.off("RefresheDoorDashboard");
})


</script> 
<style scoped>
.full-height {
    height: 90vh;
}
</style>