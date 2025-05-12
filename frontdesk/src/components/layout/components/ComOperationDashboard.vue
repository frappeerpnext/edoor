<template>
<div class="flex justify-content-between py-2 bg-white border-round-xl px-2 mt-2" style="position: sticky;top:62px;z-index: 1;">
    <div class="flex gap-3 align-items-center">
        <div @click="onRefresh()" class="text-xl md:text-2xl white-space-nowrap">{{$t(op.page_title)}}</div> 
        <div class="header-title text-xl md:text-2xl white-space-nowrap">
            - {{ moment(op.display_date).format("DD-MMM-YYYY") }}
        </div>
    </div>

    <div class="flex gap-2">
        <div class="flex">  
            <Button  @click="onChangeDate(-1)" icon="pi pi-angle-double-left" v-tippy="$t('View Previous Day')" class="border-noround-right border-y-none border-left-none"></Button>
            <Button @click="onChangeDate(0)"  v-tippy ="$t('View Today')"  class="border-noround border-none"><img class="icon-set-svg" :src="iconTodayCalendar"/></Button>
            <Button @click="onChangeDate(1)"  v-tippy ="$t('View Next Day')" class="border-noround-left border-y-none border-right-none" icon="pi pi-angle-double-right"></Button>
        </div>
        <NewFITReservationButton/>
        <NewGITReservationButton/>
        <Button @click ="onRefresh" icon="pi pi-refresh" class="content_btn_b adjBtnRefresh"></Button>
    </div>

</div>

<div class="mt-2" style="max-width: 100%;">
    <div id="fron__desk-fixed-top">
        <div :class="!isMobile ? 'flex gap-2' : ''">
            <div v-if="!isMobile" class="relative" style="width:280px">
                <div style="position: sticky;top:119px">
                    <div class="w-full">
                        <ComPanel title="Today Guest" class="mb-3 pb-3">
                            <div>
                                <ComTodaySummary/>
                            </div>
                        </ComPanel>
                    </div>
                </div>
            </div>
            <div class="relative chart-show-summary bg-white border-round-xl p-3" aria-haspopup="true" aria-controls="overlay_menu">
                <div>
                 
                       
                    <div class="flex gap-2">
                        <!-- nav kpi -->
                   
                        <ComOperationDashboardButton title="All Reservation" routeName="AllReservation" :currentRoute="op.current_route" :dataLength="data?.total_room_occupy" @onOpenRoute="openRoute('AllReservation')" icon="iconAllReservation"/>
                        <ComOperationDashboardButton title="Arrival Guest" routeName="ArrivalGuest" :currentRoute="op.current_route" :dataLength="data?.arrival - data?.arrival_remaining + '/' + data?.arrival" @onOpenRoute="openRoute('ArrivalGuest')" icon="iconArrivalGuest"/>
                        <ComOperationDashboardButton title="Stay Over" routeName="StayOverGuest" :currentRoute="op.current_route" :dataLength="data?.stay_over" @onOpenRoute="openRoute('StayOverGuest')" icon="iconStayOverGuest"/>
                        <!-- <ComOperationDashboardButton title="In-House" routeName="InHouse" :currentRoute="op.current_route" :dataLength="data?.in_house" @onOpenRoute="openRoute('InHouse')" icon="iconInHouse"/> -->
                        <ComOperationDashboardButton title="Departure" routeName="DepartureGuest" :currentRoute="op.current_route" :dataLength="data?.departure" @onOpenRoute="openRoute('DepartureGuest')" icon="iconDepartureGuest"/>
                        <ComOperationDashboardButton title="Daily Reservation" routeName="DailyReservation" :currentRoute="op.current_route" :dataLength="data?.daily_reservation + '/' + data?.daily_reservation_stay" @onOpenRoute="openRoute('DailyReservation')" icon="iconReservation"/>
                        <ComOperationDashboardButton title="Guest Folio" routeName="OperationDashboardGuestLedger" :currentRoute="op.current_route" :dataLength="2" @onOpenRoute="openRoute('OperationDashboardGuestLedger')" icon="iconGuestFolio"/>
                        
                        
                    </div>
                    <div class="mt-5">
                        <slot/>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div> 
</template>
<script setup >
import { ref, inject, useRouter, useRoute, computed,onMounted,getApi } from '@/plugin'
import ComTodaySummary from '@/views/frontdesk/components/ComTodaySummary.vue'; 
import NewFITReservationButton from "@/views/reservation/components/NewFITReservationButton.vue"
import NewGITReservationButton from "@/views/reservation/components/NewGITReservationButton.vue"
import ComOperationDashboardButton from "@/components/layout/components/ComOperationDashboardButton.vue"
import iconTodayCalendar from '@/assets/svg/calendar-today-icon.svg'
import iconArrivalToday from '@/assets/svg/icon-arrival-today.svg'
 
const router = useRouter()
const route = useRoute()
const op = inject("$operation_dashboard")

const working_day = window.working_day
op.current_date = working_day.date_working_day
op.current_route = route.name



op.display_date = working_day.date_working_day
const data = ref([])

const moment = inject("$moment")
function openRoute(name){
   
    router.push({name: name})
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

function onChangeDate(n){
    if (n==0){
        op.display_date =  moment(working_day.date_working_day ).add(n, "days").toDate();
    }else {
        op.display_date =  moment(op.display_date ).add(n, "days").toDate();
    }
    
    updateCurrentDate( op.display_date )
}


const updateCurrentDate = debouncer((date) => {
    op.current_date =   date
    loadData()
}, 700);

const onRefresh = debouncer((date) => {
    
    op.refresh_token = (Math.random() * 16)
    loadData()

}, 500);

function loadData(){
    getApi("operation_dashboard.get_summary",{
        property:window.property_name,
        date:moment(op.current_date).format("YYYY-MM-DD") 
    }).then(result=>{
        data.value = result.message
    })

}
onMounted(()=>{
    loadData()
})

 
 
</script>
<style scoped>
.chart-show-summary {
    width: calc(100% - 250px);
}
.icon-set-svg {
    height: 16px;
}
 
</style>