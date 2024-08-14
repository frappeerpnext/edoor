<template>
    <ComOwnerContentTitle :label="'Charge - ' + moment(date).format('DD-MM-YYYY')"> 
        <ComPlaceholder text="No Data"  :is-not-empty="data" >   
        <div class="col-12">
            <Skeleton v-if="loading" width="100%" height="20rem"></Skeleton> 
            <div id="chartCharge"></div>
        </div>
<div class="col-12 h-full">
    <Skeleton v-if="loading" width="100%" height="20rem"></Skeleton>     
<div v-else class="surface-ground rounded-lg p-2" >
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
 <tr>
            <th class="text-right border-1 pe-2">Total</th>
            <th class="border-1"><CurrencyFormat :value="totalValues" /></th>
        </tr>
</table>
</div>
</div>  
</ComPlaceholder>
</ComOwnerContentTitle>    

</template>
<script setup>
import {  ref, onMounted,getApi,computed, inject,defineProps,watch } from '@/plugin'
import { Chart } from "frappe-charts/dist/frappe-charts.min.esm"
import ComOwnerContentTitle from '@/views/dashboard/components/ComOwnerContentTitle.vue'
import { Colors } from 'chart.js';
const loading = ref(true)
const moment = inject("$moment")
const props = defineProps({
  date: {
    type: Date,
  },
});
 
const data = ref({})
const totalValues = computed(() => {
  return data.value.datasets.reduce((sum, payment) => sum + payment.values, 0);
});
function renderdata() {
loading.value = true    
const doc = getApi('frontdesk.get_charge_chart_data', {
        property: JSON.parse(localStorage.getItem("edoor_property")).name,
        date: props.date
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
}
watch(() => props.date, (newDate) => {
    if (newDate) {
        renderdata();
    }
}); 
onMounted(() => {
    renderdata()
})       
</script>