<template>
    <ComOwnerContentTitle label="F&B">    
       
    <div class="grid ">
  <div class="lg:col-6 col-12 pt-6 relative">
    <Skeleton v-if="loading" width="100%" height="20rem"></Skeleton> 
            <div id="chartChargefnb" style="margin-bottom: -30px;" ></div>
  </div>      
 <div class="card lg:col-6 col-12">
    <Skeleton v-if="loading" width="100%" height="100%"></Skeleton>    
<div v-else class="surface-ground rounded-lg p-2 max-h-list-scroll">
     <ComPlaceholder text="No Data" :loading="loading" :is-not-empty="data?.datasets?.length > 0">
    <table class="w-full border-bottom-1">
        <tr class="border-bottom-1">
            <th class="text-center ">Item</th>
            <th class="text-right border-left-1">Amount</th>
        </tr>
        <tr v-for="(payment, index) in data?.datasets" :key="index">
            <td class="text-center"> 
                <div class="flex align-items-center ">
                <div class="h-1rem w-1rem border-circle inline-block me-2" :style="{ backgroundColor: payment.color }" ></div> {{ payment.name }}
                </div>
            </td>
            <td class="text-right border-left-1">  <CurrencyFormat :value="payment.values" /></td>
        </tr>
        <tr>
            <th class="text-right border-1 pe-2">Total</th>
            <th class="border-1 text-right"><CurrencyFormat :value="totaldValues" /></th>
        </tr>
    </table>
</ComPlaceholder>
</div>
    </div>
    </div>

</ComOwnerContentTitle>    
</template>
<script setup>
import {  ref, onMounted,getApi,computed } from '@/plugin'
import { Chart } from "frappe-charts/dist/frappe-charts.min.esm"
import ComOwnerContentTitle from '@/views/dashboard/components/ComOwnerContentTitle.vue'
import { Colors } from 'chart.js';
const loading = ref(true)
 
const totaldValues = computed(() => {
  return data.value.datasets.reduce((sum, payment) => sum + payment.values, 0);
});  
const data = ref({})
function renderdata() {
const doc = getApi('fnb.get_fnb_revenue', {
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

  new Chart("#chartChargefnb", chartConfig);
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