<template>   
    <div class="grid">
        <div class="col p-0">
            <div class="flex">
        <ComTagReservation title="BK#:" :value="doc.reservation?.name" class="bg-black"></ComTagReservation>
        <ComTagReservation title="RES#:" :value="doc.reservation_stay?.name"></ComTagReservation>
        <ComTagReservation title="Rooms#:">
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
        <span class="px-2 rounded-lg me-2 text-white" :style="{ background: doc.reservation_stay?.status_color }">{{
            doc.reservation_stay?.reservation_status }}</span>
        <span class="px-2 rounded-lg me-2 text-white" :style="{ background: doc.reservation_stay?.status_color }">{{
            doc.reservation_stay?.reservation_type }}</span>
            </div>
        </div>
        <div class="text-right col p-0">
            <div class="font-light" >Create by:{{ doc.reservation_stay?.owner }}</div>
            <div class="font-light">Last Modify:{{ doc.reservation_stay?.modified }}</div>
            <div class="font-light">Checkin by / date:{{ doc.reservation_stay?.modified }}</div>
            <div class="font-light">Checkout by / date:{{ doc.reservation_stay?.modified }}</div>
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
                            <ComReservationBusinessSourceAndRate :data="doc.reservation_stay" ></ComReservationBusinessSourceAndRate>
                        </div>
                        <div class="col-12">
                    <ComReservationRoomStayList :reservation_stay="doc.reservation_stay" ></ComReservationRoomStayList>
                        </div>
                    </div>
                </div>
                <div class="col">
                    <ComReservationStayDetailChargeSummary :data="doc.reservation_stay">
                    </ComReservationStayDetailChargeSummary>
                </div>
            </div>
            <ComFieldset nameLegend='Summary'>
                ADR:{{ doc.reservation_stay?.adr_rate }} <br />
                Room Nights:{{ doc.reservation_stay?.room_nights }}<br />
                Total Room Rate:{{ doc.reservation_stay?.total_room_rate }}<br />
                Room Charge:{{ doc.reservation_stay?.room_charge }}<br />
                Room Discount:{{ doc.reservation_stay?.room_discount }}<br />
                Room Tax:{{ doc.reservation_stay?.total_room_tax }}<br />
                Extra Charge:{{ doc.reservation_stay?.extra_charge }}<br />
                Extra Charge Discount :{{ doc.reservation_stay?.extra_charge_discount }}<br />
                Extra Charge Tax:{{ doc.reservation_stay?.extra_charge_tax }}<br />
                Total Extra Charge:{{ doc.reservation_stay?.total_extra_charge }}<br />
                Total Payment:{{ doc.reservation_stay?.total_payment }}<br />
                Balance:{{ doc.reservation_stay?.balance }}<br />
            </ComFieldset>
            <ComFieldset nameLegend='Room list'>
                {{ doc.reservation_stay?.stays }}
                <DataTable :value="doc.reservation_stay?.stays" tableStyle="min-width: 50rem">
                    <Column field="room_number" header="Room Number"></Column>
                    <Column field="start_date" header="Stay">
                        <template #body="slotProps">
                            {{ slotProps.data.start_date }} - {{ slotProps.data.end_date }}
                        </template>
                    </Column>
                </DataTable>
            </ComFieldset>
            <ComFieldset nameLegend='Pickup'>
                <!-- {{ doc.reservation_stay }} -->
                Arrival Date : {{ doc.reservation_stay?.arrival_date }}<br />
                Arrival Time :{{ doc.reservation_stay?.arrival_time }}<br />
                Departure Date :{{ doc.reservation_stay?.departure_date }}<br />
                Departure Time :{{ doc.reservation_stay?.departure_time }}<br />
                Room Types :{{ doc.reservation_stay?.room_types }}<br />
                Rooms :{{ doc.reservation_stay?.rooms }}<br />
                Guest :{{ doc.reservation_stay?.guest }}<br />
                Start Date :{{ doc.reservation_stay?.start_date }}<br />
                End Date :{{ doc.reservation_stay?.end_date }}<br />
                Guest :{{ doc.reservation_stay?.guest }}<br />
                Room Chart:{{ doc.reservation_stay?.show_in_room_chart }}<br />
                {{ doc.reservation_stay?.arrival_mode ?? " No arriva mode" }}
            </ComFieldset>
            <ComFieldset nameLegend=''>
                {{ doc }}
                {{ doc.reservation_stay?.stays }}
            </ComFieldset>
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
    <ComReservationStayPrintButton  :reservation_stay="name"/>
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