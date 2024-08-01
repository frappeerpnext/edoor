<template>

    <ComOwnerContentTitle label="Current Month">  
      <div class="flex justify-content-end mr-5">
        <SplitButton :model="items" @click="save" class="p-component spl__btn_cs sp mb-0 mt-2 mr-2" :label="$t(view_chart_by)"></SplitButton>
        <SplitButton :model="duration_types" :label="$t(duration_type)"   class="p-component spl__btn_cs sp mb-0 mt-2"></SplitButton>
    
    </div>
         <TabView>
            <TabPanel>
        <template #header>
            <div class="flex align-items-center gap-2 ">
                <span class="font-bold white-space-nowrap">Chart</span>
            </div>
        </template>
        <div>
<div class="col w-full p-0">
      <div class="grid w-full py-5">
      <div id="chart_mt" class="w-full" style="margin-bottom: -30px;"></div>
      </div> 
</div>
        </div>
    </TabPanel>
    <TabPanel>
        <template #header>
            <div class="flex align-items-center gap-2">
                <span class="font-bold white-space-nowrap">Data</span>
            </div>
        </template>
        <div class="w-full overflow-auto px-2 py-4">
      <table class="w-full" >
          <tr class="border-1 p-2 w-full">
            <th>Name</th>
            <th v-for="l in data.labels" class="p-2 border-1">{{l}}</th>
          </tr>
          <tr class="border-1" v-for="dataset in data.datasets">
              <th class="white-space-nowrap py-2 px-4 " >{{ dataset.name }}</th>
              <td  class="p-1 border-1 white-space-nowrap" v-for="(value, index) in dataset.values" :key="index">
                <CurrencyFormat :value="value" />
              </td>
          </tr>
        </table>
      </div>
    </TabPanel>
           
        </TabView>
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
const duration_type = ref("Daily")
const view_chart_by = ref("Time Series")
import {i18n} from '@/i18n';
const { t: $t } = i18n.global;  
const data = ref({})
const items = [
    {
        label: $t('Time Series'),
        icon: 'pi pi-clock',
        command: () => {
            view_chart_by.value =("Time Series")
            renderdata()
        }
    },
    {
        label: $t('Business Source'),
        icon: 'pi pi-briefcase',
        command: () => {
            view_chart_by.value = "Business Source"
            renderdata()
        }
    },
    {
        label: $t('Room Type'),
        icon: 'pi pi-building',
        command: () => {
            view_chart_by.value = "Room Type"
            renderdata()
        }
    },
   
];

const duration_types = [
    {
        label: $t('Daily'),
        command: () => {
            duration_type.value = ("Daily")
            renderdata()
        }
    },
    {
        label: $t('Monthly'),
        command: () => {
            duration_type.value = ("Monthly")
            renderdata()
        }
    }

]
function renderdata() {
    loading.value = true 
const doc = getApi('frontdesk.get_owner_dashboard_current_mount_chart', {
        property: JSON.parse(localStorage.getItem("edoor_property")).name,
        duration_type:duration_type.value,
        view_chart_by:view_chart_by.value
    })
    .then((result) => {
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