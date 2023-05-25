<template>   
    <div class="main_doughnut">
        <div class="doughnut_percent text-color-chart">
        {{ ((value_room_vacant/value_doughnut)*100)  }}%
        </div>
        <div class="card flex justify-content-center">
            <Chart type="doughnut" :data="chartData" :options="chartOptions" class="w-full w-17rem" />
        </div>
    </div>
</template>
<script setup>
 const props = defineProps({
    value_doughnut: Number,
    value_total_room: Number,
    value_room_vacant: Number,
    value: [String,Number]
 })
import { ref, onMounted } from "vue";
import Chart from 'primevue/chart';
onMounted(() => {
    chartData.value = setChartData();
});
const chartData = ref();
const chartOptions = ref({
    cutout: '70%',
});
const setChartData = () => {
    const documentStyle = getComputedStyle(document.body);
    return {
        datasets: [
            {  
                data: [ 25 , 10 ],
                backgroundColor: [documentStyle.getPropertyValue('--bg-btn-green-color'), documentStyle.getPropertyValue('--bg-warning-color'), documentStyle.getPropertyValue('--green-500')],
                hoverBackgroundColor: [documentStyle.getPropertyValue('--bg-btn-green-hover'), documentStyle.getPropertyValue('--bg-warning-hover'), documentStyle.getPropertyValue('--green-400')]
            }
        ], 
    };
};
</script>
<style scoped>
    .main_doughnut{
       position: relative; 
    }
    .doughnut_percent{
        white-space: nowrap;
        position: absolute;
        left: 50%;
        top: 52%;
        font-size: 40px;
        transform: translate(-50%,-50%);
    }
</style>
