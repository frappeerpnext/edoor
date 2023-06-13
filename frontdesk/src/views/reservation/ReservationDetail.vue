<template>
    <ComDialogContent hideButtonOK :hideButtonClose="isPage" @onClose="onClose" :isDialog="!isPage">
        <div :class="[isPage, 'bg-white']">
            <div class="grid">
                <div :class="isPage ? 'col py-3' : 'col pt-0'">
                    <div class="flex justify-between">
                        <div class="flex align-items-center">
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
                        <div>
                            <button @click="onRoute" v-tooltip.top="'Open New Window'" v-if="!isPage" class="h-3rem rounded-lg w-3rem border-purple-50-hover-edoor border-1 cursor-pointer flex justify-center items-center" link>
                                <ComIcon icon="iconOpenBrower" style="height:18px;"></ComIcon>
                            </button>
                        </div>
                    </div>
                </div>
            </div>
            <TabView lazy>
                <TabPanel header="General Information">
                    <div class="grid mt-2 ml-0 ms-0">
                        <div class="col-8 pl-0">
                            <div class="grid">
                                <div class="col-4">
                                    <ComReservationDetailGuestInfo />
                                </div>
                                <div class="col-8">
                                    <ComReservationInfo />
                                </div>
                                <div class="col-12 pb-0">
                                    <ComReservationDetailBusinessSourceAndRate />
                                </div>
                            </div>
                        </div>
                        <div class="col-4">
                            <div class="h-full">
                                <ComReservationDetailChargeSummary/>
                            </div>
                        </div>
                    </div>
                    <div class="pt-2">
                        <ComReservationDetailRoomList v-if="!rs.loading"/>
                    </div>
                    <div class="pt-3">
                        <div class="border-round-xl">
                            <ComReservationNote v-if="rs.reservation && rs.reservation.name" doctype="Reservation"/>
                        </div>
                    </div>
                    <hr class="my-3"/>
                    <div>
                        <div class="border-round-xl">
                            <ComCommentAndNotice v-if="rs && rs.reservation && rs.reservation.name" doctype="Reservation" :docname="rs.reservation.name"/>
                        </div>
                    </div>
                </TabPanel>
                <TabPanel header="Room Rate">
                    <ComReservationRoomRate />
                </TabPanel>

                <TabPanel header="Folio">

                </TabPanel>

                <TabPanel header="Document"> 
                    <ComDocument doctype="Reservation" :extraFilters="rs.reservationStays" :docname="name"/>
                </TabPanel>

            </TabView>
        </div>
        <template #footer-left>
            <Button @click="onAuditTrail">
                <i class="pi pi-history me-2"></i>Audit Trail
            </Button>
        </template>
    </ComDialogContent>
</template>
<script setup>
import { inject, ref, onMounted, computed, useToast, useRoute,onUnmounted ,useDialog} from '@/plugin'
import { useConfirm } from "primevue/useconfirm";
import ComTagReservation from '@/views/reservation/components/ComTagReservation.vue';
import ComReservationDetailGuestInfo from '@/views/reservation/components/ComReservationDetailGuestInfo.vue'
import ComReservationInfo from '@/views/reservation/components/ComReservationInfo.vue'
import ComReservationDetailBusinessSourceAndRate from '@/views/reservation/components/ComReservationDetailBusinessSourceAndRate.vue'
import ComReservationDetailRoomList from '@/views/reservation/components/ComReservationDetailRoomList.vue'
import ComReservationDetailChargeSummary from '@/views/reservation/components/ComReservationDetailChargeSummary.vue'
import ComReservationRoomRate from '@/views/reservation/components/ComReservationRoomRate.vue'
import ComCommentAndNotice from '../../components/form/ComCommentAndNotice.vue';
import ComReservationNote from './components/ComReservationNote.vue';
import ComAuditTrail from '../../components/layout/components/ComAuditTrail.vue';

const route = useRoute()
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
const dialog = useDialog()
const isPage = computed(() => {
    return route.name == 'ReservationDetail'
})


onMounted(() => {
    if (!dialogRef) {
        if (route.params.name) {
            name.value = route.params.name
            rs.LoadReservation(name.value);
        } else {
            alert("Go back to reserveatin list")
        }
    } else {
        name.value = dialogRef.value.data.name;
        rs.LoadReservation(name.value);

    }
});
function onRoute(){
    window.open('reservation-detail/' + name.value, '_blank')
}
function onClose(){ 
    dialogRef.value.close()
}
function onAuditTrail() {
    const dialogRef = dialog.open(ComAuditTrail, {
        data: {
            doctype: 'Reservation',
            docname: name.value
        },
        props: {
            header: 'Audit Trail',
            style: {
                width: '75vw',
            },
            breakpoints: {
                '960px': '100vw',
                '640px': '100vw'
            },
            modal: true,
            maximizable: true,
        },
        onClose: (options) => {
            //
        }
    });
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

onUnmounted(() => {
    rs.clear()
})
</script>
<style scoped>
    .res__bagde{
        border-radius: 0.5rem;
        padding: 0 5px;
        background: #cacaca;
        position: relative;
        right: -3px;
    }
</style>