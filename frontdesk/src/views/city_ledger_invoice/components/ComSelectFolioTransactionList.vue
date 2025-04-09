<template>
   <div v-if="city_ledger">
    
    <DataTable v-model:selection="selectedData" :value="data"   scrollable scrollHeight="400px" :virtualScrollerOptions="{ itemSize: 46 }" tableStyle="min-width: 50rem">
      <template #empty>
        <div class="flex items-center justify-center h-full  p-16 text-2xl">
  There is no city ledger transaction
</div>

        </template> 
      <Column selectionMode="multiple" headerStyle="width: 3rem"></Column>
    <Column field="name" header="Tran. #">
      <template #body="slotProps">
        
        <Button class="link_line_action1" @click="onOpenLink('view_folio_transaction_detail', slotProps.data.name)" link>
          {{slotProps.data.name}}

            </Button>
           
           
      </template>
    </Column>
    <Column field="source_transaction_number" header="Folio. #">
      <template #body="slotProps">
        <Button v-if="slotProps.data.source_transaction_type =='Reservation Folio'" class="link_line_action1" @click="onOpenLink('view_reservation_folio_detail', slotProps.data.source_transaction_number)" link>
          {{slotProps.data.source_transaction_number}}

            </Button>
           
           
      </template>
    </Column>
    <Column field="reference_number" header="Ref. #">
      <template #body="slotProps">
        <Stack gap="1px">
          <span>{{slotProps.data.reference_number}}</span>
          <Stack v-if="slotProps.data.reservation" :row="true">
            <label>Res. #: </label>
            <Button class="link_line_action1" @click="onOpenLink('view_reservation_detail', slotProps.data.reservation)" link>
            {{slotProps.data.reservation}}

            </Button>
          </Stack>
          <!-- stay -->
          <Stack v-if="slotProps.data.reservation_stay" :row="true">
            <label>Stay. #: </label>
            <Button class="link_line_action1" @click="onOpenLink('view_reservation_stay_detail', slotProps.data.reservation_stay)" link>
            {{slotProps.data.reservation_stay}}

            </Button>
          </Stack>
          

          
        </Stack>
        

           
      </template>
    </Column>
    <Column field="posting_date" header="Posting Date" >
        <template #body="slotProps">
            <span>{{ moment.utc(slotProps.data.posting_date).format("DD-MM-YYYY") }}</span>
      </template>
    </Column> 
    <Column field="account_name" header="Accont Code" >
      <template #body="slotProps">
            <span>{{  slotProps.data.account_code }} - {{  slotProps.data.account_name }}</span>
      </template>
    </Column>    
    <Column field="guest_name" header="Guest" >
      <template #body="slotProps">
        <Button class="link_line_action1" @click="onOpenLink('view_guest_detail', slotProps.data.guest)" link>
          {{slotProps.data.guest_name}}

            </Button>
      </template>
    </Column>    
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
        fields:["name","reference_number","source_transaction_number","source_transaction_type","reservation","reservation_stay","posting_date","account_code","account_name","transaction_amount","guest",'guest_name',"note"],
        filters:filters,
        limit: 1000000,
    })
    
    if(resp.data){
        data.value = resp.data
    }

}

function onOpenLink(action, name) {
        
        window.postMessage(action + '|' + name, '*')
    }
    


</script>