<template>
    <div class="">
        <div class="card flex justify-content-center">
            <Chart type="doughnut" :data="chartData" :options="chartOptions" class="w-full" />
        </div>
    </div>
</template>
<script setup>

import { ref, onMounted, inject } from "@/plugin";
import Chart from 'primevue/chart';
onMounted(() => {
    chartData.value = setChartData();
});
const chartData = ref();
const chartOptions = ref({
    cutout: '60%',
});
const props = defineProps({
    data: Object
})
const frappe = inject("$frappe")
const call = frappe.call()
const data = ref([])
const working_day = JSON.parse(localStorage.getItem("edoor_working_day"))

const setChartData = () => {
    const documentStyle = getComputedStyle(document.body);
    // console.log(data);
    return {
        labels: ['Occupy', 'Vacant'],
        datasets: [
            {
                data: [25, 10],
                backgroundColor: [documentStyle.getPropertyValue('--bg-btn-green-color'), documentStyle.getPropertyValue('--bg-warning-color'), documentStyle.getPropertyValue('--green-500')],
                hoverBackgroundColor: [documentStyle.getPropertyValue('--bg-btn-green-hover'), documentStyle.getPropertyValue('--bg-warning-hover'), documentStyle.getPropertyValue('--green-400')]
            }
        ],
    };
};

call.get('edoor.api.frontdesk.get_dashboard_data', {
    property: JSON.parse(localStorage.getItem("edoor_property")).name,
    date: working_day.date_working_day
}).then((result) => {
    data.value = result.message
})
</script>
