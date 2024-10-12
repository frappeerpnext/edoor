<template>
<ComChart v-if="chartData" height="300px" :chartData="chartData" />

</template>
<script setup>
import { onMounted,ref } from "@/plugin"
const chartData = ref()
const props = defineProps({param: Object})
import { Chart } from "frappe-charts/dist/frappe-charts.min.esm"
import ComChart from "@/components/chart/ComChart.vue"
function renderChart() {
    
    chartData.value = {
        legend:{
            show:false
        },
        labels:  props.param.map(r=>r.room_type_alias),
        datasets: [
            {
                name: "Room Type",
                type:"bar",
                data: props.param.map(r=>r.total),
                
            }
        ]
    };


}
onMounted(() => {
    renderChart()
})

</script>