<template>
   <div class="mb-2">
    <Dropdown v-model="selected_folio" :options="folios" optionLabel="folio" optionValue="name"
        placeholder="Select Folio" class="w-full md:w-14rem mr-2" @change="refreshReport" 
       
        />
    <ComSelect v-model="letterHead" doctype="Letter Head" @change="refreshReport"/>  
</div>
    <iframe id="report-view" style="height: 70vh;" width="100%" :src="url"></iframe>
</template>

<script setup>
import { ref, onMounted, inject } from "@/plugin"
const dialogRef = inject("dialogRef");
const frappe = inject("$frappe")
const call = frappe.call()
const letterHead= ref("")

const setting = JSON.parse(localStorage.getItem("edoor_setting"))
const serverUrl = window.location.protocol + "//" + window.location.hostname + ":" + setting.backend_port;
const url = ref("")
const folios = ref([]);
const selected_folio = ref("all")
const reservation_stay = ref("")
const report_name = ref("")

letterHead.value = setting.property.default_letter_head

const refreshReport = () => {
    url.value = serverUrl + "/printview?doctype=Reservation Stay&name=" + reservation_stay.value + "&format=" +  report_name.value + "&&settings=%7B%7D&_lang=en&letterhead=" + letterHead.value + "&show_toolbar=1"
     
    if (selected_folio.value){
        url.value = url.value + "&folio=" + selected_folio.value
    }

    document.getElementById("report-view").contentWindow.location.replace(url.value)
}

onMounted(() => {
    if (dialogRef)  {
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
                   
                    selected_folio.value =params.folio_number
                   
                }
                refreshReport()
            })

    }



});
</script> 