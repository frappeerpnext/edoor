<template>
<div>
    <span class="text-xl">{{$t('Top Debtor Companies')}}</span>
<div>
    <ComChart v-if="chartData" height="300px" :chartData="chartData" />
</div>

</div>  
</template>
<script setup>
    import { ref, onMounted, inject,onUnmounted , getApi , defineExpose } from "@/plugin"  
    
import ComChart from "@/components/chart/ComChart.vue"
   const data = ref()
    const chartData = ref()
    function loadData() {
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