<template>
    <ComOwnerContentTitle label="Business Source">    
        <div class="col-12">
            <Skeleton v-if="loading" class="mb-2"  width="100%" height="20rem"></Skeleton>
            <div id="chartbs"></div>
        </div>
<div class="col-12 h-full">
    <div class="grid ">
        <div class="lg:col-6 col-12">
            {{ data }}
            <Skeleton v-if="loading"  class="mb-2"  width="100%" height="20rem"></Skeleton>
            <div v-else class="surface-ground rounded-lg p-2 h-full">
                <table class="w-full border-bottom-1">
                <tr >
                    <th colspan="2" class="text-start">  
<spna class="border-b-2" style="border-color:#7cd6fd;">Actual</spna>
                    </th>
                </tr>
                <tr class="border-bottom-1">
                    <th class="text-start ">Charge List</th>
                    <th class="text-center border-left-1">Amount</th>
                </tr>
                <tr v-for="(payment, index) in data?.datasets" :key="index">
                    <td class="text-center"> 
                        <div class="flex align-items-center "> {{ payment.name }}
                        </div>
                    </td>
                    <td class="text-center border-left-1">  <CurrencyFormat :value="payment.values" /></td>
                </tr>
                <tr>
            <th class="text-right border-1 pe-2">Total</th>
            <th class="border-1"><CurrencyFormat :value="totaldActualValues" /></th>
        </tr>
                </table>
            </div>
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
const totaldActualValues = computed(() => {
  return data.value.datasets.reduce((sum, payment) => sum + payment.values, 0);
}); 
const totalExpectedValues = computed(() => {
  return data.value.datasets.reduce((sum, payment) => sum + payment.expected_value, 0);
}); 
 
const data = ref({})
function renderdata() {
    loading.value = true     
const doc = getApi('frontdesk.get_business_source_chart_data', {
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
                name: "Actual", type: "bar",
                values:data.value.datasets.map(r=>r.values),
            },
            {
                name: "Expected", type: "bar",
                values:data.value.datasets.map(r=>r.expected_value),
            }
        ]
            },
            type: "bar",
        };

  new Chart("#chartbs", chartConfig);
}
onMounted(() => {
    renderdata()
})       
</script>