<template>
    <ComOwnerContentTitle label="Current Month">  
      <div class="grid w-full py-5">
      <div id="chart_mt" class="w-full" style="margin-bottom: -30px;"></div>
      </div> 
   
    </ComOwnerContentTitle>   
</template>
<script setup>
import ComOwnerContentTitle from '@/views/dashboard/components/ComOwnerContentTitle.vue'
import {  ref, onMounted,getApi } from '@/plugin'
import { Chart } from "frappe-charts/dist/frappe-charts.min.esm"
import NumberFormat from 'number-format.js'
const setting = JSON.parse(  localStorage.getItem("edoor_setting"))
const loading = ref(true)
const formatter = new Intl.NumberFormat(setting.currency.name, {
  style: 'currency',
  currency: setting.currency.name,
});
 
const data = ref({})
function renderdata() {
    loading.value = true 
const doc = getApi('frontdesk.get_owner_dashboard_current_mount_chart', {
        property: JSON.parse(localStorage.getItem("edoor_property")).name,
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
            datasets:data.value.datasets
            }
,
  height: 350,
  colors: data.value.datasets.map(r=>r.colors),
  axisOptions: {
    xAxisMode: "tick",
    xIsSeries: true
  },
  barOptions: {
    stacked: true,
    spaceRatio: 0.3
  },
  tooltipOptions: {
        formatTooltipX: d => d,
        formatTooltipY: d => formatter.format(Number(d)).toLocaleString()
      }
}

  new Chart("#chart_mt", chartConfig);
  
}

onMounted(() => {
    renderdata()
})   
</script>