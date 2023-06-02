<template>   
    <div class="grid">
        <div class="col mb-2">
            <div class="flex">
            <span @click="OnViewReservation" >
        <ComTagReservation  title="BK#:" :value="doc.reservation?.name" class="link_line_action">
            <span class="link_line_action number_action_line inline-block">{{ doc.total_reservation_stay }}</span>
        </ComTagReservation>
            </span>
        <ComTagReservation title="RES#:" :value="doc.reservation_stay?.name" class="bg-card-info p-1px" ></ComTagReservation>
        <ComTagReservation title="Rooms#:" class="bg-card-info p-1px">
            <span v-if="doc.reservation_stay?.rooms.split(',').length > 3">
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
                </span>
        </ComTagReservation>
        <span class="px-2 rounded-lg me-2 text-white p-1px" :style="{ background: doc.reservation_stay?.status_color }">{{
            doc.reservation_stay?.reservation_status }}</span>
        <span class="px-2 rounded-lg me-2 text-white p-1px" :style="{ background: doc.reservation_stay?.status_color }">{{
            doc.reservation_stay?.reservation_type }}</span>
            </div>
        </div>
    </div>
    <TabView>
        <TabPanel header="General Information">
            <div class="grid mt-3 ml-0 ms-0">
                <div class="col-8">
                    <div class="grid">
                        <div class="col-4">
                            <ComReservationStayDetailGuestInfo v-model="doc" />
                        </div>
                        <div class="col-8">
                            <ComReservationStayInfo :reservation-stay="doc.reservation_stay"/>
                        </div>
                        <div class="col-12">
                            <ComReservationBusinessSourceAndRate :data="doc.reservation" ></ComReservationBusinessSourceAndRate>
                        </div>
                        <div class="col-12">
                            <ComReservationRoomStayList :reservation_stay="doc.reservation_stay" ></ComReservationRoomStayList>
                        </div>
                    </div>
                    <div class="col-12">
            <div class="font-light" >Created by: {{ doc.reservation_stay?.owner }} </div>
            <div class="font-light">Checked-in by: {{ doc.reservation_stay?.modified }}</div>
            <div class="font-light">Checked-out by: {{ doc.reservation_stay?.modified }}</div>
            <div class="font-light">Last Modified: {{ doc.reservation_stay?.modified }}</div>
                    </div>
                </div>
                <div class="col">
                    <div class="grid">
                    <ComReservationStayDetailChargeSummary :data="doc">
                    </ComReservationStayDetailChargeSummary>
                    <ComArrivalAndDeparture></ComArrivalAndDeparture>
                    </div>
                </div>
            </div>
        </TabPanel>
        <TabPanel header="Room Rate">
            {{ name }}
            <ComReservationStayRoomRate :reservation_stay="name" />
        </TabPanel>

        <TabPanel header="Folio">

        </TabPanel>

        <TabPanel header="Document">

        </TabPanel>

        <TabPanel header="Document">
            {{ doc }}
        </TabPanel>

    </TabView>


    <hr>
    <Button @click="onCheckIn">Check In</Button>
    <Button @click="OnViewReservation">View Reservation</Button>
    <ComReservationStayPrintButton  :reservation_stay="name" v-if="name"/>
</template>
<script setup>

import { inject, ref, onMounted, computed, useToast, useRoute, useRouter } from '@/plugin'
import { useConfirm } from "primevue/useconfirm";

import ComReservationStayPrintButton from "@/views/reservation/components/ComReservationStayPrintButton.vue"

import ComReservationStayRoomRate from '@/views/reservation/components/ComReservationStayRoomRate.vue';
import ComCardProfileGuest from '@/views/reservation/components/ComCardProfileGuest.vue';
import ComReservationStayDetailGuestInfo from './components/ComReservationStayDetailGuestInfo.vue';
import ComReservationStayPanel from './components/ComReservationStayPanel.vue';
import ComReservationStayDetailChargeSummary from './components/ComReservationStayDetailChargeSummary.vue';
import ComBoxStayInformation from '@/views/reservation/components/ComBoxStayInformation.vue';
import ComTagReservation from '@/views/reservation/components/ComTagReservation.vue';
import ComReservationBusinessSourceAndRate from '@/views/reservation/components/ComReservationBusinessSourceAndRate.vue';
import ComReservationStayInfo from './components/ComReservationStayInfo.vue';
import ComReservationRoomStayList from './components/ComReservationRoomStayList.vue'
import ComArrivalAndDeparture from './components/ComArrivalAndDeparture.vue';

const route = useRoute()
const router = useRouter()

const frappe = inject("$frappe")
const call = frappe.call();
const moment = inject("$moment")
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
        if (route.params.name) {
            name.value = route.params.name
            getReservationDetail();
        } else {
            alert("Go back to reserveatin list")
        }

    } else {

        name.value = dialogRef.value.data.name;
        getReservationDetail();
    }


});

const getReservationDetail = () => {
    call.get("edoor.api.reservation.get_reservation_stay_detail", {
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

const OnViewReservation = () => {

    dialogRef.value.close({ action: "view_reservation_detail", reservation: doc.value.reservation.name });
}


</script>