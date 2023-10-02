 
<template>
    <div class="card">
        <Chart type="bar" :data="chartData" :options="chartOptions" class="h-30rem" />
    </div>
</template>

<script setup>

import { ref, onMounted, inject } from "vue";
import Chart from 'primevue/chart';

const frappe = inject("$frappe")
const call = frappe.call()
const moment = inject("$moment")
const property = JSON.parse(localStorage.getItem("edoor_property"))

onMounted(() => {
    call.get("edoor.api.frontdesk.get_mtd_room_occupany",
        {
            property: property.name
        }
    ).then((result)=>{
            chartData.value = setChartData(result.message);
        chartOptions.value = setChartOptions();
    })
});

const chartData = ref();
const chartOptions = ref();

const setChartData = (data) => {
    const documentStyle = getComputedStyle(document.documentElement);
    return {
        labels: data.map(r => moment(r.date).format("DD")),
        datasets: [
            {
                label: 'Occupancy',
                backgroundColor: documentStyle.getPropertyValue('--blue-500'),
                data:  data.map(r => r.occupancy), 
            }
        ]
    };
};

const setChartOptions = () => {
    const documentStyle = getComputedStyle(document.documentElement);
    const textColor = documentStyle.getPropertyValue('--text-color');
    const textColorSecondary = documentStyle.getPropertyValue('--text-color-secondary');
    const surfaceBorder = documentStyle.getPropertyValue('--surface-border');
    return {
        maintainAspectRatio: false,
        aspectRatio: 0.8,
        plugins: {
            legend: {
                labels: {
                    fontColor: textColor,  
                }
            }
        },
        scales: {
            x: {
                ticks: {
                    color: textColorSecondary,
                    font: {
                        weight: 500
                    }
                },
                grid: {
                    display: false,
                    drawBorder: false
                }
            },
            y: {
                ticks: {
                    color: textColorSecondary, 
                },
                grid: {
                    color: surfaceBorder,
                    drawBorder: false
                }
            }
        }
    };
}
</script>
