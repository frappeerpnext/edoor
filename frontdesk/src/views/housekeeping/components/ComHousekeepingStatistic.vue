<template>
       <div>
              <ComPanel title="Today Statistic" class=" pb-3">
                <!-- <ComDonutFrontdesk/>  -->
                <ComChartDoughnut :total_room="data?.total_room" :data="chartData" :showPercentageInteger="true" v-if="chartData.length > 0" show-percentage="Occupied" class="doughnut__chart_ds"/>
                <ComHousekeepingTodaySummary :isHousekeeping="true"/>   
              </ComPanel>
              <ComPanel title="Housekeeping Statistic" class="mt-3 pb-3">
                 <ComHousekeepingStatus />       
              </ComPanel>
                  
       </div>
</template>
<script setup>
import { ref, getApi,watch, inject,onMounted } from "@/plugin"
import ComHousekeepingStatus from '@/views/dashboard/components/ComHousekeepingStatus.vue';
import ComRoomStatusDoughnut from '@/views/dashboard/components/ComRoomStatusDoughnut.vue';
import ComDonutFrontdesk from '../../frontdesk/components/ComDonutFrontdesk.vue';
import ComHousekeepingTodaySummary from './ComHousekeepingTodaySummary.vue';
const data = ref({})
const chartData = ref([]) 
const props = defineProps({
    date: ""
})
const gv = inject("$gv")
const moment = inject("$moment")
const working_day = JSON.parse(localStorage.getItem("edoor_working_day"))
watch(()=> [props.date], ([newValue])=>{
    loadData(newValue)
})
onMounted(() => {
    loadData(props.date)
})
function loadData(date){ 
    chartData.value = []
    const currentDate = ref(working_day?.date_working_day)
    if(date){
        currentDate.value = gv.dateApiFormat(date)
    }
    getApi('frontdesk.get_dashboard_data', {
        property: JSON.parse(localStorage.getItem("edoor_property")).name,
        date: currentDate.value
    }).then((result) => {
        data.value = result.message
        const documentStyle = getComputedStyle(document.body);
        chartData.value.push({label: 'Occupied', value: data.value.total_room_occupy, color: documentStyle.getPropertyValue('--bg-btn-green-color')})
        chartData.value.push({label: 'Vacant', value: data.value.total_room_vacant, color: documentStyle.getPropertyValue('--bg-warning-color')})
    })
}
</script>