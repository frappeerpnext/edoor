<template>
    <ComDialogContent hideButtonOK :hideButtonClose="isPage" @onClose="onClose" :isDialog="!isPage" :loading="rs.loading">
        <div :class="[isPage, 'bg-white']">
            <div class="grid">
                <div :class="isPage ? 'col py-3' : 'col pt-0'">
                    <div class="flex justify-between">
                        <div class="flex align-items-center">
                            <div class="flex">

                                <ComTagReservation title="RS#:" :value="rs.reservation?.name" class="bg-card-info p-1px">
                                    <span class="res__bagde ml-1">
                                        {{ rs.reservationStays.length }}
                                    </span>
                                </ComTagReservation>
                                <span class="px-2 rounded-lg me-2 text-white p-1px"
                                    :style="{ background: rs.reservation?.status_color }">{{
                                        rs.reservation?.reservation_status }}</span>
                                        <span v-if="rs.reservation?.reservation_type == 'FIT'" class="px-2 rounded-lg me-2 text-white p-1px bg-teal-500">
                                            <i class="pi pi-user" style="font-size: 10px;"></i>
                                            {{rs.reservation?.reservation_type }}</span>
                                        <span v-else class="px-2 rounded-lg me-2 text-white p-1px bg-yellow-500">
                                            <i class="pi pi-users"></i>
                                            {{rs.reservation?.reservation_type }}</span>
                                <!-- <span class="px-2 rounded-lg me-2 text-white p-1px"
                                    :style="{ background: rs.reservation?.status_color }">{{
                                        rs.reservation?.reservation_type }}</span> -->
                            </div>
                        </div>
                        <div class="flex gap-2">
                            <button @click="onRefresh" v-tooltip.left="'Refresh'" :loading="rs?.loading"
                                class="rounded-lg conten-btn flex" link>
                                <icon class="pi pi-refresh font-semibold text-lg m-auto" style="color:var(--bg-purple-cs);">
                                </icon>
                            </button>
                            <button @click="onRoute" v-tooltip.top="'Open New Window'" v-if="!isPage"
                                class="rounded-lg conten-btn " link>
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
                                    <div class="grid">
                                        <div class="col-12">
                                            <ComReservationDetailGuestInfo />
                                        </div>
                                        <div class="col-12">
                                            <ComReservationDetailBusinessSourceAndRate />
                                        </div>
                                    </div>

                                </div>
                                <div class="col-8 pb-0">
                                    <ComReservationInfo />
                                </div>
                            </div>
                        </div>
                        <div class="col-4 pb-0">
                            <div class="grid">
                                <ComReservationDetailChargeSummary />
                            </div>
                        </div>
                    </div>
                    <div class="pt-2">
                        <ComReservationDetailRoomList/>
                    </div>
                    <div class="pt-3">
                        <div class="border-round-xl">
                            <ComReservationNote v-if="rs.reservation && rs.reservation.name" doctype="Reservation" />
                        </div>
                    </div>
                    <hr class="my-3" />
                    <div>
                        <div class="border-round-xl">
                            <ComCommentAndNotice v-if="rs && rs.reservation && rs.reservation.name" doctype="Reservation"
                                :docname="rs.reservation.name" />
                        </div>
                    </div>
                </TabPanel>
                <TabPanel header="Room Rate">
                    <ComReservationRoomRate />
                </TabPanel>

                <TabPanel header="Folio">

                </TabPanel>

                <TabPanel header="Document">
                    <ComDocument doctype="Reservation" :extraFilters="rs.reservationStays" :docname="name" />
                </TabPanel>

            </TabView>
        </div>
        <template #footer-left>
            <Button class="border-none" @click="onAuditTrail">
                <i class="pi pi-history me-2"></i>Audit Trail
            </Button>
        </template>
    </ComDialogContent>
</template>
<script setup>
import { inject, ref, onMounted, computed, useToast, useRoute, onUnmounted, useDialog } from '@/plugin'
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


function onRefresh(showLoading = true) {
    rs.LoadReservation(name.value, showLoading);
    rs.getChargeSummary(name.value)
}


function onRoute() {
    window.open('reservation-detail/' + name.value, '_blank')
}
function onClose() {
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
            closeOnEscape: false,
            position: "top"
        },
        onClose: (options) => {
            //
        }
    });
}

onMounted(() => {
    socket.on("RefreshReservationDetail", (reservation) => {
        if (reservation == name.value) {
            //we run this in settime out 
            //because we need to wait until data from backend that run enqueue process is update ted
            setTimeout(function(){
                onRefresh(false)
            },3000)
            
            

        }
    })


    if (!dialogRef) {
        if (route.params.name) {
            name.value = route.params.name
            onRefresh()
        }
    } else {
        name.value = dialogRef.value.data.name;
        onRefresh()

    }
});

onUnmounted(() => {
    rs.clear()
    socket.off("RefreshReservationDetail");


})
</script>
<style scoped>
.res__bagde {
    border-radius: 0.5rem;
    padding: 0 5px;
    background: #cacaca;
    position: relative;
    right: -3px;
}</style>