<template>
    <span class="text-2xl pb-2">Pending Outgoing Invoice</span>
<div  class="pb-5" style="max-height: 50rem;overflow: auto;" > 
    <ComPlaceholder text="No Data" :loading="loading"  :is-not-empty="data && data.length > 0">
        <div  v-for="d in data" class="shadow-md p-3 my-2 border-1 border-round-lg">
<span @click="onOpenLink('view_city_ledger_invoice_detail',d.name)" class="link_line_action1">{{ d.name }} </span>  <span style="background-color: red;" class="border-round-lg px-2 py-1 text-white ms-1">{{ d.status }}</span>
<span v-if="d.payment_status" style="background-color: red;" class="border-round-lg px-2 py-1 text-white ms-1">{{ d.payment_status }}</span>
<div class="grid mt-2">
    <div style="width: 100%;">
        <table style="width: 100%;">
           <ComStayInfoNoBox label="City Ledger" :value="d.city_ledger_name" />
           <ComStayInfoNoBox label="Balance" :isCurrency="true" :value="d.balance" /> 
           <ComStayInfoNoBox label="Posting Date" ><span class="-ms-3">{{gv.dateFormat(moment(d.posting_date))}}</span>
           
           </ComStayInfoNoBox>
        </table>
        <div class="flex justify-content-between mt-2 px-2">
            <span>{{ d.owner }}</span>
            <span> <ComTimeago  :date='d.creation' /></span>
        </div>
    </div>
</div>
</div>
    </ComPlaceholder>    
</div>
</template>
<script setup>
 import { ref, onMounted, inject,onUnmounted , getData ,computed , defineExpose} from "@/plugin"
  import ComChart from "@/components/chart/ComChart.vue"
import ComPendingOutgoingInvoice from "./ComPendingOutgoingInvoice.vue"
 const data = ref()
 const gv = inject('$gv')
 const moment= inject("$moment")
 const chartData = ref()
 const loading = ref(false)
 
async function loadData()  { 
loading.value = true 
const res = await getData("city_ledger.get_city_ledger_invoice",{ property: window.property_name , status:"Open" })
if (res.data){
    data.value = res.data
}  
loading.value = false
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