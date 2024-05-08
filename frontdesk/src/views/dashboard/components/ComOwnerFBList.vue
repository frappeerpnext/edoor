<template>
    <ComOwnerContentTitle label="F&B">    
    {{data}}
    <div class="card">
        <DataTable :value="data?.datasets_actual" tableStyle="min-width: 50rem">
            <Column field="name" header="Name"></Column>
        </DataTable>
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
const doc = getApi('frontdesk.get_f_and_b_chart_data', {
        property: JSON.parse(localStorage.getItem("edoor_property")).name,
        date: JSON.parse(localStorage.getItem("edoor_working_day")).date_working_day
    })
    .then((result) => {
            data.value = result.message
        })
    } 
    onMounted(() => {
    renderdata()
})       
</script>