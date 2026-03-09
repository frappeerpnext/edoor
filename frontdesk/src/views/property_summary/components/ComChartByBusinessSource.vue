<template>
<ComChart v-if="chartData" height="300px" :chartData="chartData" />

</template>
<script setup>
import { onMounted,ref } from "@/plugin"
import { Chart } from "frappe-charts/dist/frappe-charts.min.esm"
import ComChart from "@/components/chart/ComChart.vue"
const props = defineProps({param: Object})
const chartData = ref()

function renderChart() {
    
    chartData.value = {
        legend:{
            show:false
        },
        labels:  props.param.map(r=>r.business_source),
        datasets: [
            {
                name: "Business Source",
                type:'bar',
                data: props.param.map(r=>r.total),
                
            }
        ],
        
    };
 

}
onMounted(() => {
    renderChart()
})

</script>