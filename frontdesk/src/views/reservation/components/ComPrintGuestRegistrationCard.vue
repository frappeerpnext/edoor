<template>
    <div class=" view-table-iframe-dialog -mr-3 pr-2" style="height: 75vh;">
    <div class="mb-2">
    <Dropdown v-model="selected_guest" :options="guests" optionLabel="guest_name" optionValue="name"
        placeholder="Select Guest" class="w-full md:w-14rem mb-3" @change="refreshReport" />
    
    <ComSelect @change="refreshReport" class="ml-2" place-holder="Letter Head" v-model="letter_head" doctype="Letter Head" />
    </div>
    <iframe @load="onIframeLoaded()" id="report-view" width="100%" :src="url"></iframe>
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

letter_head.value = setting.property.default_letter_head
function onIframeLoaded() {
    const iframe = document.getElementById("report-view");
    iframe.style.height = iframe.contentWindow.document.body.scrollHeight + 'px';
    // iframe.height = iframe.contentWindow.document.body.scrollHeight;
    
}

const refreshReport = () => {
    url.value = serverUrl + "/printview?doctype=Customer&name=" + selected_guest.value + "&format="+gv.getCustomPrintFormat("eDoor Guest Registration Card")+"&no_letterhead=0&letterhead="+ encodeURI(letter_head.value) +"&settings=%7B%7D&_lang=en&show_toolbar=1&reservation_stay=" + reservationStay.value
    document.getElementById("report-view").contentWindow.location.replace(url.value)
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