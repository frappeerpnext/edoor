

<template>

 

<div class="wrap-dialog iframe-modal" :class="{'full-height' : dialogRef.data.fullheight}">
        <div class="p-3 view-table-iframe-dialog" style="height: 85vh;">
            <div class="grid mb-3 ">
                <div class="col flex gap-2 ">
                    <div>
                        <Dropdown v-model="selected_guest" :options="guests" optionLabel="guest_name" optionValue="name"
                placeholder="Select Guest" class="w-full md:w-14rem mb-3" @change="refreshReport" />
                    </div>
                    <div>
                        <ComSelect @change="refreshReport" class="ml-2" place-holder="Letter Head" v-model="letter_head" doctype="Letter Head" />
                    </div>
                </div>
                <div class="col flex gap-2 justify-end">
                    <div v-if="(view||'')!='ui'">
                        <SplitButton class="spl__btn_cs sp" @click="onPrint" label="Print" icon="pi pi-print" :model="items" />
                        
                    </div>
                    <div >
                        <Button @click="loadIframe" icon="pi pi-refresh" class="d-bg-set btn-inner-set-icon p-button-icon-only content_btn_b"></Button>
                    </div>
                </div>
            </div> 
            <div class="widht-ifame">
                <iframe @load="onIframeLoaded()" id="report-view" width="100%" :src="url"></iframe>
            </div>
        </div>
    </div>

</template>

<script setup>
import { ref, onMounted, inject } from "@/plugin"
const dialogRef = inject("dialogRef");
const frappe = inject("$frappe")
const call = frappe.call()
const gv = inject("$gv")


const setting = JSON.parse(localStorage.getItem("edoor_setting"))
const serverUrl = window.location.protocol + "//" + window.location.hostname + ":" + setting.backend_port;
const url = ref("")
const guests = ref([]);
const selected_guest = ref({})
const letter_head = ref("")
const reservationStay = ref("")

const items = [
    {
        label: 'Export PDF',
        icon: 'pi pi-file-pdf',
        command: () => {
            url.value = serverUrl + "/api/method/frappe.utils.print_format.download_pdf?doctype=Customer&name=" + selected_guest.value + "&format="+ gv.getCustomPrintFormat("eDoor Guest Registration Card")+"&no_letterhead=0&letterhead="+ encodeURI(letter_head.value) +"&trigger_print=1&settings=%7B%7D&_lang=en&show_toolbar=0&reservation_stay=" + reservationStay.value
            window.open(url.value,reservationStay.value,'width=800, height=900'); 
        }
    },
];



letter_head.value = setting.property.default_letter_head
function onIframeLoaded() {
    const iframe = document.getElementById("report-view");
    iframe.style.height = iframe.contentWindow.document.body.scrollHeight + 'px';
    // iframe.height = iframe.contentWindow.document.body.scrollHeight;
    
}

const refreshReport = () => {
    url.value = serverUrl + "/printview?doctype=Customer&name=" + selected_guest.value + "&format="+ gv.getCustomPrintFormat("eDoor Guest Registration Card")+"&no_letterhead=0&show_toolbar=0&letterhead="+ encodeURI(letter_head.value) +"&settings=%7B%7D&_lang=en&show_toolbar=1&reservation_stay=" + reservationStay.value
    document.getElementById("report-view").contentWindow.location.replace(url.value)
}

function onPrint(){
    

    document.getElementById("report-view").contentWindow.print()

}

onMounted(() => {
    if (!dialogRef) {
        alert("no dialog")
    } else {
        const params = dialogRef.value.data
        reservationStay.value = params.reservation_stay

        call.get('edoor.api.reservation.get_reservation_guest', {
            reservation: params.reservation,
            reservation_stay: params.reservation_stay
        })
            .then((result) => {

                guests.value = result.message
                if (!params.name) {

                        selected_guest.value = guests.value[0].name

                } else {
                    selected_guest.name = params.name
                }
                refreshReport()
            })

    }



});
</script> 