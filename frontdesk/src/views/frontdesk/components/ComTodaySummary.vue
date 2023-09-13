<template>
    <div>
        <ComChartDoughnut v-if="!loading" :total_room="data?.total_room" :data="chartData" :showPercentageInteger="true" show-percentage="Occupied" class="doughnut__chart_ds"/>
        <Skeleton v-else shape="circle" size="18rem"></Skeleton>
    </div>
    <div class="td_guest_cs px-1 mt-3 cursor-pointer">
        
        <ComTodaySummarySep dialogKey="all_rooms"  title="All Rooms">{{ data?.total_room }}</ComTodaySummarySep>
        <tippy :content="((data?.arrival || 0) - (data?.arrival_remaining || 0)) + ' Checked-in ' + ' and ' +  ' Total Arrival ' + (data?.arrival|| 0)  ">
        <ComTodaySummarySep dialogKey="arrival" title="Arrival" :totalValue="data.arrival" :value="((data.arrival || 0) -(data.arrival_remaining || 0))">
            <span>{{ (data?.arrival || 0) -(data?.arrival_remaining || 0) }}</span>/<span>{{ (data?.arrival || 0) }}</span>
        </ComTodaySummarySep>
        </tippy>
        <tippy :content="((data?.departure ||0) - (data?.departure_remaining ||0)) + ' Checked-out' + ' and '+ 'Total Departure ' +  (data?.departure ||0)   ">
        <ComTodaySummarySep dialogKey="departure" title="Departure" :totalValue="data.departure" :value="data.departure - data?.departure_remaining">
        <span title="Departure">{{ (data?.departure ||0) - (data?.departure_remaining ||0) }}</span>/<span titel="Departure Remain">{{ data?.departure || 0 }}</span>
        </ComTodaySummarySep>
        </tippy>
        <ComTodaySummarySep dialogKey="stay_over" title="Stay Over">{{ data?.stay_over }}</ComTodaySummarySep>
        <ComTodaySummarySep dialogKey="unassign_room" title="Unassign Room">{{ data?.unassign_room }}</ComTodaySummarySep>
        <tippy :content="'Group Arrival '+  data?.git_reservation_arrival + ' Group(s) and ' + data?.git_stay_arrival + ' Stay(s)'">
            <ComTodaySummarySep   dialogKey="git_arrival" title="GIT Arrival">{{ (data?.git_reservation_arrival ||0) + '/' +  (data?.git_stay_arrival ||0) }}</ComTodaySummarySep>
        </tippy>
        <ComTodaySummarySep  dialogKey="pickup_drop_off" title="Pickup/Drop Off">{{ data?.pick_up || 0 }} / {{data?.drop_off || 0}}</ComTodaySummarySep>
        <ComTodaySummarySep  dialogKey="no_show" title="No Show">{{data?.total_no_show || 0}}</ComTodaySummarySep>
        <ComTodaySummarySep  dialogKey="cancelled" title="Cancelled">{{data?.total_cancelled || 0}}</ComTodaySummarySep>
        
    </div>
</template>
<script setup>
import { ref, getApi, inject,onMounted,onUnmounted } from "@/plugin"
import ComTodaySummarySep from '@/views/frontdesk/components/ComTodaySummarySep.vue';
const property = JSON.parse(localStorage.getItem("edoor_property"))
const socket = inject("$socket")
const props = defineProps({
    date: ""
})
const gv = inject("$gv")
const moment = inject("$moment")
const data = ref([]) 
const working_day = JSON.parse(localStorage.getItem("edoor_working_day"))
const chartData = ref([])
const loading = ref(false)


socket.on("RefreshData", (arg) => {
    if (arg.property == property.name && arg.action=="refresh_summary") {
        loadData(props.date,false)
    }
})

onMounted(() => {
    loadData(props.date)
})

onUnmounted(() => {
    
    socket.off("RefreshData");
})

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
</script>