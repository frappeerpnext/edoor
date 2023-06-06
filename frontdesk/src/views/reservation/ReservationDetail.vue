<template>
    <ComDialogContent hideButtonOK :hideButtonClose="isPage" @onClose="onClose" :isDialog="!isPage">
        <div :class="[isPage, 'bg-white']">
            <div class="grid">
                <div class="col mb-2">
                    <div class="flex">
                        <ComTagReservation title="BK#:" :value="rs.reservation?.name" class="bg-card-info p-1px">
                            <span class="res__bagde ml-1">
                                {{rs.reservationStays.length}}
                            </span>
                        </ComTagReservation>
                        <span class="px-2 rounded-lg me-2 text-white p-1px"
                            :style="{ background: rs.reservation?.status_color }">{{
                                rs.reservation?.reservation_status }}</span>
                        <span class="px-2 rounded-lg me-2 text-white p-1px"
                            :style="{ background: rs.reservation?.status_color }">{{
                                rs.reservation?.reservation_type }}</span>
                    </div>
                </div>
            </div>
            <TabView @update:activeIndex="onTab">
                <TabPanel header="General Information">
                    <div class="grid mt-3 ml-0 ms-0">
                        <div class="col-8">
                            <div class="grid">
                                <div class="col-4">
                                    <ComReservationDetailGuestInfo />
                                </div>
                                <div class="col-8">
                                    <ComReservationInfo />
                                </div>
                                <div class="col-12">
                                    <ComReservationDetailBusinessSourceAndRate />
                                </div>
                            </div>
                        </div>
                        <div class="col-4">
                            <div class="grid h-full">
                                <ComReservationDetailChargeSummary/>
                            </div>
                        </div>
                    </div>
                    <div class="col-12">
                        <ComReservationDetailRoomList />
                    </div>
                </TabPanel>
                <TabPanel header="Room Rate">
                    <ComReservationRoomRate />
                </TabPanel>

                <TabPanel header="Folio">

                </TabPanel>

                <TabPanel header="Document"> 
                    <ComDocument v-if="tabIndex == 3" doctype="Reservation" :docname="name"/>
                </TabPanel>

            </TabView>
        </div>
    </ComDialogContent>
</template>
<script setup>
import { inject, ref, onMounted, computed, useToast } from '@/plugin'
import { useConfirm } from "primevue/useconfirm";
import ComTagReservation from '@/views/reservation/components/ComTagReservation.vue';
import ComReservationDetailGuestInfo from '@/views/reservation/components/ComReservationDetailGuestInfo.vue'
import ComReservationInfo from '@/views/reservation/components/ComReservationInfo.vue'
import ComReservationDetailBusinessSourceAndRate from '@/views/reservation/components/ComReservationDetailBusinessSourceAndRate.vue'
import ComReservationDetailRoomList from '@/views/reservation/components/ComReservationDetailRoomList.vue'
import ComReservationDetailChargeSummary from '@/views/reservation/components/ComReservationDetailChargeSummary.vue'
import ComReservationRoomRate from '@/views/reservation/components/ComReservationRoomRate.vue'




const frappe = inject("$frappe")
const rs = inject("$reservation")
const call = frappe.call();

const confirm = useConfirm()
const toast = useToast()
const socket = inject("$socket")

const dialogRef = inject("dialogRef");
const setting = localStorage.getItem("edoor_setting")
const property = JSON.parse(localStorage.getItem("edoor_property"))

const serverUrl = window.location.protocol + "//" + window.location.hostname + ":" + setting.backend_port;

const name = ref("")
const tabIndex = ref(0)

onMounted(() => {
    if (!dialogRef) {
        alert("no dialog")
    } else {
        name.value = dialogRef.value.data.name;
        rs.LoadReservation(name.value);

    }
});
function onTab($event){
    tabIndex.value = $event
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
<style scoped>
    .res__bagde{
        border-radius: 0.5rem;
        padding: 0 5px;
        background: #cacaca;
        margin-right: -5px;
    }
</style>