<template>
<div class="bg-white border-round-lg">
    <span class="text-xl font-medium ps-3">{{ $t('Aging Balance') }}</span>
<ComChart v-if="chartData" height="300px" :chartData="chartData" />
<div class="px-3">
<div>
    <span class="text-xl font-medium">{{ $t('Aging List') }}  </span> 
    <div style="width: 100%;">
        <div class="" v-for="d in data?.aging_balance" :key="key">
            <div class="flex justify-content-between align-items-center">
                <span class="py-2">{{ d.label }}</span>
                <span>
                    <CurrencyFormat   :value="d.value" />
                </span>
            </div>
            <div v-tippy="((d.value / data?.pending_balance.total_pending) * 100).toFixed(2) + '%'">
                <ProgressBar style="height:2px" :showValue="false" :value="(d.value / data?.pending_balance.total_pending) * 100"></ProgressBar>
            </div>
        </div>
    </div>
</div>
<div class="grid mt-2">
    <div class="col-6">
    <span class="text-xl font-medium">Pending Balance</span>
    <br>
    <span class="text-4xl font-medium"> <CurrencyFormat :value="data?.pending_balance.total_pending" /> </span>
</div>
<div class="col-6">
    <span class="text-xl font-medium">Uninvoice Balance</span>
    <br>
    <span class="text-4xl font-medium"> <CurrencyFormat :value="data?.pending_balance.city_ledger_invoice_pending" /> </span>
</div>
</div>
<div>
    <ComPendingOutgoingInvoice ref="outgoinginvoice_refresh" />
</div>

</div>
</div>
</template>
<script setup>
 import { ref, onMounted, inject,onUnmounted , getApi ,computed ,defineExpose } from "@/plugin"
import ProgressBar from 'primevue/progressbar';
  import ComChart from "@/components/chart/ComChart.vue"
import ComPendingOutgoingInvoice from "@/views/city_ledger/components/ComPendingOutgoingInvoice.vue"
 const data = ref()
 const balance = ref()
 const moment= inject("$moment")
 const outgoinginvoice_refresh = ref(null)
 const chartData = ref()
 function loadData() {  
    outgoinginvoice_refresh.value.loadData() 
        getApi("city_ledger.get_balance_city_ledger",{ property: window.property_name , date:window.current_working_date }).then((result)=>{
            data.value = result.message;

chartData.value = {
    legend: { show: false },  
    datasets: [{
        label: {
            show: true,
            position: 'outside',
            formatter: '{b}: {c} ({d}%)' 
        },
        tooltip: {
            trigger: 'item',  
            formatter: '{b}: {c} ({d}%)' 
        },
        name: 'Debtor Breakdown',
        height: 300,
        type: 'pie',
        radius: '55%',
        data: data?.value.aging_balance.map(item => ({
  value: item.value,
  name: item.label
}))
    }]
};
    })
    }

    function onOpenLink(view, name) {
    window.postMessage(view + "|" + name , '*')
}
defineExpose({
 loadData
});
    onMounted(() => {
    loadData()
 
}); 
</script>