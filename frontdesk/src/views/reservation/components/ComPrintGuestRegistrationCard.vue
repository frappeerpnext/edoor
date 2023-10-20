

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
                        <ComLetterHead v-model="letter_head"  @onSelect="onSelectLetterHead"/>
                        <!-- <ComSelect  class="ml-2" place-holder="Letter Head" v-model="letter_head" doctype="Letter Head" @change="refreshReport" /> -->
                    </div>
                </div>
                <div class="col flex gap-2 justify-end">
                    <div v-if="(view||'')!='ui'">
                        
                        <ComPrintButton :url="url"  @click="onPrint"/>
                        
                    </div>
                    <div >
                        <Button @click="refreshReport" icon="pi pi-refresh" class="d-bg-set btn-inner-set-icon p-button-icon-only content_btn_b"></Button>
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
import { callWithAsyncErrorHandling } from "vue";

const dialogRef = inject("dialogRef");
const frappe = inject("$frappe")
const call = frappe.call()
const gv = inject("$gv")




const serverUrl = window.location.protocol + "//" + window.location.hostname + ":" + setting.backend_port;
const url = ref("")
const guests = ref([]);
const selected_guest = ref({})

const letter_head = ref("")
const reservationStay = ref("")



function onSelectLetterHead(l){
    letter_head.value = l
    refreshReport()
}

function onIframeLoaded() {
    const iframe = document.getElementById("report-view");
    iframe.style.height = iframe.contentWindow.document.body.scrollHeight + 'px';
    // iframe.height = iframe.contentWindow.document.body.scrollHeight;
    
}

const refreshReport = () => {
    if (selected_guest.value) {
        url.value = serverUrl + "/printview?doctype=Reservation%20Stay&name=" + reservationStay.value + "&format="+ gv.getCustomPrintFormat("eDoor Guest Registration Card")+"&no_letterhead=0&show_toolbar=0&letterhead="+ letter_head.value +"&settings=%7B%7D&_lang=en&show_toolbar=1&customer=" + selected_guest.value
    }
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