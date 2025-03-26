<template>
   <div v-if="city_ledger">
    
    <DataTable v-model:selection="selectedData" :value="data"   scrollable scrollHeight="400px" :virtualScrollerOptions="{ itemSize: 46 }" tableStyle="min-width: 50rem">
      <template #empty>
        <div class="flex items-center justify-center h-full  p-16 text-2xl">
  There is no city ledger transaction
</div>

        </template> 
      <Column selectionMode="multiple" headerStyle="width: 3rem"></Column>
    <Column field="name" header="Folio Tran. #"></Column>
    <Column field="posting_date" header="Posting Date" >
        <template #body="slotProps">
            <span>{{ moment.utc(slotProps.data.posting_date).format("DD-MM-YYYY") }}</span>
      </template>
    </Column>
    <Column field="account_code" header="Acc. Code" ></Column>    
    <Column field="account_name" header="Acc. Name" ></Column>    
    <Column field="guest_name" header="Guest" ></Column>    
    <Column field="transaction_amount" header="Amount">
        <template #body="slotProps">
        <CurrencyFormat :value="slotProps.data.transaction_amount" class="white-space-nowrap" />
    </template>
    </Column>
    <Column field="note" header="Note" />
    
</DataTable>
   </div>
   <div v-else>
    Plese select a city ledger account
   </div>
</template>
<script setup>

    import {ref,inject, getDocumentList } from "@/plugin"
import { watch } from "vue";
const moment = inject("$moment")
const props = defineProps({
    city_ledger:String,
    city_ledger_invoice: {
    type: String,
    default: null
  }
})


const selectedData = defineModel('selectedData')

const data = ref([]);
 

watch(
  () => props.city_ledger,   
  (newValue, oldValue) => {
    if (newValue !== oldValue && newValue) {
      getFolioTransactionData();
    }else {
        data.value = []
        selectedData.value = []
    }
  },
  
);

async function getFolioTransactionData(){
    const filters = [
    ["property", "=", window.property_name],
    ["transaction_type", "=", "City Ledger"],
    ["transaction_number", "=", props.city_ledger]
    ];
    
    filters.push(["source_transaction_type", "is", "set"]);
    filters.push(["city_ledger_invoice", "is", "not set"]);
  
    const resp =await getDocumentList("Folio Transaction",{
        fields:["name","posting_date","account_code","account_name","transaction_amount",'guest_name',"note"],
        filters:filters,
        limit: 1000000,
    })
    
    if(resp.data){
        data.value = resp.data
    }

}

</script>