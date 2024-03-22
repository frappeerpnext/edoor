<template>
    <div>
        <ComChartDoughnut v-if="!loading" :percentage="data?.occupancy" :data="chartData"  show-percentage="Occupied" class="doughnut__chart_ds"/>
        <Skeleton v-else shape="circle" size="18rem"></Skeleton>
    </div>
    <div class="td_guest_cs px-1 mt-3 cursor-pointer">
        <ComTodaySummarySep dialogKey="all_rooms"  title="All Rooms">{{ data?.total_room }}</ComTodaySummarySep>
        <tippy :content="((data?.arrival || 0) - (data?.arrival_remaining || 0)) + ' ' + $t('Checked-in') + ' ' + ' & ' +  $t('Total Arrival') + (data?.arrival|| 0)  ">
        <ComTodaySummarySep dialogKey="arrival" title="Arrival" :totalValue="data.arrival" :value="((data.arrival || 0) -(data.arrival_remaining || 0))">
            <span>{{ (data?.arrival || 0) -(data?.arrival_remaining || 0) }}</span> / <span>{{ (data?.arrival || 0) }}</span>
        </ComTodaySummarySep>
        </tippy>
        <tippy :content="((data?.departure ||0) - (data?.departure_remaining ||0)) + ' ' + $t('Checked-out') + ' & '+ $t('Total Departure') + ' ' +  (data?.departure ||0)   ">
        <ComTodaySummarySep dialogKey="departure" title="Departure" :totalValue="data.departure" :value="data.departure - data?.departure_remaining">
        <span title="Departure">{{ (data?.departure ||0) - (data?.departure_remaining ||0) }}</span> / <span titel="Departure Remain">{{ data?.departure || 0 }}</span>
        </ComTodaySummarySep>
        </tippy>
        <ComTodaySummarySep dialogKey="stay_over" title="Stay Over">{{ data?.stay_over }}</ComTodaySummarySep>
        <ComTodaySummarySep dialogKey="in_house" title="In-house">{{ data?.in_house }}</ComTodaySummarySep>
    <tippy :content="`${$t('Today you have')} ${data?.unassign_room} ${$t('unassign room reservation')} & ${$t('total all unassign room')} is ${data?.total_unassign_room}`">
        <ComTodaySummarySep dialogKey="unassign_room"  title="Unassign Room (Today/All)">{{ data?.unassign_room }} / {{ data?.total_unassign_room || 0 }}</ComTodaySummarySep>
    </tippy>
        <tippy :content="$t('FIT (Free Independent Traveler) Total') + ' ' + data.fit_reservation_arrival + ' & ' + $t('Total Stay') + data.fit_stay_arrival">
            <ComTodaySummarySep   dialogKey="fit_arrival" title="FIT Arrival">{{(data.fit_reservation_arrival + ' / ' + data.fit_stay_arrival)}}</ComTodaySummarySep>
        </tippy>
        <tippy :content="$t('GIT (Group Inclusive Tour) Total') + ' ' +  data?.git_reservation_arrival +  ' & ' + $t('Total Stay') + ' ' + data?.git_stay_arrival">
            <ComTodaySummarySep   dialogKey="git_arrival" title="GIT Arrival">{{ (data?.git_reservation_arrival ||0) + ' / ' +  (data?.git_stay_arrival ||0) }}</ComTodaySummarySep>
        </tippy>
        <ComTodaySummarySep  dialogKey="pickup_drop_off" title="Pickup/Drop Off">{{ data?.pick_up || 0 }} / {{data?.drop_off || 0}}</ComTodaySummarySep>
        <ComTodaySummarySep v-tippy="$t('Today No-Show') + ' ' + data.today_no_show + ' & '  + $t('No-Show With Reserved Room') + ' '  + data.total_no_show"  dialogKey="no_show" title="No-Show"> {{ data?.today_no_show }} / {{data?.total_no_show || 0}}</ComTodaySummarySep>
        <ComTodaySummarySep v-tippy="$t('Today Cancelled') + ' ' + data.today_cancelled + ' & ' +$t('Cancelled') + ' '  + data.total_cancelled " dialogKey="cancelled" title="Cancelled"> {{ data?.today_cancelled }} / {{data?.total_cancelled || 0}}</ComTodaySummarySep>
        <ComTodaySummarySep v-tippy="$t('Today Void') + ' ' + data.today_void + ' & ' + $t('Void') + data.total_void" dialogKey="void" title="Void"> {{ data?.today_void }} / {{data?.total_void || 0}}</ComTodaySummarySep>
        
    </div>
</template>
<script setup>
import { ref, getApi, inject,onMounted,onUnmounted } from "@/plugin"
import ComTodaySummarySep from '@/views/frontdesk/components/ComTodaySummarySep.vue';
import {i18n} from '@/i18n';
const { t: $t } = i18n.global;
const property = JSON.parse(localStorage.getItem("edoor_property"))
const props = defineProps({date:""})
const gv = inject("$gv")
const moment = inject("$moment")
const data = ref([]) 
const working_day = JSON.parse(localStorage.getItem("edoor_working_day"))
const chartData = ref([])
const loading = ref(false)

onMounted(() => {
    window.addEventListener('message', actionRefreshData, false);
    loadData(props.date)
})

const actionRefreshData = async function (e) {
    if (e.isTrusted && typeof (e.data) != 'string') {
        if(e.data.action=="TodaySummary"){
            setTimeout(()=>{
                loadData(props.date,false)
            },1000*2)
            
        }
    };
}

function loadData(date,show_loading = true){
    loading.value = show_loading
    chartData.value = []
    let currentDate = working_day?.date_working_day
    
    if(date){
        if (!isNaN(Date.parse(moment(date)))){
            currentDate = gv.dateApiFormat(date)
        }
        
    }
    getApi('frontdesk.get_dashboard_data', {
        property: property.name,
        date: currentDate
    }).then((result) => {
        data.value = result.message
        const documentStyle = getComputedStyle(document.body);
        chartData.value.push({label: 'Occupied', value: data.value.total_room_occupy, color: documentStyle.getPropertyValue('--bg-btn-green-color')})
        chartData.value.push({label: 'Vacant', value: data.value.total_room_vacant, color: documentStyle.getPropertyValue('--bg-warning-color')})
        loading.value = false
    }).catch(()=>{
        loading.value = false
    })
}
onUnmounted(() => {
    window.removeEventListener('message', actionRefreshData, false);
})

</script>