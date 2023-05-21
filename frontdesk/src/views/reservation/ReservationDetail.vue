<template>
    <h1>Reservation Detail</h1>
    {{ name }}
    {{ doc }}
</template>
<script setup>
import { inject, ref, onMounted, computed } from '@/plugin'
const frappe = inject("$frappe")
const call = frappe.call();

const dialogRef = inject("dialogRef");
const setting = localStorage.getItem("edoor_setting")
const serverUrl = window.location.protocol + "//" + window.location.hostname + ":" + setting.backend_port;

const name = ref("")
const doc = ref({})

onMounted(() => {
    if (!dialogRef) {
        alert("no dialog")
    } else {
        name.value = dialogRef.value.data.name;
        getReservationDetail();

    }
});

const getReservationDetail =()=>{
    call.get("edoor.api.reservation.get_reservation_detail",{
        name:name.value
    }).then((result)=>{
        doc.value = result.message
    })
}

</script>