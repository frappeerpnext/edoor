<template>
<div>
    <span class="text-xl">{{$t('Top Debtor Company')}}</span>
<div>
    <ComChart v-if="chartData" height="300px" :chartData="chartData" />
</div>
<div>
    <span class="text-xl">{{$t('Reccent Transaction')}}</span>
    <div class="mt-2">
    <TabView>
            <TabPanel :header="$t('Journal Transaction')">
                <ComCityLedgerJournalTransactioin ref="cityledger_journal_refresh" />
            </TabPanel>
            <TabPanel :header="$t('City Ledger Account')">
                <ComCityledgerAccount ref="city_ledger_account_refresh" />
            </TabPanel>
            <TabPanel :header="$t('City Ledger Invoice')">
                <ComCityLedgerLedgerInvoice ref="city_ledger_invoice_refresh" />
            </TabPanel>
    </TabView>        
    </div>

</div>
</div>  
</template>
<script setup>
    import { ref, onMounted, inject,onUnmounted , getApi , defineExpose } from "@/plugin"  
    
import TabView from 'primevue/tabview';
import TabPanel from 'primevue/tabpanel';
import ComChart from "@/components/chart/ComChart.vue"
import ComCityLedgerJournalTransactioin from "@/views/city_ledger/components/ComCityLedgerJournalTransactioin.vue";
import ComCityledgerAccount from "@/views/city_ledger/components/ComCityledgerAccount.vue";
import ComCityLedgerLedgerInvoice from "@/views/city_ledger/components/ComCityLedgerLedgerInvoice.vue";
const cityledger_journal_refresh = ref(null)   
const city_ledger_account_refresh = ref(null)
const city_ledger_invoice_refresh = ref(null)
    const data = ref()
    const chartData = ref()
    function loadData() {
        cityledger_journal_refresh.value.loadData()
        city_ledger_account_refresh.value.loadData()
        city_ledger_invoice_refresh.value.loadData()
        getApi("city_ledger.get_top_debtor_company",{ property: window.property_name }).then((result)=>{
            data.value = result.message;
            chartData.value = {
        labels: data.value.map(item => item.city_ledger_name),
        datasets: [
            {
                type:'bar',
                data:data.value.map(item => item.balance) ,
            }
        ],
        
    };
    })
    }
 
defineExpose({
 loadData
});
    onMounted(() => {
    loadData()
 
});
</script>