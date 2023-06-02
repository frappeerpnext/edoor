<template >
    <div id="xx">
      <ComChartDoughnut :data="data"/>
    
    </div>
</template>
<script setup>
import { ref, onMounted,watch } from "vue";
import ComChartDoughnut from '../components/chart/ComChartDoughnut.vue';
const data = [{label: 'a', value: 5, color: 'red'},{label: 'b', value: 12, color: 'green'}]
const chartData = ref();
const chartOptions = ref({
    cutout: '70%',
});
const documentStyle = getComputedStyle(document.body);
    chartData.value = {
    datasets: [
        {
            data: [21, 12],
            backgroundColor: [documentStyle.getPropertyValue('--bg-btn-green-color'), documentStyle.getPropertyValue('--bg-warning-color'), documentStyle.getPropertyValue('--green-500')],
            hoverBackgroundColor: [documentStyle.getPropertyValue('--bg-btn-green-hover'), documentStyle.getPropertyValue('--bg-warning-hover'), documentStyle.getPropertyValue('--green-400')]
        }
    ],
}

</script> 
<style>
 
</style>