<template>
     <div v-if="showChart" class="card" style="background:#fff; margin-bottom: 20px; border-radius: 10px; padding:10px; ">
 
        <div :id="chart_id"></div>
</div>
</template>
<script setup>
import {onMounted,ref,watch} from "@/plugin"
import { Chart } from "frappe-charts/dist/frappe-charts.min.esm"

const props =defineProps({
    chart:Object
})
const chart_id = ref("chart_" + generateRandomString(10))
const showChart = ref(true)

watch(() => props.chart, () => {
    renderChart()
})

function renderChart(){
    if (props.chart.data?.labels?.length>100){
        showChart.value = false
    }else {
        showChart.value = true
        const chart = new Chart("#" + chart_id.value,  props.chart)
    }
    
}



onMounted(()=>{
 
renderChart()


})

function generateRandomString(length) {
  const characters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
  let result = '';
  const charactersLength = characters.length;
  
  for (let i = 0; i < length; i++) {
    result += characters.charAt(Math.floor(Math.random() * charactersLength));
  }
  
  return result;
}

 

</script>