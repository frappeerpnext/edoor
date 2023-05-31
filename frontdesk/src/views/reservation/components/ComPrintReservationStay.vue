<template>
 
    <Dropdown v-model="selected_folio" :options="folios" optionLabel="folio" optionValue="name"
        placeholder="Select Folio" class="w-full md:w-14rem" @change="refreshReport" />
    <iframe id="report-view" style="height: 1024px;" width="100%" :src="url"></iframe>
</template>

<script setup>
import { ref, onMounted, inject } from "@/plugin"
const dialogRef = inject("dialogRef");
const frappe = inject("$frappe")
const call = frappe.call()


const setting = JSON.parse(localStorage.getItem("edoor_setting"))
const serverUrl = window.location.protocol + "//" + window.location.hostname + ":" + setting.backend_port;
const url = ref("")
const folios = ref([]);
const selected_folio = ref("all")
const reservation_stay = ref("")
const report_name = ref("")


const refreshReport = () => {
    url.value = serverUrl + "/printview?doctype=Reservation Stay&name=" + reservation_stay.value + "&format=" +  report_name.value + "&no_letterhead=0&letterhead=No%20Letterhead&settings=%7B%7D&_lang=en"
    if (selected_folio.value){
        url.value = url.value + "&folio=" + selected_folio.value
    }

    document.getElementById("report-view").contentWindow.location.replace(url.value)
}

onMounted(() => {
    if (!dialogRef) {
        alert("no dialog")
    } else {
        const params = dialogRef.value.data
        reservation_stay.value = params.name
        report_name.value = params.report_name


        call.get('edoor.api.reservation.get_reservation_folio', {
            reservation: params.reservation,
            reservation_stay: params.reservation_stay
        })
            .then((result) => {
                
                folios.value = result.message
                if (!params.name) {

                        selected_folio.value = folios.value[0].name

                } else {
                    selected_folio.name = params.name
                }
                refreshReport()
            })

    }



});
</script> 