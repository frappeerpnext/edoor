<template>
    <ComOwnerContentTitle :label="'Ledger Summary'" :date="moment(date).format('DD-MM-YYYY')">  
      <div class="card">
        <DataTable :value="data?.ledger_summary" tableStyle="min-width: 50rem">
            <Column field="label" :header="$t('Ledger Type')"></Column>
            <Column :header="$t('Opening')" bodyClass="text-right" headerClass="text-right">
                <template #body="slotProps">
                    <CurrencyFormat :value="slotProps.data.opening" />
                </template>
            </Column>
            <Column  :header=" $t('Debit') " bodyClass="text-right" headerClass="text-right">
                <template #body="slotProps">
                    <CurrencyFormat :value="slotProps.data.debit" />
                </template>
            </Column>
            <Column :header=" $t('Credit') " bodyClass="text-right" headerClass="text-right">
                <template #body="slotProps">
                    <CurrencyFormat :value="slotProps.data.credit" />
                </template>
            </Column>
            <Column  :header=" $t('Balance') " bodyClass="text-right" headerClass="text-right">
                <template #body="slotProps">
                    <CurrencyFormat :value="(slotProps.data.debit - slotProps.data.credit)" />
                </template>
            </Column>
            <ColumnGroup type="footer">
        <Row>
          <Column :footer="$t('Total') + ':'"  footerStyle="text-align:left" />
          <Column  footerStyle="text-align:right" >
            <template #footer >
              <CurrencyFormat :value="getTotal('opening')" />
            </template>
          </Column>
          <Column  footerStyle="text-align:right">
            <template #footer>
              <CurrencyFormat :value="getTotal('debit')" />
            </template>
          </Column>
          <Column footerStyle="text-align:right" >
            <template #footer >
              <CurrencyFormat :value="getTotal('credit')" />
            </template>
          </Column>
          <Column  footerStyle="text-align:right">
            <template #footer >
              <CurrencyFormat :value="(getTotal('debit') - getTotal('credit'))" />
            </template>
          </Column>
        </Row>
      </ColumnGroup>
        </DataTable>
    </div>
</ComOwnerContentTitle>    
</template>
<script setup>
import {i18n} from '@/i18n';
const { t: $t } = i18n.global;
import {  ref, onMounted,getApi,computed,inject,defineProps,watch } from '@/plugin'
import { Chart } from "frappe-charts/dist/frappe-charts.min.esm"
import ComOwnerContentTitle from '@/views/dashboard/components/ComOwnerContentTitle.vue'
import { Colors } from 'chart.js';
const moment = inject("$moment")
const getTotal = ref((column_name) => {

    return data.value.ledger_summary?.reduce((n, d) => n + d[column_name], 0)

});
const props = defineProps({
    date: {
        type: Date,
    },
}); 
 
const totalValues = computed(() => {
  return 10
}); 
const data = ref({})
function renderdata() {
const doc = getApi('frontdesk.get_day_end_summary_report', {
        property: JSON.parse(localStorage.getItem("edoor_property")).name,
        date: props.date
    })
    .then((result) => {
            data.value = result.message
        })
    }    
    onMounted(() => {
    renderdata()
}) 
watch(() => props.date, (newDate) => {
    if (newDate) {
        renderdata();
    }
});       
</script>