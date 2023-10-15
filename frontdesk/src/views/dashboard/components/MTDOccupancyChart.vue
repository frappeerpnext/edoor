 
<template>
    <SplitButton   :model="items"  @click="save" class="mb-2" :label="view_chart_by"></SplitButton>
    <SplitButton   :model="duration_types" :label="duration_type"   class="mb-2"></SplitButton>
    
    <label for="show_occupancy_only" class="font-medium cursor-pointer ">Show occupancy only</label>
                                <Checkbox 
                                :trueValue="1"
                                :falseValue="0"
                                    v-model="show_occupancy_only" :binary="true"
                                    inputId="show_occupancy_only"
                                    @change="onShowOccupancyOnly"
                                     />
    <Dropdown v-if="show_occupancy_only" @change="onViewChartTypeChange" v-model="view_chart_type" :options="['line','bar','pie','doughnut']"   class="w-full md:w-14rem"  />
  

 
 
    <div class="card">
        
        <Chart v-if="!loading" :type="view_chart_type"  :data="chartData" :options="chartOptions"  :plugins="plugins" class="h-30rem"  />
    </div>
</template>

<script setup>

import { ref, onMounted ,getApi,computed} from "@/plugin";
import Chart from 'primevue/chart';
import ChartDataLabels from 'chartjs-plugin-datalabels';


const plugins = [ChartDataLabels]
const duration_type = ref("Daily")
const view_chart_by = ref("Time Series")
const show_occupancy_only = ref(0)
const view_chart_type = ref("line")

const chartData = ref();
const chartOptions = ref();
const loading = ref(false)

 
const items = [
    {
        label: 'Time Series',
        icon: 'pi pi-clock',
        command: () => {
            view_chart_by.value =("Time Series")
            getChartData()
        }
    },
    {
        label: 'Business Source',
        icon: 'pi pi-briefcase',
        command: () => {
            view_chart_by.value = "Business Source"
            getChartData()
        }
    },
    {
        label: 'Room Type',
        icon: 'pi pi-building',
        command: () => {
            view_chart_by.value = "Room Type"
            getChartData()
        }
    },
   
];

const duration_types = [
    {
        label: 'Daily',
        command: () => {
            duration_type.value = ("Daily")
            getChartData()
        }
    },
    {
        label: 'Monthly',
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
        chartOptions.value = setChartOptions();
        loading.value  = false
    }).catch(err=>{
        loading.value  = false
    })
}

onMounted(() => {
    getChartData()
});

 


const setChartOptions = () => {
    const documentStyle = getComputedStyle(document.documentElement);
    const textColor = documentStyle.getPropertyValue('--text-color');
    const textColorSecondary = documentStyle.getPropertyValue('--text-color-secondary');
    return {
        maintainAspectRatio: false,
        aspectRatio: 0.6,
         plugins: {
            tooltips: {
                mode: 'index',
                intersect: true
            },
            legend: {
                labels: {
                    color: textColor
                }
            },
        },
        scales: {
            x: {
                stacked:true,
                ticks: {
                    color: textColorSecondary
                },
            },
            y: {
                stacked:true,
                ticks: {
                    color: textColorSecondary
                },
                
            }
        }
    };
}

</script>
