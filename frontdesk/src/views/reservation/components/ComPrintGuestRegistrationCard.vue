<template>
    <Dropdown v-model="selected_guest" :options="guests" optionLabel="guest_name" optionValue="name"
        placeholder="Select Guest" class="w-full md:w-14rem" @change="refreshReport" />
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
const guests = ref([]);
const selected_guest = ref({})


const refreshReport = () => {
    url.value = serverUrl + "/printview?doctype=Customer&name=" + selected_guest.value + "&format=eDoor%20Guest%20Registration%20Card&no_letterhead=0&letterhead=No%20Letterhead&settings=%7B%7D&_lang=en"
    document.getElementById("report-view").contentWindow.location.replace(url.value)
}

onMounted(() => {
    if (!dialogRef) {
        alert("no dialog")
    } else {
        const params = dialogRef.value.data


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