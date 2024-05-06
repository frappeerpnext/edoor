<template>
    <ComOwnerContentTitle label="F&B Payment">    
      hiiiii
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
        })
    }      
</script>