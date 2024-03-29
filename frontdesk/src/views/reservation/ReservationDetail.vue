<template>
    <ComDialogContent hideButtonOK :hideButtonClose="true" @onClose="onClose" @onMaximize="onMaximize" :isDialog="!isPage"
        :loading="rs.loading">
        <div :class="[isPage, 'bg-white']">
            <div class="grid stickyReservationStatus" style="height:40px;">
                <div :class="isPage ? 'col py-3' : 'col pt-0'">
                    <div class="flex justify-between">
                        <div class="flex align-items-center">
                            <div class="flex">
                                <ComTagReservation title="RS#:" :value="rs.reservation?.name" class="bg-card-info p-1px">
                                    <span class="res__bagde ml-1">
                                        {{ rs.reservationStays.length }}
                                    </span>
                                </ComTagReservation>
                                <div v-tippy="$t('Free Independent Traveler')"
                                    v-if="rs.reservation?.reservation_type == 'FIT'"
                                    class="flex items-center justify-center px-2 rounded-lg me-2 text-white p-1px bg-teal-500">
                                    <span class="">
                                        <ComIcon style="height: 15px;" class="m-auto" icon="userFitWhite" />
                                    </span>
                                </div>
                                <div v-tippy="$t('Group Inclusive Tour')" v-else
                                    class="flex items-center justify-center px-2 rounded-lg me-2 text-white p-1px bg-yellow-500">
                                    <span>
                                        <ComIcon style="height: 15px;" class="m-auto" icon="userGroupWhite" />
                                    </span>
                                </div>
                                <span class="px-2 rounded-lg me-2 text-white p-1px"
                                    :style="{ background: rs.reservation?.status_color }">
                                    {{ $t(rs.reservation?.reservation_status || "" ) }}
                                </span>
                            </div>
                        </div>
                        <div class="flex gap-2">
                            <button @click="onRefresh" v-tippy="$t('Refresh')" :loading="rs?.loading"
                                class="rounded-lg conten-btn flex" link>
                                <icon class="pi pi-refresh font-semibold text-lg m-auto" style="color:var(--bg-purple-cs);">
                                </icon>
                            </button>
                            <button @click="onRoute" v-tippy="$t('Open New Window')" v-if="!isPage"
                                class="rounded-lg conten-btn hidden lg:block" link>
                                <ComIcon icon="iconOpenBrower" style="height:18px;"></ComIcon>
                            </button>
                        </div>
                    </div>
                </div>
            </div>

            <TabView lazy v-model:activeIndex="activeTab" class="tabview-custom">
                <TabPanel :header="$t('General Information')">
                    <div class="grid mt-2 ml-0 ms-0">
                        <div class="col-12 lg:col pl-0">
                            <div class="grid">
                                <div class="col-12 lg:col-4">
                                    <div class="grid">
                                        <div class="col-12">
                                            <ComReservationDetailGuestInfo />
                                        </div>
                                        <div class="col-12">
                                            <ComReservationDetailBusinessSourceAndRate />
                                        </div>
                                    </div>

                                </div>
                                <div class="col-12 lg:col-8 pb-0">
                                    <ComReservationInfo />
                                </div>
                            </div>
                        </div>
                        <div v-if="can_view_rate" class="col-12 lg:col-4 pb-0"> 
                            <div class="grid">
                                <ComReservationDetailChargeSummary />
                            </div>
                        </div>
                    </div>
                    <div class="pt-2">
                        <ComReservationDetailRoomList />
                    </div>
                    <div class="pt-3">
                        <div class="border-round-xl">
                            <ComReservationNote v-if="!rs.loading && rs.reservation && rs.reservation.name"
                                doctype="Reservation" />
                        </div>
                    </div>
                    <hr class="my-3" />
                    <div>
                        <div class="border-round-xl">

                            <ComCommentAndNotice v-if="!rs.loading && name" doctype="Reservation"
                                :docname="rs?.reservation?.name" :filters="['custom_reservation', '=', name]" />
                        </div>
                    </div>
                </TabPanel>

                <TabPanel v-if="can_view_rate" :header="$t('Room Rate')">
                    <ComReservationRoomRate />
                </TabPanel>

                <TabPanel v-if="can_view_rate">
                    <template #header>
                        <span class="me-2">{{ $t('Folio') }} </span>
                        <Badge :value="rs.totalFolio"></Badge>
                    </template>
                    <ComReservationFolio />
                </TabPanel>
                <TabPanel>
                    <template #header>
                            <span class="me-2">{{ $t('Document') }} </span>
                            <Badge :value="totalDocument"></Badge>
                    </template>

                    <ComDocument doctype="Reservation"
                        :doctypes="['Reservation Stay', 'Reservation', 'Customer', 'Reservation Folio', 'Folio Transaction']"
                        :attacheds="rs.attacheds" :docname="name" @updateCount="onUpdateDocumentCount" />
                </TabPanel>

            </TabView>
        </div>
        <template #footer-left>
            <div class="flex justify-end gap-2">
                <ComReservationMoreOptionsButton />
                <ReservationPrintButton :reservation="name" />
                <Button class="border-none" @click="onAddRoomMore" icon="pi pi-plus" :label="$t('Add More Room')" />
            </div>

        </template>
        <template #footer-right>

            <Button v-if="canCheckIn.length > 0" class="border-none bg-green-500" @click="onCheckIn">
                <ComIcon icon="checkin" style="height: 18px;" class="me-2" />
{{ $t('Check In') }}
            </Button>
        </template>
    </ComDialogContent>
</template>

<script setup>
import { inject, ref, onMounted, computed, useToast, useRoute, onUnmounted, useDialog, postApi } from '@/plugin'

import ComTagReservation from '@/views/reservation/components/ComTagReservation.vue';
import ComReservationDetailGuestInfo from '@/views/reservation/components/ComReservationDetailGuestInfo.vue'
import ComReservationInfo from '@/views/reservation/components/ComReservationInfo.vue'
import ComReservationDetailBusinessSourceAndRate from '@/views/reservation/components/ComReservationDetailBusinessSourceAndRate.vue'
import ComReservationDetailRoomList from '@/views/reservation/components/ComReservationDetailRoomList.vue'
import ComReservationDetailChargeSummary from '@/views/reservation/components/ComReservationDetailChargeSummary.vue'
import ComReservationRoomRate from '@/views/reservation/components/ComReservationRoomRate.vue'
import ComCommentAndNotice from '@/components/form/ComCommentAndNotice.vue';
import ComReservationNote from './components/ComReservationNote.vue';
import ComConfirmCheckIn from '@/views/reservation/components/confirm/ComConfirmCheckIn.vue'
import ComReservationFolio from '@/views/reservation/components/reservation_folio/ComReservationFolio.vue'
import ReservationPrintButton from '@/views/reservation/components/ReservationPrintButton.vue'
import ComReservationStayAddMore from './components/ComReservationStayAddMore.vue'

import ComReservationMoreOptionsButton from './components/ComReservationMoreOptionsButton.vue'
import {i18n} from '@/i18n';
const { t: $t } = i18n.global; 
const moment = inject('$moment');
const can_view_rate = window.can_view_rate
const activeTab = ref(0)
const route = useRoute()

const rs = inject("$reservation")

const toast = useToast()
const dialogRef = inject("dialogRef");

const property = JSON.parse(localStorage.getItem("edoor_property"))

const name = ref("")
const dialog = useDialog()
const working_day = JSON.parse(localStorage.getItem("edoor_working_day"))
const totalDocument = ref(0)

const isPage = computed(() => {
    return route.name == 'ReservationDetail'
})
const canCheckIn = computed(() => {
    const can_check_in = rs.reservationStays.filter((r) => r.reservation_status === 'Reserved' && moment(r.arrival_date).toDate() <= moment(working_day.date_working_day).toDate());
    return can_check_in;
});


const onRefresh = debouncer((showLoading = true) => {
    rs.LoadReservation(name.value, showLoading);
    if (activeTab.value == 0) {
        rs.getChargeSummary(name.value)

    } else if (activeTab.value == 2) {
        window.postMessage({ action: "load_reservation_folio_list", reservation: name.value }, "*")
        window.postMessage({ action: "load_folio_transaction" }, "*")
    } else if (activeTab.value == 1) {
        rs.getRoomRate(name.value, showLoading);
    }
    else if (activeTab.value == 3) {
        window.postMessage({ action: "refresh_document", docname: name.value })
        window.postMessage({ action: "refresh_document_count", docname: name.value })
    }
}, 500);

function debouncer(fn, delay) {
    var timeoutID = null;
    return function () {
        clearTimeout(timeoutID);
        var args = arguments;
        var that = this;
        timeoutID = setTimeout(function () {
            fn.apply(that, args);
        }, delay);
    };
}
function onRoute() {
    window.open('reservation-detail/' + name.value, '_blank')
}
function onClose() {
    dialogRef.value.close()
}
function onMaximize() {
    dialogRef.value.maximize()
}

function onUpdateDocumentCount(n){
    totalDocument.value = n
}
onMounted(() => {
    if(window.isMobile){
        let elem = document.querySelectorAll(".p-dialog");
        if (elem){
            elem = elem[elem.length-1]
            elem?.classList.add("p-dialog-maximized"); // adds the maximized class
        }
    }
    window.has_reservation_detail_opened = true

    if (!dialogRef) {
        if (route.params.name) {
            name.value = route.params.name
            onRefresh()
        }
    } else {
        name.value = dialogRef.value.data.name;
        if (dialogRef.value.data.delay_load_data) {
            rs.loading = true
            setTimeout(() => {
                onRefresh()
            }, dialogRef.value.data.delay_load_data);
        }
        else {
            onRefresh()
        }
    } 
    window.reservation = name.value 
    window.addEventListener('message', actionRefreshData, false);
});

const actionRefreshData = async function (e) {
    if (e.isTrusted && typeof (e.data) != 'string') {
        if(e.data.action=="ReservationDetail"){
            setTimeout(()=>{
                onRefresh(false)
            },1000*2) 
        }
    };
}

onUnmounted(() => {
    rs.clear() 
    window.removeEventListener('message', actionRefreshData, false);
    window.has_reservation_detail_opened = false
    window.reservation = ""
})

function onCheckIn() {
    if (rs.selecteds.length == 0) {
        if (rs.reservationStays.length > 1) {
            toast.add({ severity: 'warn', summary: "Group Check In", detail: "Please select reservation stay to check in.", life: 3000 })
            return
        } else {
            rs.selecteds = rs.reservationStays
        }

    }
    const dialogRef = dialog.open(ComConfirmCheckIn, {
        data: {
            stays: rs.selecteds
        },
        props: {
            header: 'Confirm Check In',
            style: {
                width: '450px',
            },
            modal: true,
            closeOnEscape: false,
            breakpoints:{
                '960px': '450px',
                '640px': '100vw'
            },
        },
        onClose: (options) => {
            const result = options.data;

            if (result) {
                rs.loading = true

                postApi("reservation.check_in", {
                    reservation: rs.reservation.name,
                    reservation_stays: rs.selecteds.map(d => d["name"])
                }).then((result) => {
                    rs.loading = false
                    rs.LoadReservation(rs.reservation.name, false);
                    window.postMessage({"action":"Dashboard"},"*")
                    window.postMessage({action:"ReservationList"},"*")
                    window.postMessage({action:"Reports"},"*")
                    window.postMessage({action:"ReservationStayDetail"},"*")
                    window.postMessage({action:"FolioTransactionList"},"*")


                })
                    .catch((err) => {
                        rs.loading = false
                    })
            }
        }
    })
}
function onAddRoomMore() {
    const dialogRef = dialog.open(ComReservationStayAddMore, {
        props: {
            header: $t('Add More Room'),
            style: {
                width: '80vw',
            },
            maximizable: true,
            modal: true,
            closeOnEscape: false,
            position: 'top',
            breakpoints:{
                '960px': '80vw',
                '640px': '100vw'
            },
        },
        onClose: (options) => {
            const data = options.data;

            if (data) {
                setTimeout(() => {

                    rs.LoadReservation(data.name, false)
                }, 1000);
            }
        }
    });
}

const items = ref([

]);
</script>

<style scoped>
.res__bagde {
    border-radius: 0.5rem;
    padding: 0 5px;
    background: #cacaca;
    position: relative;
    right: -3px;
}

.min-whidth-modified {
    line-height: 1.4;
}
</style>
