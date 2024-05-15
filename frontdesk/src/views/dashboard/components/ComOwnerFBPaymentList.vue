<template>
    <ComOwnerContentTitle label="F&B">    
    <div class="grid ">
  <div class="col-6 pt-6">
    <Skeleton v-if="loading" width="100%" height="20rem"></Skeleton> 
            <div id="chartChargefnbpayment" style="margin-bottom: -30px;"></div>
  </div>      
 <div class="card col-6">
    <Skeleton v-if="loading" width="100%" height="100%"></Skeleton>    
<div v-else class="surface-ground rounded-lg p-2 max-h-list-scroll">
    <table class="w-full border-bottom-1">
        <tr class="border-bottom-1">
            <th class="text-center ">Payment Type</th>
            <th class="text-center border-left-1">Amount</th>
        </tr>
        <tr v-for="(payment, index) in data?.datasets" :key="index">
            <td class="text-center"> 
                <div class="flex align-items-center ">
                <div class="h-1rem w-1rem border-circle inline-block me-2" :style="{ backgroundColor: payment.color }" ></div> {{ payment.name }}
                </div>
            </td>
            <td class="text-center border-left-1">  <CurrencyFormat :value="payment.values" /></td>
        </tr>
    </table>
</div>
    </div>
    </div>
   
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
const doc = getApi('fnb.get_fnb_payment', {
        property: JSON.parse(localStorage.getItem("edoor_property")).name,
        date: JSON.parse(localStorage.getItem("edoor_working_day")).date_working_day
    })
    .then((result) => {
        loading.value = false  
            data.value = result.message
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
            height:320,
            type: "pie",
            colors:data.value.datasets.map(r=>r.color)
           
        };

  new Chart("#chartChargefnbpayment", chartConfig);
  console.log(chartConfig);
}
    onMounted(() => {
    renderdata()
})       
</script>
<style scoped>
::v-deep .chart-legend,
::v-deep .chart-container text {
    display: none !important;
}
</style>