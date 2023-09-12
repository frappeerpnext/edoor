<template>
    <ComDialogContent hideButtonOK :hideButtonClose="true" @onClose="onClose" @onMaximize="onMaximize" :isDialog="!isPage" :loading="rs.loading">
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
                                <div v-tooltip.top="rs.reservation?.reservation_type" v-if="rs.reservation?.reservation_type == 'FIT'" class="flex items-center justify-center px-2 rounded-lg me-2 text-white p-1px bg-teal-500">
                                    <span class="">
                                        <ComIcon style="height: 15px;" class="m-auto" icon="userFitWhite" />
                                    </span>
                                </div>
                                <div v-tooltip.top="rs.reservation?.reservation_type" v-else class="flex items-center justify-center px-2 rounded-lg me-2 text-white p-1px bg-yellow-500">
                                    <span>
                                        <ComIcon style="height: 15px;" class="m-auto" icon="userGroupWhite" />
                                    </span>
                                </div>
                                <span class="px-2 rounded-lg me-2 text-white p-1px"
                                :style="{ background: rs.reservation?.status_color }">{{
                                    rs.reservation?.reservation_status }}
                                </span>
                            </div>
                        </div>
                        <div class="flex gap-2">
                            <button @click="onRefresh" v-tooltip.left="'Refresh'" :loading="rs?.loading"
                                class="rounded-lg conten-btn flex" link>
                                <icon class="pi pi-refresh font-semibold text-lg m-auto" style="color:var(--bg-purple-cs);">
                                </icon>
                            </button>
                            <button @click="onRoute" v-tooltip.left="'Open New Window'" v-if="!isPage"
                                class="rounded-lg conten-btn" link>
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
                            <ComReservationNote v-if="!rs.loading && rs.reservation && rs.reservation.name" doctype="Reservation" />
                        </div>
                    </div>
                    <hr class="my-3" />
                    <div>
                        <div class="border-round-xl">
                            <ComCommentAndNotice v-if="!rs.loading && rs.reservation && rs.reservation.name" doctype="Reservation"
                                :docname="rs.reservation.name" />
                        </div>
                    </div>
                </TabPanel>
                <TabPanel header="Deposit">
                    <ComReservationDeposit />
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
        </div>{{ canCheckIn }}
        {{ working_day.date_working_day }}
        {{ moment(r.arrival_date).toDate() }}
        <template #footer-left>
            <div class="flex justify-end gap-2">  
                <!-- <SplitButton class="border-none" icon="pi pi-list" label="Mores" :model="items" /> -->
                <ComReservationMoreOptionsButton />
                <Button class="border-none" @click="onAddRoomMore" icon="pi pi-plus" label="Add More Room"/>
            </div>
        </template>
        <template #footer-right> 
            <Button v-if="canCheckIn" class="border-none bg-green-500" @click="onCheckIn">
                <ComIcon icon="checkin" style="height: 18px;" class="me-2" />
               
                Check In</Button>
        </template>
    </ComDialogContent>
    <!-- <ComDialogNote :header="note.title" :visible="note.show" :loading="loading" @onOk="onSaveGroupStatus" @onClose="onCloseNote"/> -->
</template>

<script setup>
import { inject, ref, onMounted, computed, useToast, useRoute, onUnmounted, useDialog, postApi } from '@/plugin'
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
import ComConfirmCheckIn from '@/views/reservation/components/confirm/ComConfirmCheckIn.vue'
import AddRoomIcon from '@/assets/svg/icon-add-plus-sign-purple.svg'
import ComReservationStayAddMore from './components/ComReservationStayAddMore.vue'
import ComReservationDeposit from '@/views/reservation/components/deposit/ComReservationDeposit.vue'
import ComReservationMoreOptionsButton from './components/ComReservationMoreOptionsButton.vue'
const moment = inject('$moment');

const loading = ref(false)
const route = useRoute()

const rs = inject("$reservation")
const gv = inject("$gv")
 
const confirm = useConfirm()
const toast = useToast()
const socket = inject("$socket")
const dialogRef = inject("dialogRef");
const setting = localStorage.getItem("edoor_setting")
const property = JSON.parse(localStorage.getItem("edoor_property"))

const name = ref("")
const dialog = useDialog()
const working_day = JSON.parse(localStorage.getItem("edoor_working_day"))

 
const isPage = computed(() => {
    return route.name == 'ReservationDetail'
})
const canCheckIn = computed(() => {
    let can_check_in =  rs.reservationStays.map((x)=>x.reservation_status).includes("Reserved")
    can_check_in = can_check_in &&  rs.reservationStays.filter((r)=>r.reservation_status=='Reserved' && moment(r.arrival_date).toDate() >= moment(working_day.date_working_day).toDate())
    return can_check_in;
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
function onMaximize(){
    dialogRef.value.maximize()
}

onMounted(() => {
 
    socket.on("RefreshReservationDetail", (reservation) => {
        console.log(reservation)
        if (reservation == name.value) {
            //we run this in settime out 
            //because we need to wait until data from backend that run enqueue process is update ted
            setTimeout(function(){
                onRefresh(false)
            },1500)
            
            

        }
    })


    if (!dialogRef) {
        if (route.params.name) {
            name.value = route.params.name
            onRefresh()
        }
    } else {
        name.value = dialogRef.value.data.name;
        window.has_reservation_detail_opened = true
        onRefresh()

    }
});

onUnmounted(() => {
    rs.clear()
    socket.off("RefreshReservationDetail");
    if (dialogRef) {
        
        window.has_reservation_detail_opened = false
        

    }

})

function onCheckIn(){
    if (rs.selecteds.length==0){
        if(rs.reservationStays.length>1){
            toast.add({ severity: 'warn', summary: "Group Check In", detail:"Please select reservation stay to check in.", life: 3000 })
        return
        }else {
            rs.selecteds = rs.reservationStays
        }
       
    }
    const dialogRef = dialog.open(ComConfirmCheckIn, {
        data:{
            stays:rs.selecteds
        },
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
                    reservation_stays: rs.selecteds.map(d => d["name"])
                }).then((result) => {
                    rs.loading = false
                    rs.LoadReservation(rs.reservation.name);
                    socket.emit("RefresheDoorDashboard", property.name);
                })
                    .catch((err) => {
                        rs.loading = false
                    })
                }
        }
    })
}
function onAddRoomMore(){
    const dialogRef = dialog.open(ComReservationStayAddMore, {
        props: {
            header: 'Add More Stay Room',
            style: {
                width: '80vw',
            },
            maximizable: true,
            modal: true,
            closeOnEscape: false,
            position: 'top'
        },
        onClose: (options) => {
            const data = options.data;
           
            if (data) {
                setTimeout(() => {
                    
                    rs.LoadReservation(data.name,false)
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
</style>
