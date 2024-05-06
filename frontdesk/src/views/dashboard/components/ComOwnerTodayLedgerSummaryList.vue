<template>
    <ComOwnerContentTitle label="Today Ledger Summary">  
      <div class="card">
        <DataTable :value="data?.ledger_summary" tableStyle="min-width: 50rem">
            <Column field="label" header="Ledger Type"></Column>
            <Column header="Opening">
                <template #body="slotProps">
                    <CurrencyFormat :value="slotProps.data.opening" />
                </template>
            </Column>
            <Column  header="Debit">
                <template #body="slotProps">
                    <CurrencyFormat :value="slotProps.data.debit" />
                </template>
            </Column>
            <Column header="Credit">
                <template #body="slotProps">
                    <CurrencyFormat :value="slotProps.data.credit" />
                </template>
            </Column>
            <Column  header="Balance">
                <template #body="slotProps">
                    <CurrencyFormat :value="(slotProps.data.debit + slotProps.data.credit)" />
                </template>
            </Column>
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
const doc = getApi('frontdesk.get_day_end_summary_report', {
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