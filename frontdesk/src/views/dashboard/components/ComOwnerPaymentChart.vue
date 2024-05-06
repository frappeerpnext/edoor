<template>
    <ComOwnerContentTitle label="Payment chart">         
        <div class="grid">
        <div class="col-6">
            <div v-if="loading" class="flex w-full justify-content-center">
            <Skeleton  shape="circle" size="17rem" class="mr-2"></Skeleton>
            </div>
            <div id="chart"></div>
        </div>
<div class="col-6 h-auto">
<Skeleton v-if="loading" width="100%" height="100%"></Skeleton>    
<div v-else class="surface-ground rounded-lg p-2 h-full">
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
    loading.value = true 
const doc = getApi('frontdesk.get_paymet_chart_data', {
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
            type: "pie",
            colors:data.value.datasets.map(r=>r.color)
        };

  new Chart("#chart", chartConfig);
  console.log(chartConfig);
}
onMounted(() => {
    renderdata()
})       
</script>