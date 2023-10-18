<template>
    <div class="wrap-dialog iframe-modal" :class="{'full-height' : dialogRef.data.fullheight}">
        <div class="p-3 view-table-iframe-dialog" style="height: 85vh;">
            <div class="grid mb-3 ">
                <div class="col flex gap-2 ">
                    <div>
                        <Dropdown v-model="selected_folio" :options="folios" optionLabel="folio" optionValue="name"
                placeholder="Select Folio" class="w-full md:w-14rem" @change="refreshReport" />
                    </div>
                    <div>
                        <ComSelect v-model="letterHead" doctype="Letter Head" @change="refreshReport" />
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
import { ref, onMounted, inject , onUnmounted } from "@/plugin"
const dialogRef = inject("dialogRef");
const frappe = inject("$frappe")
const call = frappe.call()
const letterHead = ref("")

const setting = JSON.parse(localStorage.getItem("edoor_setting"))
const serverUrl = window.location.protocol + "//" + window.location.hostname + ":" + setting.backend_port;
const url = ref("")
const folios = ref([]);
const selected_folio = ref("all")
const reservation_stay = ref("")
const report_name = ref("")

letterHead.value = setting.property.default_letter_head

const refreshReport = () => {
    url.value = serverUrl + "/printview?doctype=Reservation Stay&name=" + reservation_stay.value + "&format=" + report_name.value + "&&settings=%7B%7D&_lang=en&letterhead=" + letterHead.value + "&show_toolbar=1"

    if (selected_folio.value) {
        url.value = url.value + "&folio=" + selected_folio.value
    }

    document.getElementById("report-view").contentWindow.location.replace(url.value)

}
function onIframeLoaded() {
    const iframe = document.getElementById("report-view");
    iframe.style.height = iframe.contentWindow.document.body.scrollHeight + 'px';
    // iframe.height = iframe.contentWindow.document.body.scrollHeight;
}
function onPrint(){
    url.value = serverUrl + "/printview?doctype=Reservation Stay&name=" + reservation_stay.value + "&format=" + report_name.value + "&&settings=%7B%7D&_lang=en&letterhead=" + letterHead.value + "&show_toolbar=1"

    if (selected_folio.value) {
        url.value = url.value + "&trigger_print=1&folio=" + selected_folio.value
    }

    document.getElementById("report-view").contentWindow.location.replace(url.value)
}

onMounted(() => {
    if (dialogRef) {
        const params = dialogRef.value.data
        reservation_stay.value = params.reservation_stay
        report_name.value = params.report_name

        call.get('edoor.api.reservation.get_reservation_folio', {
            reservation: params.reservation,
            reservation_stay: params.reservation_stay
        })
            .then((result) => {
                folios.value = result.message
                if (!params.folio_number) {

                    selected_folio.value = folios.value[0].name
                } else {

                    selected_folio.value = params.folio_number

                }
                refreshReport()
            })

    }



});

</script> 