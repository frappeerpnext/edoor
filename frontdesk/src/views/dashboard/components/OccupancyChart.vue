 
<template>
    <div class="flex justify-content-end mr-5">
        <SplitButton :model="items" @click="save" class="p-component spl__btn_cs sp mb-0 mt-2 mr-2" :label="$t(view_chart_by)"></SplitButton>
        <SplitButton :model="duration_types" :label="$t(duration_type)"   class="p-component spl__btn_cs sp mb-0 mt-2"></SplitButton>
    
    </div>
    <div class="card">
        <div id="occupancy_chart"></div>
    </div>
</template>

<script setup>

import { ref, onMounted ,getApi,computed} from "@/plugin";
 
import { Chart } from "frappe-charts/dist/frappe-charts.min.esm"
import {i18n} from '@/i18n';
const { t: $t } = i18n.global; 
const duration_type = ref("Daily")
const view_chart_by = ref("Time Series")
const show_occupancy_only = ref(0)
const view_chart_type = ref("line")

const chartData = ref();
const loading = ref(false)

const items = [
    {
        label: $t('Time Series'),
        icon: 'pi pi-clock',
        command: () => {
            view_chart_by.value =("Time Series")
            getChartData()
        }
    },
    {
        label: $t('Business Source'),
        icon: 'pi pi-briefcase',
        command: () => {
            view_chart_by.value = "Business Source"
            getChartData()
        }
    },
    {
        label: $t('Room Type'),
        icon: 'pi pi-building',
        command: () => {
            view_chart_by.value = "Room Type"
            getChartData()
        }
    },
   
];

const duration_types = [
    {
        label: $t('Daily'),
        command: () => {
            duration_type.value = ("Daily")
            getChartData()
        }
    },
    {
        label: $t('Monthly'),
        command: () => {
            duration_type.value = ("Monthly")
            getChartData()
        }
    }

]

function onViewChartTypeChange(){
    getChartData()
}

function onShowOccupancyOnly(v){
   if(show_occupancy_only.value==0){
    view_chart_type.value = "line"
   }

    getChartData()
}

function getChartData(){
   loading.value  = true

    getApi("frontdesk.get_mtd_room_occupany",
        {
            property: window.property_name,
            view_chart_by: view_chart_by.value,
            duration_type:duration_type.value,
            show_occupancy_only:show_occupancy_only.value,
            view_chart_type:view_chart_type.value
        }
    ).then((result)=>{
         
        chartData.value = result.message;
        renderChart()
        loading.value  = false
    }).catch(err=>{
        loading.value  = false
    })
}

onMounted(() => {
    getChartData()
    
});
 


function renderChart(){
 
    const chartConfig = {
  data: chartData.value,
  height: 350,
  colors: [
        window.setting.room_block_color,getStatusColor("No Show"), getStatusColor("Checked Out"), getStatusColor("In-house"),getStatusColor("Reserved"),"light-blue"],
  axisOptions: {
    xAxisMode: "tick",
    xIsSeries: true
  },
  barOptions: {
    stacked: true,
    spaceRatio: 0.3
  },
}
const chart = new Chart("#occupancy_chart",chartConfig)

 
}
 
function getStatusColor(status){
    return window.setting.reservation_status.find(r=>r.name==status).color
}

</script>
