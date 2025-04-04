<template>
 
   <ComDocumentList doctype="Folio Transaction" 
   title="City Ledger Transaction"
   :options="options"
   list_view_setting="city_ledger_folio_transaction"
   @row-dblclick="onRowDblclick"
   >
      <template #name="{ item, index }">
         <Button class="p-0 link_line_action1" link @click="onOpenLink('view_folio_transaction_detail',item.name)" >
            {{ item.name }}
         </Button>
      </template>
      <template #city_ledger_name="{ item, index }">
         <Button class="p-0 link_line_action1" link @click="onOpenLink('view_city_ledger_detail',item.transaction_number)" >
            {{ item.city_ledger_name }}
         </Button>
      </template>
      <template #reservation="{ item, index }">
         <Button v-if="item.reservation" class="p-0 link_line_action1" link @click="onOpenLink('view_reservation_detail',item.reservation)" >
            {{ item.reservation }}
         </Button>
      </template>
      
      <template #reservation_stay="{ item, index }">
         <Button v-if="item.reservation_stay" class="p-0 link_line_action1" link @click="onOpenLink('view_reservation_stay_detail',item.reservation_stay)" >
            {{ item.reservation_stay }}
         </Button>
      </template>
      <template #room_number="{ item, index }">
         {{ item.room_number }} - {{  item.room_type_alias }}
      </template>


      <template #account_code="{ item, index }">
         {{ item.account_code }} - {{ item.account_name }}</template>

      <template #debit="{ item, index }">
          
         <CurrencyFormat  :value="item.type == 'Debit' ? item.debit : 0" />

      </template>
      <template #credit="{ item, index }">
         <CurrencyFormat  :value="item.type == 'Credit' ? item.credit : 0" />
      </template>

   </ComDocumentList>

</template>
<script setup>
import ComDocumentList from "@/components/document/ComDocumentList.vue"
const options = {
   fields:[
      {fieldname:"name",label:"Tran. #"},
      {fieldname:"posting_date",label:"Date"},
      {fieldname:"reservation",label:"Res. #"},
      {fieldname:"reservation_stay",label:"Stay. #"},
      {fieldname:"transaction_number",label:"City Ledger" ,is_hide:true},
      {fieldname:"city_ledger_name",label:"City Ledger"},
      {fieldname:"room_number",label:"Room"},
      {fieldname:"room_type_alias",label:"Room Type" , is_hide:true},
      {fieldname:"account_code",label:"account_code"},
      {fieldname:"account_name",label:"account_name", is_hide:true},
      {fieldname:"type",label:"account_name", is_hide:true},
      {fieldname:"transaction_amount as debit",label:"Debit"},
      {fieldname:"transaction_amount as credit",label:"Credit"},
      {fieldname:"modified",label:"Last Modified",fieldtype:"Datetime"},
      

   ],
   filterOptions:[
      {fieldname:"posting_date"},
      {fieldname:"transaction_number",label:"City Ledger", fieldtype:"Link", options:"City Ledger",operator:"="},
      {fieldname:"reservation"},
      {fieldname:"reservation_stay"},
      {fieldname:"account_code"},

   ],
   filters: [["property", '=', window.property_name], ["transaction_type", '=', 'City Ledger'], ["is_base_transaction", '=', 1]]
}


function onRowDblclick(event) {
onOpenLink("view_folio_transaction_detail", event.name)
}


function onOpenLink(action,name){
   window.postMessage(action + "|" + name, '*')
}
</script>