<template>
    <ComOwnerContentTitle label="Payment">       
        <ComPlaceholder text="No Data" :loading="loading" :is-not-empty="data?.datasets.length > 0">  
        <div class="grid">
        <div class="col-6 pt-6">
            <div v-if="loading" class="flex w-full justify-content-center">
            <Skeleton  shape="circle" size="17rem" class="mr-2"></Skeleton>
            </div>
            <div id="chart" style="margin-bottom: -30px;"></div>
        </div>
<div class="col-6 h-auto">
<Skeleton v-if="loading" width="100%" height="100%"></Skeleton>    
<div v-else class="surface-ground rounded-lg p-2 max-h-list-scroll">
    <table class="w-full border-bottom-1 relative">
        <tr class="border-bottom-1 surface-ground" style="position: sticky;top: 0;">
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
        <tr>
            <th class="text-right border-1 pe-2">Total</th>
            <th class="border-1"><CurrencyFormat :value="totalValues" /></th>
        </tr>
    </table>
</div>
</div>  
</div>
</ComPlaceholder>
</ComOwnerContentTitle>    
</template>
<script setup>
import {  ref, onMounted,getApi,computed } from '@/plugin'
import { Chart } from "frappe-charts/dist/frappe-charts.min.esm"
import ComOwnerContentTitle from '@/views/dashboard/components/ComOwnerContentTitle.vue'
const loading = ref(true)
 
 
const data = ref({})
const totalValues = computed(() => {
  return data.value.datasets.reduce((sum, payment) => sum + payment.values, 0);
});
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
                name: "", 
                values:data.value.datasets.map(r=>r.values),
            }
        ]
            },
             height: 320,
            type: "pie",
            colors:data.value.datasets.map(r=>r.color),
            
        };

  new Chart("#chart", chartConfig);
  
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