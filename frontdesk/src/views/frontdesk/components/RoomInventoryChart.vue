
<template>
    <div class="card" style="background:#fff; margin-bottom: 20px; border-radius: 10px; padding:10px; ">
 
        <div id="room_inventory_occupancy_chart"></div>
    
    </div>
</template>

<script setup>
import {  inject,watch } from "vue";
import { Chart } from "frappe-charts/dist/frappe-charts.min.esm"
const props = defineProps({ data: Object })
const moment = inject("$moment")

watch(() => props.data, (newValue, oldValue) => {
    renderChart();
})


function renderChart(){
 
    const chartData = {
        labels: [...new Set(props.data.map(r=>moment(r.start).format("DD/MMM")))],
        datasets: [
            {
                chartType: 'bar',
                name: 'Departure',
                values:  props.data.filter(r=>r.departure>=0).map(r=>parseFloat( r.departure))
            },
                {
                    chartType: 'bar',
                    name: 'Stay Over',
                   
                    values:   props.data.filter(r=>r.stay_over>=0) .map(r=>parseFloat( r.stay_over))
                },
            {
                chartType: 'bar',
                name: 'Arrival',
                values:   props.data.filter(r=>r.arrival>=0) .map(r=>parseFloat( r.arrival)),
                
            },
            {
                chartType: 'line',
                name: 'Occupancy',
                values: props.data.filter(r=>r.occupancy) .map(r=>parseFloat( r.occupancy)),
            },
           
        ]
    }

    const chartConfig = {
        data: chartData,
        height: 350,
        colors: [
            getStatusColor("Checked Out"), getStatusColor("In-house"), getStatusColor("Reserved"), "light-blue"],
        axisOptions: {
            xAxisMode: "tick",
            xIsSeries: true
        },
        barOptions: {
            stacked: true,
            spaceRatio: 0.3
        },
        valuesOverPoints: 1
    }
    const chart = new Chart("#room_inventory_occupancy_chart",chartConfig)


    }

    function getStatusColor(status){
    return window.setting.reservation_status.find(r=>r.name==status).color
    }


</script>
