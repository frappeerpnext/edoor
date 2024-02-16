<template>
    
    <ComDialogContent :loading="rs.loading" hideButtonOK :hideButtonClose="true" @onClose="onClose" :isDialog="!isPage">
        <div :class="(rs.loading ? 'opacity-10 bg-black' : '')">
            <div :class="[isPage, 'bg-white']">
                <div class="overflow-auto w-full">
                    <div class="flex mb-3 justify-between stickyReservationStatus overflow-scroll lg:overflow-hidden w-full lg:w-full">
                        <ComReservationStayHeaderStatus />
                        <div class="flex gap-2">
                            <button @click="onRefresh" v-tippy="'Refresh'" :loading="rs?.loading"
                                class="rounded-lg conten-btn flex" link>
                                <icon class="pi pi-refresh font-semibold text-lg m-auto" style="color:var(--bg-purple-cs);">
                                </icon>
                            </button>
                            <button @click="onRoute" v-tippy="'Open New Window'" v-if="!isPage" class="rounded-lg conten-btn hidden lg:inline-block"
                                link>
                                <ComIcon icon="iconOpenBrower" style="height:18px;"></ComIcon>
                            </button>
                            <div class="ms-2" v-if="rs?.reservationStayNames.length > 1">
                                <Button v-if="rs?.reservationStayNames.length > 1" @click="onNavigateStay(-1)"
                                    :disabled="rs?.canNavigatePrevious(name) || rs.loading" icon="pi pi-angle-double-left"
                                    class="border-noround-right border-y-none border-left-none">
                                </Button>
                                <Button class="border-noround border-rl-ed border-none">{{
                                    (rs?.reservationStayNames.indexOf(rs.reservationStay?.name)) + 1 }} / {{rs?.reservationStayNames.length }} </Button>
                                <Button v-if="rs?.reservationStayNames.length > 1" @click="onNavigateStay(1)"
                                    :disabled="rs?.canNavigateNext(name) || rs.loading"
                                    class="border-noround-left border-y-none border-right-none"
                                    icon="pi pi-angle-double-right"></Button>
                            </div>
                        </div>
                    </div>
                </div>
                <Message v-if="rs.reservationStay && rs.reservationStay?.reservation_status == 'No Show'">
                    <div class="flex items-center gap-3"
                        v-if="rs.reservationStay?.stays?.filter(r => r.show_in_room_chart == 1).length > 0 && rs.reservationStay?.reservation_status == 'No Show'">
                        <span>
                            We reserved room for this reservation.
                        </span>
                        <Button @click="onUnreservedRoom" class="conten-btn border-1" serverity="waring">Unreserve
                            Room</Button>
                    </div>
                    <div class="flex items-center gap-3" v-else>
                        <span>We do not reserved room for this reservation.</span>
                        <Button @click="onReservedRoom" class="conten-btn border-1" serverity="waring">Reserve Room</Button>
                    </div>
                </Message>
                <Message v-if="rs.reservationStay.reservation_status=='Checked Out' && rs.reservationStay.departure_date != rs.reservationStay.checked_out_system_date" severity="info">
                    This guest is early checked out. Check out date is {{  moment(rs.reservationStay.checked_out_system_date).format("DD-MM-YYYY") }}
                </Message>
                <TabView lazy v-model:activeIndex="activeTab" class="tabview-custom">
                    <TabPanel header="General Information">
                        <div class="grid mt-2 ml-0 ms-0">
                            <div class="col-12 lg:col-8 pl-0">
                                <div class="grid">
                                    <div class="col-12 lg:col-4">
                                        <div class="grid">
                                            <div class="col-12">
                                                <ComReservationStayDetailGuestInfo />
                                            </div>
                                            <div class="col-12">
                                                <ComReservationBusinessSourceAndRate />
                                            </div>
                                        </div>
                                    </div>
                                    <div class="col-12 lg:col-8">
                                        <ComReservationStayInfo />
                                    </div>
                                    <div class="col-12" v-if="isMobile">
                                        <div class="grid">
                                            <ComReservationStayDetailChargeSummary
                                            @onViewReservation="OnViewReservation()"/>
                                            <ComArrivalAndDeparture/>
                                        </div>
                                    </div>
                                    <div class="col-12">
                                        <ComReservationRoomStayList />
                                    </div>
                                    <div class="col-12"> 
                                        <ComReservationStayNote />
                                    </div>
                                    <div class="col-12">
                                        <hr>
                                    </div>
                                    <div class="col-12">
                                        <ComCommentAndNotice v-if="name" doctype="Reservation Stay"
                                            :docname="name"
                                            :filters="['custom_reservation_stay','=', name]"
                                                
                                            />
                                    </div>
                                </div>
                            </div>
                            <div class="col-12 lg:col-4" v-if="!isMobile">
                                <div class="grid">
                                    <ComReservationStayDetailChargeSummary v-if="can_view_rate"
                                        @onViewReservation="OnViewReservation()"/>
                                    <ComArrivalAndDeparture/>
                                </div>
                            </div>
                        </div>
                    </TabPanel>
                    <TabPanel header="Room Rate" v-if="can_view_rate">
                        <ComReservationStayRoomRate />
                    </TabPanel>
                    <TabPanel>
                        <template #header>
                            <span class="me-2">Folio</span>
                            <Badge :value="rs.totalFolio"></Badge>
                        </template>
                        <ComReservationStayFolio />
                    </TabPanel>
                    <TabPanel>
                        <template #header>
                            <span class="me-2">Document</span>
                            <ComDocumentBadge doctype="Reservation Stay"
                                :doctypes="['Reservation Stay', 'Reservation Folio', 'Folio Transaction']" :docname="name"
                                :attacheds="rs.attacheds" v-if="name && rs.attacheds.length > 0" />
                        </template>
                        <ComDocument doctype="Reservation Stay"
                            :doctypes="['Reservation Stay', 'Reservation Folio', 'Folio Transaction']" :docname="name"
                            :fill="false"  />
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
                        {{ rs.reservationStay?.owner?.split("@")[0] }}
                        <ComTimeago :date="rs.reservationStay?.creation"/>  
                    </span>
                </div>
                <div>
                    <span class="italic"> Last Modified: </span>
                    <span class="text-500 font-italic">
                        {{ rs.reservationStay?.modified_by?.split("@")[0] }}
                        <ComTimeago :date="rs.reservationStay?.modified"/>  
                    </span>
                </div>
                <div v-if="rs.reservationStay?.checked_in_by || rs.reservationStay?.checked_out_by">
                    <div v-if="rs.reservationStay.checked_in_by || rs.reservationStay.checked_in_date" class="inline">
                        <span class="italic">Checked-in by: </span>
                        <span class="text-500 font-italic">
                            {{ rs.reservationStay.checked_in_by?.split("@")[0] }}
                        <ComTimeago :date="rs.reservationStay?.checked_in_date"/>  
                        </span>
                    </div>
                    
                </div>
                <div v-if="rs.reservationStay?.checked_in_by || rs.reservationStay?.checked_out_by">
                    
                    <div v-if="rs.reservationStay?.checked_out_by || rs.reservation?.checked_out_date" class="inline">
                        <span class="italic">Checked-out by: </span>
                        <span class="text-500 font-italic">
                            {{ rs.reservationStay?.checked_out_by?.split("@")[0] }} 
                        <ComTimeago :date="rs.reservationStay?.checked_out_date"/>  

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
            <Button v-if="rs.canCheckIn() && rs.reservationStay?.reservation_status != 'In-house'" @click="onCheckIn"
                class="bg-green-500 border-none">
                <ComIcon icon="checkin" style="height: 18px;" class="me-2" />Check In
            </Button>
            <Button
                v-if="rs.reservationStay?.reservation_status === 'In-house' && (moment(working_day.date_working_day) >= moment(rs.reservationStay.departure_date).add(-1, 'day'))"
                @click="onCheckOut" class="bg-red-400 border-none">
                <ComIcon icon="checkout" style="height: 18px;" class="me-2" />Check Out
            </Button>
        </template>
    </ComDialogContent>
</template>

<script setup>
import { inject, ref, onMounted, computed, useRoute, useRouter, onUnmounted, useDialog, postApi } from '@/plugin'
import { useConfirm } from "primevue/useconfirm";
import ComReservationStayPrintButton from "@/views/reservation/components/ComReservationStayPrintButton.vue"
import ComReservationStayRoomRate from '@/views/reservation/components/ComReservationStayRoomRate.vue';
import ComReservationStayDetailGuestInfo from './components/ComReservationStayDetailGuestInfo.vue';
import ComReservationStayDetailChargeSummary from './components/ComReservationStayDetailChargeSummary.vue';
import ComReservationBusinessSourceAndRate from '@/views/reservation/components/ComReservationBusinessSourceAndRate.vue';
import ComReservationStayInfo from './components/ComReservationStayInfo.vue';
import ComReservationRoomStayList from './components/ComReservationRoomStayList.vue'
import ComArrivalAndDeparture from './components/ComArrivalAndDeparture.vue';
import ComCommentAndNotice from '@/components/form/ComCommentAndNotice.vue';
import ComReservationStayNote from './components/ComReservationStayNote.vue';
import ComAuditTrail from '@/components/layout/components/ComAuditTrail.vue';
import ComReservationStayFolio from '@/views/reservation/components/ComReservationStayFolio.vue';
import ComReservationStayHeaderStatus from '@/views/reservation/components/ComReservationStayHeaderStatus.vue'
import ComReservationStayMoreOptionsButton from '@/views/reservation/components/ComReservationStayMoreOptionsButton.vue'
import ComConfirmCheckIn from '@/views/reservation/components/confirm/ComConfirmCheckIn.vue'
import Message from 'primevue/message';

const isMobile = ref(window.isMobile)

const rs = inject('$reservation_stay');
const dialog = useDialog()
const route = useRoute()
const router = useRouter()
const moment = inject("$moment")
const confirm = useConfirm()
const dialogRef = inject("dialogRef");
const activeTab = ref(0)
const name = ref("")
const working_day = JSON.parse(localStorage.getItem("edoor_working_day"))
const can_view_rate = ref(window.can_view_rate)
const isPage = computed(() => {
    return route.name == 'ReservationStayDetail'
})


const onRefresh = debouncer(() => {
    loadData()
}, 500);

function loadData(show_loading=true,delay_load_reservation_stay=0){
    
    setTimeout(() => {    
        rs.getReservationDetail(name.value,show_loading) 
        rs.getChargeSummary(name.value)
        
    }, delay_load_reservation_stay);
    
    rs.selectedRoomRates = []
    //load comment  
    window.postMessage({ action: "load_comment" }, "*") 
    if (activeTab.value == 1) {
        rs.getRoomRate(name.value)
    } else if (activeTab.value == 2) {  
        window.postMessage({ action: "load_reservation_stay_folio_list" }, "*")
    } else if (activeTab.value == 3) { 
        window.postMessage({ action: "refresh_document", docname: name.value })
        window.postMessage({ action: "refresh_document_count", docname: name.value })
    }
}

function onUnreservedRoom() {
    confirm.require({
        message: 'Are you sure you want to unreserve room for this reservation?',
        header: 'Confirmation',
        icon: 'pi pi-exclamation-triangle',
        acceptClass: 'border-none crfm-dialog',
        rejectClass: 'hidden',
        acceptIcon: 'pi pi-check-circle',
        acceptLabel: 'Ok',
        accept: () => {
            postApi("reservation.unreserved_room", {
                property: rs.reservation.property,
                reservation_stay: rs.reservationStay.name
            }).then((resul) => {
                rs.getReservationDetail(rs.reservationStay.name)
                window.postMessage({action:"ReservationStayList"},"*")
                window.postMessage({action:"ReservationList"},"*")
                window.postMessage({action:"GuestLedger"},"*")
                window.postMessage({action:"GuestLedgerTransaction"},"*")
                window.postMessage({action:"Reports"},"*")
            })
        },
    });
}


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
function onReservedRoom() {
    confirm.require({
        message: 'Are you sure you want to reserve room for this reservation?',
        header: 'Confirmation',
        icon: 'pi pi-exclamation-triangle',
        acceptClass: 'border-none crfm-dialog',
        rejectClass: 'hidden',
        acceptIcon: 'pi pi-check-circle',
        acceptLabel: 'Ok',
        accept: () => {
            postApi("reservation.reserved_room", {
                property: rs.reservation.property,
                reservation_stay: rs.reservationStay.name
            }).then((resul) => {
                rs.getReservationDetail(rs.reservationStay.name)
                window.postMessage({action:"ReservationList"},"*")
                window.postMessage({action:"ReservationStayList"},"*")
                window.postMessage({action:"GuestLedger"},"*")
                window.postMessage({action:"GuestLedgerTransaction"},"*")
                window.postMessage({action:"Reports"},"*")
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
        }
        window.reservation_stay = route.params.name
    } else {
        name.value = dialogRef.value.data.name;
        rs.getReservationDetail(name.value);
        rs.getChargeSummary(name.value)
        rs.is_page = false
        window.reservation_stay = dialogRef.value.data.name
    }
    window.addEventListener('message', actionRefreshData, false); 
});

const actionRefreshData = async function (e) {
    if (e.isTrusted && typeof (e.data) != 'string') {
        if(e.data.action=="ReservationStayDetail"){
            setTimeout(()=>{
                loadData(false,0)
            },1000*2)
            
        }
    };
}


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
                width: '650px',
            },
            modal: true,
            closeOnEscape: false,
            pt: {
                root: `${window.isMobile ? 'p-dialog-maximized' : ''}`
            }
        },
        onClose: (options) => {
            const result = options.data;
            if (result) {
                rs.loading = true
                postApi("reservation.check_in", {
                    reservation: rs.reservation.name,
                    reservation_stays: [rs.reservationStay.name],
                    note: result.note
                }).then((result) => {
                    rs.loading = false
                    window.postMessage({"action":"ComHousekeepingStatus"},"*");
                    window.postMessage({"action":"Dashboard"},"*")
                    window.postMessage({action:"ReservationList"},"*")
                    window.postMessage({action:"ReservationDetail"},"*")
                    window.postMessage({action:"Frontdesk"},"*")
                    window.postMessage({action:"TodaySummary"},"*")
                    window.postMessage({action:"GuestLedger"},"*")
                    window.postMessage({action:"GuestLedgerTransaction"},"*")
                    window.postMessage({action:"Reports"},"*")
        	        window.postMessage({action:"FolioTransactionList"},"*")

                    onRefresh(false)
                })
                    .catch((err) => {
                        rs.loading = false
                    })
            }
        }
    })
}
const onCheckOut = () => {
    confirm.require({
        message: 'Are you sure you want to check out this room?',
        header: 'Confirmation',
        acceptLabel: 'OK',
        rejectVisible: true,
        rejectClass: 'hidden',
        acceptClass: 'border-none',
        acceptIcon: 'pi pi-check-circle',
        icon: 'pi pi-exclamation-triangle',
        accept: () => {
            rs.loading = true
            postApi("reservation.check_out", {
                reservation: rs.reservation.name,
                reservation_stays: [rs.reservationStay.name]
            }, "Check out successfully")
                .then((result) => {
                    rs.loading = false
                    onRefresh()
                    window.postMessage({"action":"ComHousekeepingStatus"},"*");
                    window.postMessage({"action":"Dashboard"},"*")
                    window.postMessage({action:"ReservationStayList"},"*")
                    window.postMessage({action:"ReservationList"},"*") 
                    window.postMessage({action:"ReservationDetail"},"*")
                    window.postMessage({action:"Frontdesk"},"*")
                    window.postMessage({action:"TodaySummary"},"*")
                    window.postMessage({action:"GuestLedger"},"*")
                    window.postMessage({action:"GuestLedgerTransaction"},"*")
                    window.postMessage({action:"Reports"},"*")
        	        window.postMessage({action:"FolioTransactionList"},"*")
                    window.socket.emit("ComRunNightAudit", { property: window.property_name })

                })
                .catch((err) => {
                    rs.loading = false
                })
        }
    });
}
const OnViewReservation = () => {

    if (window.has_reservation_detail_opened == true) {
       
        if (window.reservation = rs.reservationStay.reservation) {
            dialogRef.value.close();
        } else {
            window.postMessage('view_reservation_detail|' + rs.reservationStay.reservation, '*')
        }
    } else {
        if (dialogRef?.value){
            dialogRef.value.close();
        }
        
        window.postMessage('view_reservation_detail|' + rs.reservationStay.reservation, '*')
    }
}
onUnmounted(() => {
    rs.clear() 
    window.removeEventListener('message', actionRefreshData, false);
    window.reservation_stay = ""
})
function onAuditTrail() {
    const dialogRef = dialog.open(ComAuditTrail, {
        data: {
            doctype: 'Reservation Stay',
            docname: name.value,
            referenceTypes: [
                { doctype: 'Reservation Stay', label: 'Reservation stay' },
                { doctype: 'Reservation Room Rate', label: 'Room Rate' },
                { doctype: 'Customer', label: 'Guest' },
                { doctype: 'Reservation Folio', label: 'Reservation Folio' },
                { doctype: 'Folio Transaction', label: 'Folio Transaction' },
            ],
            filter_key: "custom_reservation_stay"
        },
        props: {
            header: 'Audit Trail',
            style: {
                width: '80vw',
            },
            modal: true,
            maximizable: true,
            closeOnEscape: false,
            position: "top",
            pt: {
                root: `${window.isMobile ? 'p-dialog-maximized' : ''}`
            }
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