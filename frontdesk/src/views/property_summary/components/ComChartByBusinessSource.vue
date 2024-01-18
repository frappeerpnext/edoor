<template>

    <div id="business_source_chart"></div>

</template>
<script setup>
import { onMounted } from "@/plugin"
import { Chart } from "frappe-charts/dist/frappe-charts.min.esm"

const props = defineProps({param: Object})


function renderChart() {
    
    const data = {
        labels:  props.param.map(r=>r.business_source),
        datasets: [
            {
                name: "Business Source",
                values: props.param.map(r=>r.total),
                
            }
        ],
        
    };


    const chartConfig = {
        data: data,
        type: "bar",
        height: 250,
        valuesOverPoints: 1

    }
    const chart = new Chart("#business_source_chart", chartConfig)

}
onMounted(() => {
    renderChart()
})

</script>