<template>
    <ComOwnerContentTitle label="Room Type">  
        {{data}}  
        <div class="card">
        <TabView>
            <TabPanel>
        <template #header>
            <div class="flex align-items-center gap-2 ">
                <span class="font-bold white-space-nowrap">Actual</span>
                <span style="background:#0000001f" class="text-sm rounded-lg px-2 py-1 ">      <CurrencyFormat :value="32423" />  </span>
            </div>
        </template>
        <p class="m-0">
            Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo
            consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.
        </p>
    </TabPanel>
    <TabPanel>
        <template #header>
            <div class="flex align-items-center gap-2">
                <span class="font-bold white-space-nowrap">Expected</span>
                <span style="background:#0000001f" class="text-sm rounded-lg px-2 py-1 "> <CurrencyFormat :value="32423" /> </span>
            </div>
        </template>
        <p class="m-0">
            Sed ut perspiciatis unde omnis iste natus error sit voluptatem accusantium doloremque laudantium, totam rem aperiam, eaque ipsa quae ab illo inventore veritatis et quasi architecto beatae vitae dicta sunt explicabo. Nemo enim
            ipsam voluptatem quia voluptas sit aspernatur aut odit aut fugit, sed quia consequuntur magni dolores eos qui ratione voluptatem sequi nesciunt. Consectetur, adipisci velit, sed quia non numquam eius modi.
        </p>
    </TabPanel>
           
        </TabView>
    </div>
</ComOwnerContentTitle>    
</template>
<script setup>
import {  ref, onMounted,getApi } from '@/plugin'
import { Chart } from "frappe-charts/dist/frappe-charts.min.esm"
import ComOwnerContentTitle from '@/views/dashboard/components/ComOwnerContentTitle.vue'
import { Colors } from 'chart.js';
import TabView from 'primevue/tabview';
const data = ref({})
function renderdata() {
const doc = getApi('frontdesk.get_charge_chart_data', {
        property: JSON.parse(localStorage.getItem("edoor_property")).name,
        date: JSON.parse(localStorage.getItem("edoor_working_day")).date_working_day
    })
    .then((result) => {
            data.value = result.message
            
    
           
        })
    }
   
</script>