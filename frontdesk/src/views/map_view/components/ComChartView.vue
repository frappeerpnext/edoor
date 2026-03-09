<template>

 
  
  <div v-if="showChart" class="card" style="background:#fff; margin-bottom: 20px; border-radius: 10px; padding:10px; ">
    <ComChart v-if="chartData" :chartData="chartData" /> 
</div>
  
 

</template>
<script setup>
import {onMounted,ref,watch} from "@/plugin"
import ComChart from "@/components/chart/ComChart.vue"

const props =defineProps({
    chart:Object
})

const showChart = ref(true)
const chartData = ref({})

watch(() => props.chart, () => {
    renderChart()
})
function renderChart(){
    if (props.chart.data?.labels?.length>100){
        showChart.value = false
    }else {
        showChart.value = true
      
        chartData.value.labels = props.chart.data?.labels
       
        chartData.value.datasets  = props.chart.data.datasets.map(r=>{
           
            return {
                type:"bar",
                label: {
                    show: true,
                    position: 'top'
                },
                name:r.name,
                data: r.values
            }
        })
        
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