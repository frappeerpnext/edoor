<template>
    <ComDialogContent :loading="rs.loading" hideButtonOK :hideButtonClose="true" @onClose="onClose" :isDialog="!isPage">
        <div :class="(rs.loading ? 'opacity-10 bg-black' : '')">

            <div :class="[isPage, 'bg-white']">
                <div class="flex mb-3 justify-between">
                    <ComReservationStayHeaderStatus />

                    <div class="flex gap-2">
                        <button @click="onRefresh" v-tooltip.left="'Refresh'" :loading="rs?.loading"
                            class="rounded-lg conten-btn flex" link>
                            <icon class="pi pi-refresh font-semibold text-lg m-auto" style="color:var(--bg-purple-cs);">
                            </icon>
                        </button>
                        <button @click="onRoute" v-tooltip.left="'Open New Window'" v-if="!isPage"
                            class="rounded-lg conten-btn " link>
                            <ComIcon icon="iconOpenBrower" style="height:18px;"></ComIcon>
                        </button>
                        <div class="ms-2" v-if="rs?.reservationStayNames.length > 1">
                            <Button v-if="rs?.reservationStayNames.length > 1" @click="onNavigateStay(-1)"
                                :disabled="rs?.canNavigatePrevious(name) || rs.loading" icon="pi pi-angle-double-left"
                                class="border-noround-right border-y-none border-left-none">
                            </Button>
                            <Button class="border-noround border-rl-ed border-none">{{
                                (rs?.reservationStayNames.indexOf(rs.reservationStay?.name))
                                + 1 }} / {{ rs?.reservationStayNames.length }} </Button>
                            <Button v-if="rs?.reservationStayNames.length > 1" @click="onNavigateStay(1)"
                                :disabled="rs?.canNavigateNext(name) || rs.loading"
                                class="border-noround-left border-y-none border-right-none"
                                icon="pi pi-angle-double-right"></Button>
                        </div>
                    </div>
                </div>
                <Message v-if="rs.reservationStay && rs.reservationStay?.reservation_status=='No Show'">
                  
                    <div 
                        class="flex items-center gap-3"
                        v-if="rs.reservationStay?.stays?.filter(r => r.show_in_room_chart == 1).length > 0 && rs.reservationStay?.reservation_status == 'No Show'">
                        <span>
                            We reserved room for this reservation.
                        </span>
                        <Button @click="onUnreservedRoom" class="conten-btn border-1" serverity="waring">Unreserve Room</Button>
                    </div>
                    <div class="flex items-center gap-3" v-else>
                        <span>We do not reserved room for this reservation.</span>
                        <Button @click="onReservedRoom" class="conten-btn border-1" serverity="waring">Reserve Room</Button>
                    </div>
                </Message>
                <TabView lazy v-model:activeIndex="activeTab">
                    <TabPanel header="General Information">
                        <div class="grid mt-2 ml-0 ms-0">
                            <div class="col-8 pl-0">
                                <div class="grid">
                                    <div class="col-4">
                                        <div class="grid">
                                            <div class="col-12">
                                                <ComReservationStayDetailGuestInfo />
                                            </div>
                                            <div class="col-12">
                                                <ComReservationBusinessSourceAndRate />
                                            </div>
                                        </div>
                                    </div>
                                    <div class="col-8">
                                        <ComReservationStayInfo />
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
                                        <ComCommentAndNotice v-if="!rs.loading && rs.reservationStay.name"
                                            doctype="Reservation Stay" :docname="rs.reservationStay.name" />
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

                        <ComReservationStayFolio />
                    </TabPanel>

                    <TabPanel header="Document">
                        <ComDocument doctype="Reservation Stay" :docname="name" v-if="!rs.loading" />
                    </TabPanel>

                </TabView>
            </div>
        </div>
        <hr class="mt-2">
        <div :class="rs.is_page ? 'mt-2 mb-2' : 'mt-2 -mb-2'">
            <div
                class="line-height-1 text-right flex p-0 flex-col justify-center gap-2 w-full text-sm white-space-nowrap overflow-hidden text-overflow-ellipsis">
                <div>
                    <span class="italic">Created by: </span>
                    <span class="text-500 font-italic">
                        {{ rs.reservationStay?.owner }} {{ gv.datetimeFormat(rs.reservation?.creation) }}
                    </span>
                    <span class="italic"> Last Modified: </span>
                    <span class="text-500 font-italic">
                        {{ rs.reservationStay?.modified_by }} {{ gv.datetimeFormat(rs.reservation?.modified) }}
                    </span>
                </div>
                <div v-if="rs.reservationStay?.checked_in_by || rs.reservationStay?.checked_out_by">
                    <div v-if="rs.reservationStay.checked_in_by || rs.reservationStay.checked_in_date" class="inline">
                        <span class="italic">Checked-in by: </span>
                        <span class="text-500 font-italic">
                            {{ rs.reservationStay.checked_in_by }} {{ gv.datetimeFormat(rs.reservationStay.checked_in_date)
                            }}
                        </span>
                    </div>
                    <div v-if="rs.reservationStay?.checked_out_by || rs.reservation?.checked_out_date" class="inline">
                        <span class="italic"> Checked-out by: </span>
                        <span class="text-500 font-italic">
                            {{ rs.reservationStay?.checked_out_by }} {{ gv.datetimeFormat(rs.reservation?.checked_out_date)
                            }}
                        </span>
                    </div>
                </div>
            </div>
        </div>
        <!-- <hr class="mt-2" v-if="rs?.is_page"> -->
        <template #footer-left>
            <ComReservationStayMoreOptionsButton @onAuditTrail="onAuditTrail()" @onRefresh="onRefresh(false)" />

            <ComReservationStayPrintButton :reservation_stay="name" :folio_number="rs.selectedFolio?.name" v-if="name" />
            <Button class="border-none" @click="OnViewReservation">
                <ComIcon icon="ViewDetailIcon" style="height: 13px;" class="me-2" /> View Reservation <Badge
                    style="font-weight: 600 !important;" class="badge-rs" :value="rs?.reservationStayNames.length"
                    severity="warning">
                </Badge>
            </Button>
        </template>
        <template #footer-right>

            <Button v-if="rs.canCheckIn()" @click="onCheckIn" class="bg-green-500 border-none">
                <ComIcon icon="checkin" style="height: 18px;" class="me-2" />Check In
            </Button>
            <Button
                v-if="rs.reservationStay?.reservation_status == 'In-house' && (moment(working_day.date_working_day) >= moment(rs.reservation.departure_date).add(-1, 'day'))"
                @click="onCheckOut" class="bg-red-400 border-none">
                <ComIcon icon="checkout" style="height: 18px;" class="me-2" />Check Out
            </Button>

        </template>

    </ComDialogContent>
</template>
<script setup>

import { inject, ref, onMounted, computed, useToast, useRoute, useRouter, onUnmounted, useDialog, postApi } from '@/plugin'
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
import ComReservationStayHeaderStatus from '@/views/reservation/components/ComReservationStayHeaderStatus.vue'
import ComReservationStayMoreOptionsButton from '@/views/reservation/components/ComReservationStayMoreOptionsButton.vue'
import ComConfirmCheckIn from '@/views/reservation/components/confirm/ComConfirmCheckIn.vue'
import TestPage2 from '../TestPage2.vue';
import Message from 'primevue/message';
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
const gv = inject('$gv');
const activeTab = ref(0)
const name = ref("")
const working_day = JSON.parse(localStorage.getItem("edoor_working_day"))

const isPage = computed(() => {
    return route.name == 'ReservationStayDetail'
})

const onRefresh = (showLoading = true) => {

    rs.getReservationDetail(name.value, showLoading)
    rs.getChargeSummary(name.value)
    rs.selectedRoomRates = []


    if (activeTab.value == 1) {
        rs.getRoomRate(name.value)
    } else if (activeTab.value == 2) {
        //load folio
        rs.onLoadReservationFolios(name.value)
            .then((doc) => {

                if (doc) {
                    const masterFolio = doc.find(r => r.is_master == 1)
                    if (masterFolio == undefined) {
                        if (doc.length > 0) {
                            rs.onLoadFolioTransaction(doc[0])
                        }
                    } else {
                        rs.onLoadFolioTransaction(masterFolio)
                    }
                }

            })
    }


}
function onUnreservedRoom(){ 
    
    confirm.require({
        message: 'Are you sure you want to unreserve room for this reservation?',
        header: 'Confirmation',
        icon: 'pi pi-exclamation-triangle',
        acceptClass: 'border-none crfm-dialog',
        rejectClass: 'hidden',
        acceptIcon: 'pi pi-check-circle',
        acceptLabel: 'Ok',
        accept: () => {
            postApi("reservation.unreserved_room",{
                property: rs.reservation.property,
                reservation_stay: rs.reservationStay.name
            }).then((resul)=>{
                rs.getReservationDetail(rs.reservationStay.name)
            })  
        },

    });
}
function onReservedRoom(){ 
    confirm.require({
        message: 'Are you sure you want to reserve room for this reservation?',
        header: 'Confirmation',
        icon: 'pi pi-exclamation-triangle',
        acceptClass: 'border-none crfm-dialog',
        rejectClass: 'hidden',
        acceptIcon: 'pi pi-check-circle',
        acceptLabel: 'Ok',
        accept: () => {
            postApi("reservation.reserved_room",{
                property: rs.reservation.property,
                reservation_stay: rs.reservationStay.name
            }).then((resul)=>{
                rs.getReservationDetail(rs.reservationStay.name)
            })  
        },

    });
}

onMounted(() => {

    if (!dialogRef) {
        rs.is_page = true
        if (route.params.name) {
            name.value = route.params.name

            rs.getReservationDetail(name.value);

            rs.getChargeSummary(name.value)

        } else {
            alert("Go back to reserveatin list")
        }

    } else {

        name.value = dialogRef.value.data.name;
        rs.getReservationDetail(name.value);
        rs.getChargeSummary(name.value)
        rs.is_page = false
    }


});

function onNavigateStay(isNext) {
    const stay_name = rs.getStayName(name.value, isNext)

    if (stay_name) {

        if (isPage.value) {

            router.push({ name: 'ReservationStayDetail', params: { name: stay_name } })
        }
        name.value = stay_name
        onRefresh()
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
    const dialogRef = dialog.open(ComConfirmCheckIn, {
        props: {
            header: 'Confirm Check In',
            style: {
                width: '450px',
            },
            modal: true,

            closeOnEscape: false
        },
        onClose: (options) => {
            const result = options.data;

            if (result) {
                rs.loading = true
                postApi("reservation.check_in", {
                    reservation: rs.reservation.name,
                    reservation_stays: [rs.reservationStay.name],

                }).then((result) => {
                    rs.loading = false
                    onRefresh()
                    socket.emit("RefresheDoorDashboard", property.name);
                    socket.emit("RefreshReservationDetail", rs.reservation.name);
                })
                    .catch((err) => {
                        rs.loading = false
                    })
            }
        }


    })
}

const onCheckOut = () => {
    if (rs.reservationStay.balance > 0) {
        toast.add({ severity: 'warn', summary: "You cannot check this reservation because balance is not zero", detail: '', life: 3000 })
        return
    }
    confirm.require({
        message: 'Are you sure you want to check out this room?',
        header: 'Confirmation',
        icon: 'pi pi-exclamation-triangle',
        accept: () => {
            rs.loading = true
            postApi("reservation.check_out", {
                reservation: rs.reservation.name,
                reservation_stays: [rs.reservationStay.name]
            }, "Check out successfully").then((result) => {
                rs.loading = false
                onRefresh()
                socket.emit("RefresheDoorDashboard", property.name);
                socket.emit("RefreshReservationDetail", rs.reservation.name);
            })
                .catch((err) => {
                    rs.loading = false
                })
        }
    });

}

const OnViewReservation = () => {
    dialogRef.value.close({ action: "view_reservation_detail", reservation: rs.reservation.name });
}

onUnmounted(() => {

    rs.clear()


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
            modal: true,
            maximizable: true,
            closeOnEscape: false,
            position: "top"
        },

    });
}

function onTest() {
    const dialogRef = dialog.open(TestPage2, {
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
            position: "top"
        },
    });
}


</script>
<style scoped>


.border-rl-ed {
    border-right: 1px solid var(--btn-border-color) !important;
    border-left: 1px solid var(--btn-border-color) !important;
}

.min-whidth-modified {
    line-height: 1.4;
}</style>