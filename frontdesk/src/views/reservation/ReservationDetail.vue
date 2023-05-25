<template>
    <h1>Reservation Detail</h1>
    <TabView>
        <TabPanel header="General Information">
            {{ doc }}
        </TabPanel>
        <TabPanel header="Room Rate">

        </TabPanel>
        
        <TabPanel header="Folio">

        </TabPanel>
        
        <TabPanel header="Document">

        </TabPanel>
        <TabPanel header="json data">
            {{ doc }}
        </TabPanel>


    </TabView>
 
    <hr>
    <Button @click="onCheckIn">Check In</Button>
</template>
<script setup>
import { inject, ref, onMounted, computed, useToast } from '@/plugin'
import { useConfirm } from "primevue/useconfirm";
const frappe = inject("$frappe")
const call = frappe.call();

const confirm = useConfirm()
const toast = useToast()
const socket = inject("$socket")

const dialogRef = inject("dialogRef");
const setting = localStorage.getItem("edoor_setting")
const property = JSON.parse(localStorage.getItem("edoor_property"))

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

const getReservationDetail = () => {
    alert(name.value)
    call.get("edoor.api.reservation.get_reservation_detail", {
        name: name.value
    }).then((result) => {
        doc.value = result.message
    })
}

//check in
const onCheckIn = () => {
    confirm.require({
        message: 'Are you sure you want to Check In this reservation?',
        header: 'Check In',
        icon: 'pi pi-info-circle',
        acceptClass: 'p-button-success',
        accept: () => {
            call.post("edoor.api.reservation.check_in", {
                reservation: doc.value.reservation.name
            }).then((result) => {

                socket.emit("RefresheDoorDashboard", property.name);
                doc.value = result.message

                toast.add({ severity: 'info', summary: 'Check In', detail: 'Check in successfully', life: 3000 });

            }).catch((error) => {
                const errors = error.exception.split(":")
                toast.add({ severity: 'error', summary: errors[0], detail: error.exception.replace(errors[0] + ":", ""), life: 5000 })
            })

        }
    });
}


</script>