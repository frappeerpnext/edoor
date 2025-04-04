<template>
   {{  }}
   <ComDocumentList doctype="Folio Transaction" :options="options">
      <template #name="{ item, index }">
         <Button class="p-0 link_line_action1" link @click="onOpenFolioTransaction(item.name)" >
            {{ item.name }}
         </Button>
      </template>

      <template #account_code="{ item, index }">
         {{ item.account_code }} - {{ item.account_name }}</template>

      <template #Debit="{ item, index }">
         {{ item.type == "Debit" ? item.Debit : 0 }}
      </template>
      <template #Credit="{ item, index }">
         {{ item.type == "Credit" ? item.Debit : 0 }}
      </template>

   </ComDocumentList>

</template>
<script setup>
import ComDocumentList from "@/components/document/ComDocumentList.vue"
const options = {
    
   filters: [["property", '=', window.property_name], ["transaction_type", '=', 'City Ledger'], ["is_base_transaction", '=', 1]]

}

function onOpenFolioTransaction(name){
   window.postMessage("view_folio_transaction_detail" + "|" + name, '*')
}
</script>