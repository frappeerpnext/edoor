<template>
<div>           
    <div class="mt-1 mb-2">
        <b>transaction during  - {{ working_day.date_working_day }}</b>
       
    </div>
    <div class="grid ">
         <ComBoxSummaryBalanceTransaction label="opening Balance" :value='cityLedgerAmountSummary?.opening_balance' :isCurrency="true" :class="'col-4 md:col bg-white md:mx-1 my-1'" >
         </ComBoxSummaryBalanceTransaction>   
         <ComBoxSummaryBalanceTransaction label="Debit" :value='cityLedgerAmountSummary?.debit' :isCurrency="true" :class="'col-4 md:col md:mx-1 my-1'" />
         <ComBoxSummaryBalanceTransaction label="Credit" :value='cityLedgerAmountSummary?.credit' :isCurrency="true" :class="'col-4 md:col bg-red-50 md:mx-1 my-1'" />
         <ComBoxSummaryBalanceTransaction label="Balance" :value='cityLedgerAmountSummary?.balance' :isCurrency="true" :class="'col-4 md:col bg-green-50 md:mx-1 my-1'" />
    </div>
    <div class="grid mt-1">
        <ComBoxSummaryBalanceTransaction label="Pending Invoice" :value='transatction?.pending_balance.count_pending' :class="'col-4 md:col  md:mx-1 my-1'" />
        <ComBoxSummaryBalanceTransaction label="Unpaid Invoice" :value='transatction?.pending_balance.city_ledger_invoice_pending' :isCurrency="true" :class="'col-4 md:col  md:mx-1 my-1'" />
        <ComBoxSummaryBalanceTransaction label="UnInvoice" :value='transatction?.pending_balance.city_ledger_uninvoice' :isCurrency="true" :class="'col-4 md:col md:mx-1 my-1'" />
    </div>

</div>
</template>
<script setup>
import { ref, getDoc, inject, useDialog, onMounted, deleteDoc, useConfirm, onUnmounted, useToast ,getApi} from '@/plugin'
import ComBoxSummaryBalanceTransaction from '@/views/city_ledger/components/ComBoxSummaryBalanceTransaction.vue';

const working_day =  window.working_day
const props = defineProps({
    data: Object,
})
const cityLedgerAmountSummary = ref()
const transatction = ref()
function loadData(){
    getApi("utils.get_city_ledger_amount_summary", {
        filters: {
            end_date: working_day.date_working_day,
            city_ledger: props.data?.name
        }
    }).then((result) => {
        cityLedgerAmountSummary.value = result.message
    })
    console.log(props.data?.name)
    getApi("city_ledger.get_balance_city_ledger",{ property: window.property_name , date:window.current_working_date , cityLedger:props.data?.name }).then((result)=>{
        transatction.value = result.message;
    })
}
onMounted(() => {
    loadData()
})
</script>