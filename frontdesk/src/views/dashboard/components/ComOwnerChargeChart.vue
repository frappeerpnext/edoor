<template>
    <ComOwnerContentTitle label="Charge"> 
        
        <ComPlaceholder text="No Data"  :is-not-empty="data" >   
        <div class="col-12">
            <Skeleton v-if="loading" width="100%" height="20rem"></Skeleton> 
            <div id="chartCharge"></div>
        </div>
<div class="col-12 h-full">
    <Skeleton v-if="loading" width="100%" height="20rem"></Skeleton>     
<div v-else class="surface-ground rounded-lg p-2" style="min-height:20rem;max-height:20rem;">
    <table class="w-full border-bottom-1">
  <tr class="border-bottom-1">
    <th class="text-center ">Charge List</th>
    <th class="text-center border-left-1">Amount</th>
  </tr>
  <tr v-for="(payment, index) in data?.datasets" :key="index">
      <td class="text-center"> 
        <div class="flex align-items-center ">
 {{ payment.name }}
        </div>
     </td>
      <td class="text-center border-left-1">  <CurrencyFormat :value="payment.values" /></td>
 </tr>
</table>
</div>
</div>  
</ComPlaceholder>
</ComOwnerContentTitle>    

</template>
<script setup>
import {  ref, onMounted,getApi } from '@/plugin'
import { Chart } from "frappe-charts/dist/frappe-charts.min.esm"
import ComOwnerContentTitle from '@/views/dashboard/components/ComOwnerContentTitle.vue'
import { Colors } from 'chart.js';
const loading = ref(true)
 
 
const data = ref({})
function renderdata() {
loading.value = true    
const doc = getApi('frontdesk.get_charge_chart_data', {
        property: JSON.parse(localStorage.getItem("edoor_property")).name,
        date: JSON.parse(localStorage.getItem("edoor_working_day")).date_working_day
    })
    .then((result) => {
            data.value = result.message
            loading.value = false
            renderChart()
           
        })
    }
    function renderChart() {
        const chartConfig = {
            data: {
            labels:data.value.labels,
            datasets:[{
                values:data.value.datasets.map(r=>r.values),
     
            }
        ]
            },
            type: "bar",
           
        };

  new Chart("#chartCharge", chartConfig);
  console.log(chartConfig);
}
onMounted(() => {
    renderdata()
})       
</script>