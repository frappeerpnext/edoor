<template>
    <div class="flex ">
        <ComTagReservation title="BK#:" :value="doc.reservation?.name"></ComTagReservation>
        <ComTagReservation title="RES#:" :value="doc.reservation?.guest"></ComTagReservation>
        <ComTagReservation title="Rooms#:">
            <!-- <span v-if="doc.reservation?.rooms.split(',').length > 3">
                <span v-for="value_room_stay_status in doc.reservation_stay?.rooms.split(',').slice(0, 3)"
                    :key="value_room_stay_status">
                    {{ value_room_stay_status }}
                </span>
                <span>
                    {{ doc.reservation_stay?.rooms.split(",").length }}more
                </span>
            </span>
            <span v-else>
                {{ doc.reservation_stay?.rooms }}
            </span> -->
        </ComTagReservation>
        <span class="px-2 rounded-lg me-2 text-white" :style="{ background: doc.reservation?.status_color }">{{
            doc.reservation?.reservation_status }}</span>
        <span class="px-2 rounded-lg me-2 text-white" :style="{ background: doc.reservation?.status_color }">{{
            doc.reservation?.reservation_type }}</span>
    </div>
    <TabView>
        <TabPanel header="General Information">
            {{ doc }}
        </TabPanel>
        <TabPanel header="Room Rate" lazy>

        </TabPanel>

        <TabPanel header="Folio">

        </TabPanel>

        <TabPanel header="Document">

        </TabPanel>
        <TabPanel header="json data">
            {{ doc.reservation }}
        </TabPanel>


    </TabView>

    <hr>
    <Button @click="onCheckIn">Check In</Button>
</template>
<script setup>
import { inject, ref, onMounted, computed, useToast } from '@/plugin'
import { useConfirm } from "primevue/useconfirm";
import ComTagReservation from '@/views/reservation/components/ComTagReservation.vue';



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