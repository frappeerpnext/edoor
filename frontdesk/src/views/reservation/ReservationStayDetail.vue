<template>
    <ComDialogContent :loading="rs.loading" hideButtonOK :hideButtonClose="isPage" @onClose="onClose" :isDialog="!isPage">
        <div :class="(rs.loading ? 'opacity-10 bg-black' : '' )">
        <div :class="[isPage, 'bg-white']">
            <div class="flex mb-3 justify-between">
                <div class="flex items-center">
                    <div>
                        <span @click="OnViewReservation">
                            <ComTagReservation title="BK#:" :value="rs?.reservation?.name" class="link_line_action w-auto">
                                <span class="number_action_line inline-block">
                                    {{ rs?.reservationStayNames.length }} </span>
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
                        <ComReservationStatus v-if="rs.reservationStay && rs.reservationStay?.reservation_status"
                            :status-name="rs.reservationStay?.reservation_status" />
                        <span class="px-2 rounded-lg me-2 text-white p-1px"
                            :style="{ background: rs.reservationStay?.status_color }">{{
                                rs.reservationStay?.reservation_type }}</span>
                    </div>
                </div>

                <div class="flex gap-2">
                        
                    <Button>Is Master Room {{ rs.reservationStay.is_master }}</Button>
                    <button @click="onRefresh" v-tooltip.top="'Refresh'" :loading="rs?.loading" class="rounded-lg w-3rem border-purple-50-hover-edoor border-1 cursor-pointer flex justify-center items-center" link><icon class="pi pi-refresh font-semibold text-lg" style="color:var(--bg-purple-cs);"></icon></button>
                    <button @click="onRoute" v-tooltip.top="'Open New Window'" v-if="!isPage" class="rounded-lg w-3rem border-purple-50-hover-edoor border-1 cursor-pointer flex justify-center items-center" link>
                        <ComIcon icon="iconOpenBrower" style="height:18px;"></ComIcon>
                    </button>
                    <div class="ms-2" v-if="rs?.reservationStayNames.length > 1">
                    <Button  v-if="rs?.reservationStayNames.length > 1" @click="onNavigateStay(-1)"
                            :disabled="rs?.canNavigatePrevious(name) || rs.loading" icon="pi pi-angle-double-left"
                            class="border-noround-right border-y-none border-left-none">
                    </Button>
                    <Button class="border-noround border-rl-ed">{{(rs?.reservationStayNames.indexOf(rs.reservationStay?.name)) + 1}} / {{ rs?.reservationStayNames.length }} </Button>
                    <Button v-if="rs?.reservationStayNames.length > 1" @click="onNavigateStay(1)"
            :disabled="rs?.canNavigateNext(name) || rs.loading" class="border-noround-left border-y-none border-right-none"
                            icon="pi pi-angle-double-right"></Button>
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
                                    <ComReservationNote v-if="rs.reservationStay && rs.reservationStay.name"
                                        doctype="Reservation Stay" />
                                </div>
                                <div class="col-12">
                                    <hr>
                                </div>
                                <div class="col-12">
                                    <ComCommentAndNotice v-if="rs.reservationStay && rs.reservationStay.name"
                                        doctype="Reservation Stay" :docname="rs.reservationStay.name" />
                                </div>
                            </div>
                        </div>
                        <div class="col-4">
                            <div class="grid">
                                <ComReservationStayDetailChargeSummary @onViewReservation="OnViewReservation()" />
                                <ComArrivalAndDeparture />
                            </div>
                            <hr class="mt-2">
                            <div class="mt-3">
                                    <div class="line-height-1 flex p-0 flex-col justify-center gap-2 w-full text-sm white-space-nowrap overflow-hidden text-overflow-ellipsis">
                                        <div>
                                             <span class="italic">Created by: </span> 
                                             <span class="text-500 font-italic">
                                                {{ rs.reservationStay?.owner }} {{gv.datetimeFormat(rs.reservation?.creation) }}
                                             </span> 
                                        </div>
                                        <div>
                                             <span class="italic">Last Modified: </span>
                                             <span class="text-500 font-italic">
                                                {{ rs.reservationStay?.modified_by }} {{ gv.datetimeFormat(rs.reservation?.modified) }}
                                             </span>
                                        </div>
                                        <div>
                                            <span class="italic">Checked-out by: </span>
                                            <span class="text-500 font-italic">
                                                {{ rs.reservationStay?.owner }} {{ gv.datetimeFormat(rs.reservation?.creation) }}
                                            </span>
                                        </div>
                                        <div>
                                            <span class="italic">Checked-in by: </span>
                                            <span class="text-500 font-italic">
                                                {{ rs.reservationStay?.owner }} {{ gv.datetimeFormat(rs.reservation?.creation) }}
                                            </span>
                                        </div>
                                    </div>
                            </div>

                        </div>
                    </div>
                </TabPanel>

                <TabPanel header="Room Rate">
                    <ComReservationStayRoomRate />
                </TabPanel>

                <TabPanel header="Folio">
                   <ComReservationStayFolio/>
                </TabPanel>

                <TabPanel header="Document">
                    <ComDocument doctype="Reservation Stay" :docname="name" />
                </TabPanel>

            </TabView>
        </div>
    </div>
        <template #footer-left>
            <SplitButton class="border-split-none" label="Mores" icon="pi pi-list" :model="more_options_items" />
            <Button @click="onAuditTrail">
                <i class="pi pi-history me-2"></i>Audit Trail
            </Button>
            <ComReservationStayPrintButton :reservation_stay="name" v-if="name" />
            <Button class="border-none" @click="OnViewReservation">
                <ComIcon icon="ViewDetailIcon" style="height: 13px;" class="me-2" /> View Reservation <Badge
                    style="font-weight: 600 !important" :value="rs?.reservationStayNames.length" severity="warning">
                </Badge>
            </Button>
        </template>
        <template #footer-right>
            <Button @click="onCheckIn" class="bg-green-500">
                <ComIcon icon="checkin" style="height: 18px;" class="me-2" />Check In
            </Button>
            <Button @click="onCheckIn" class="bg-red-400">
                <ComIcon icon="checkout" style="height: 18px;" class="me-2" />Check Out
            </Button>
        </template>

    </ComDialogContent>
</template>
<script setup>

import { inject, ref, onMounted, computed, useToast, useRoute, useRouter, onUnmounted, useDialog } from '@/plugin'
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
import ComReservationNote from './components/ComReservationNote.vue';
import ComAuditTrail from '../../components/layout/components/ComAuditTrail.vue';
import ComReservationStayFolio from '@/views/reservation/components/ComReservationStayFolio.vue';

const rs = inject('$reservation_stay');
const dialog = useDialog()
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
const gv = inject('$gv');

const name = ref("")

const isPage = computed(() => {
    return route.name == 'ReservationStayDetail'
})

const onRefresh = () => {
    rs.getReservationDetail(name.value)
}
onMounted(() => {

    if (!dialogRef) {
        if (route.params.name) {
            name.value = route.params.name
            rs.getReservationDetail(name.value);
        } else {
            alert("Go back to reserveatin list")
        }

    } else {

        name.value = dialogRef.value.data.name;
        rs.getReservationDetail(name.value);
    }


});

function onNavigateStay(isNext) {

    const stay_name = rs.getStayName(name.value, isNext)

    if (stay_name) {

        if (isPage.value) {

            router.push({ name: 'ReservationStayDetail', params: { name: stay_name } })
        }
        name.value = stay_name
        rs.getReservationDetail(stay_name)
    }


}

function onRoute() {
    window.open('stay-detail/' + name.value, '_blank')
}
const onClose = () => {
    dialogRef.value.close()
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

onUnmounted(() => {

    rs.reservation = {}
    rs.reservationStay = {}
    rs.guest = {}
    rs.masterGuest = {}

})


function onAuditTrail() {
    const dialogRef = dialog.open(ComAuditTrail, {
        data: {
            doctype: 'Reservation Stay',
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
// More Options items
const more_options_items = ref([])
more_options_items.value.push({
    label: "Options 1",
    icon: 'pi pi-user-edit',
})
more_options_items.value.push({
    label: "Options 2",
    icon: 'pi pi-user-edit',
})
more_options_items.value.push({
    label: "Options 3",
    icon: 'pi pi-user-edit',
})
</script>
<style scoped>
.p-button {
    border: 0 !important;
}

.border-rl-ed {
    border-right: 1px solid var(--btn-border-color) !important;
    border-left: 1px solid var(--btn-border-color) !important;
}

.min-whidth-modified {
    line-height: 1.4;
}

</style>