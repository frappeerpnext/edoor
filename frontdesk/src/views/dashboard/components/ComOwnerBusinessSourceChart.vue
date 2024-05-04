<template>
    {{data}}
    <ComOwnerContentTitle label="Business Source">    
        <div class="col-12">
            <div id="chartbs"></div>
        </div>
<div class="col-12 h-full">
    <div class="flex ">
        <div class="col-6">
            <div class="surface-ground rounded-lg p-2 h-full">
                <table class="w-full border-bottom-1">
                <tr >
                    <th colspan="2" class="text-start"> Actual </th>
                </tr>
                <tr class="border-bottom-1">
                    <th class="text-start ">Charge List</th>
                    <th class="text-center border-left-1">Amount</th>
                </tr>
                <tr v-for="(payment, index) in data?.datasets_actual" :key="index">
                    <td class="text-center"> 
                        <div class="flex align-items-center "> {{ payment.name }}
                        </div>
                    </td>
                    <td class="text-center border-left-1">  <CurrencyFormat :value="payment.values" /></td>
                </tr>
                </table>
            </div>
        </div>
        <div class="col-6">
            <div class="surface-ground rounded-lg p-2 h-full">
                <table class="w-full border-bottom-1">
                <tr >
                    <th colspan="2" class="text-start"> Expected </th>
                </tr>
                <tr class="border-bottom-1">
                    <th class="text-start ">Charge List</th>
                    <th class="text-center border-left-1">Amount</th>
                </tr>
                <tr v-for="(payment, index) in data?.datasets_expected" :key="index">
                    <td class="text-center"> 
                        <div class="flex align-items-center "> {{ payment.name }}
                        </div>
                    </td>
                    <td class="text-center border-left-1">  <CurrencyFormat :value="payment.values" /></td>
                </tr>
                </table>
            </div>
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

 
 
const data = ref({})
function renderdata() {
const doc = getApi('frontdesk.get_business_source_chart_data', {
        property: JSON.parse(localStorage.getItem("edoor_property")).name,
        date: JSON.parse(localStorage.getItem("edoor_working_day")).date_working_day
    })
    .then((result) => {
            data.value = result.message
            console.log(data)
            renderChart()
           
        })
    }
    function renderChart() {
        const chartConfig = {
            data: {
            labels:data.value.labels,
            datasets:[{
                name: "Actual", type: "bar",
                values:data.value.datasets_actual.map(r=>r.values),
            },
            {
                name: "Expected", type: "bar",
                values:data.value.datasets_expected.map(r=>r.values),
            }
        ]
            },
            type: "bar",
        };

  new Chart("#chartbs", chartConfig);
  console.log(chartConfig);
}
onMounted(() => {
    renderdata()
})       
</script>