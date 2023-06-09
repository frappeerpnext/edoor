<template>
    <ComDialogContent hideButtonOK :hideButtonClose="isPage" @onClose="onClose" :isDialog="!isPage">

        <div :class="[isPage, 'bg-white']">
            <div class="flex mb-3 justify-between">
                
                <div class="flex items-center">
                    <div>
                        <span @click="OnViewReservation">
                            <ComTagReservation title="BK#:" :value="rs.reservation?.name" class="link_line_action w-auto">
                                <span class="number_action_line inline-block">{{
                                    rs.stay.total_reservation_stay
                                }}</span>
                            </ComTagReservation>
                        </span>
                        <ComTagReservation title="RES#:" :value="rs.reservationStay?.name" class="bg-card-info p-1px">
                        </ComTagReservation>
                        <ComTagReservation title="Rooms#:" class="bg-card-info p-1px"
                            v-if="rs.reservationStay && rs.reservationStay.rooms">
                            <span v-if="rs.reservationStay?.rooms.split(',').length > 3">
                                <span v-for="value_room_stay_status in rs.reservationStay?.rooms.split(',').slice(0, 3)"
                                    :key="value_room_stay_status">
                                    {{ value_room_stay_status }}
                                </span>
                                <span>
                                    {{ rs.reservationStay?.rooms.split(",").length }}more
                                </span>
                            </span>
                            <span v-else>
                                {{ rs.reservationStay?.rooms }}
                            </span>
                        </ComTagReservation> 
                        <ComReservationStatus v-if="rs.reservationStay && rs.reservationStay?.reservation_status" :status-name="rs.reservationStay?.reservation_status"/>
                        <span class="px-2 rounded-lg me-2 text-white p-1px"
                            :style="{ background: rs.reservationStay?.status_color }">{{
                                rs.reservationStay?.reservation_type }}</span>
                    </div>
                </div>
                <div class="flex">
                    <Button  class="rounded-lg">
                        <ComIcon icon="iconOpenBrower" style="height:18px;" ></ComIcon>
                    </Button>
                    <div class="ms-2" v-if=" rs.stay.total_reservation_stay > 1">
                    <Button  icon="pi pi-angle-double-left" class="border-noround-right border-y-none border-left-none"></Button>
                    <Button  class="border-noround border-rl-ed"> {{ rs.stay.total_reservation_stay }}  </Button>
                    <Button  class="border-noround-left border-y-none border-right-none" icon="pi pi-angle-double-right"></Button>
                    </div>
                </div>
            </div>
            <TabView lazy>
                <TabPanel header="General Information">
                    <div class="grid mt-3 ml-0 ms-0">
                        <div class="col-8 pl-0">
                            <div class="grid">
                                <div class="col-4">
                                    <ComReservationStayDetailGuestInfo />
                                </div>
                                <div class="col-8">
                                    <ComReservationStayInfo />
                                </div>
                                <div class="col-12">
                                    <ComReservationBusinessSourceAndRate />
                                </div>
                                <div class="col-12">
                                    <ComReservationRoomStayList />
                                </div>
                                <div class="col-12">
                                    <ComCommentAndNotice v-if="rs.reservationStay && rs.reservationStay.name" doctype="Reservation Stay" :docname="rs.reservationStay.name"/>
                                </div>
                            </div>
                        </div>
                        <div class="col-4">
                            <div class="grid">
                                <ComReservationStayDetailChargeSummary @onViewReservation="OnViewReservation()" />
                                <ComArrivalAndDeparture />
                            </div>
                        </div>
                    </div>
                </TabPanel>
                <TabPanel header="Room Rate">
                    <ComReservationStayRoomRate />
                </TabPanel>

                <TabPanel header="Folio">

                </TabPanel>

                <TabPanel header="Document">
                    <ComDocument doctype="Reservation Stay" :docname="name"/>
                </TabPanel>

            </TabView>
        </div>
        <template #footer-left>
            <div class="flex flex-col gap-0 justify-around italic min-whidth-modified">
                <div class="xl:col-12 col-10 p-0 font-light text-sm">
                    <div class="col p-0 white-space-nowrap overflow-hidden text-overflow-ellipsis">
                        <span class="font-semibold">Created by: </span>{{ rs.reservationStay?.owner }} {{
                            moment(rs.reservation?.creation).format('DD-MM-yyyy h:mm a') }}
                        <span class="font-semibold">Last Modified: </span> {{ rs.reservationStay?.owner }} {{
                            moment(rs.reservationStay?.modified).format('DD-MM-yyyy h:mm a') }}
                    </div>
                </div>
                <div class="xl:col-12 col-10 p-0 font-light text-sm">
                    <div class="col p-0 white-space-nowrap overflow-hidden text-overflow-ellipsis">
                        <span class="font-semibold">Checked-out by: </span> {{ rs.reservationStay?.owner }} {{
                            moment(rs.reservation?.creation).format('DD-MM-yyyy h:mm a') }}
                        <span class="font-semibold">Checked-in by: </span> {{ rs.reservationStay?.owner }} {{
                            moment(rs.reservation?.creation).format('DD-MM-yyyy h:mm a') }}
                    </div>
                </div>
            </div>
        </template>
        <template #footer-right>
            <Button @click="onCheckIn" class="bg-green-500"><ComIcon icon="checkin" style="height: 18px;" class="me-2"/>Check In</Button>
            <Button @click="OnViewReservation"><ComIcon icon="ViewDetailIcon" style="height: 13px;" class="me-2" /> View Reservation <Badge style="font-weight: 600 !important" :value="rs?.stay?.total_reservation_stay"
                    severity="warning"></Badge></Button>
            <ComReservationStayPrintButton :reservation_stay="name" v-if="name" />
        </template>
    </ComDialogContent>
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
import ComCommentAndNotice from '../../components/form/ComCommentAndNotice.vue';

const rs = inject('$reservation_stay');

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

const isPage = computed(() => {
    return route.name == 'ReservationStayDetail'
})

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
const onClose = () => {
    dialogRef.value.close()
}
const getReservationDetail = () => {

    call.get("edoor.api.reservation.get_reservation_stay_detail", {
        name: name.value
    }).then((result) => {

        rs.stay = result.message
        rs.total_reservation_stay = result.message.total_reservation_stay
        rs.reservation = result.message.reservation
        rs.reservationStay = result.message.reservation_stay
        rs.guest = result.message.guest
        rs.masterGuest = result.message.master_guest
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
                reservation: rs.reservation.name
            }).then((result) => {

                socket.emit("RefresheDoorDashboard", property.name);
                rs = result.message

                toast.add({ severity: 'info', summary: 'Check In', detail: 'Check in successfully', life: 3000 });

            }).catch((error) => {
                const errors = error.exception.split(":")
                toast.add({ severity: 'error', summary: errors[0], detail: error.exception.replace(errors[0] + ":", ""), life: 5000 })
            })

        }
    });
}

const OnViewReservation = () => {
    dialogRef.value.close({ action: "view_reservation_detail", reservation: rs.reservation.name });
}


</script>
<style scoped>
.p-button {
    border: 0 !important;
}
.border-rl-ed{
    border-right: 1px solid var(--btn-border-color) !important;
    border-left: 1px solid var(--btn-border-color) !important;
}

.min-whidth-modified {
    line-height: 1.4;
}</style>