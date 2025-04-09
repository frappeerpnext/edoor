<template>
 
   <ComDocumentList doctype="Folio Transaction" 
   title="City Ledger Transaction"
   :options="options"
   list_view_setting="city_ledger_folio_transaction"
   @row-dblclick="onRowDblclick"
   >
     
          
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
      <template #payment_status="{ item, index }">
         <ComStatus  :status="item.payment_status" />
      </template>

   </ComDocumentList>

</template>
<script setup>
import ComDocumentList from "@/components/document/ComDocumentList.vue"
import ComStatus from "@/components/label/ComStatus.vue"
const options = {
   fields:[
      {fieldname:"name",label:"Tran. #",action:"view_folio_transaction_detail"},
      {fieldname:"posting_date"},
      {fieldname:"source_transaction_number", label:"Source Tran. #"},
      {fieldname:"source_transaction_type", is_hide:true},
      {fieldname:"reservation",label:"Res. #",action:"view_reservation_detail"},
      {fieldname:"reservation_stay",label:"Stay. #",action:"view_reservation_stay_detail"},
      {fieldname:"transaction_number",label:"City Ledger" ,is_hide:true},
      {fieldname:"city_ledger_name",label:"City Ledger",action:"view_city_ledger_detail",id_field:"transaction_number"},
      {fieldname:"guest",label:"Guest",is_hide:true},
      {fieldname:"guest_name",label:"Guest",action:"view_guest_detail",id_field:"guest"},
      {fieldname:"room_number",label:"Room"},
      {fieldname:"room_type_alias",label:"Room Type" , is_hide:true},
      {fieldname:"account_code",label:"Account Code"},
      {fieldname:"account_name",label:"account_name", is_hide:true},
      {fieldname:"type",label:"account_name", is_hide:true},
      {fieldname:"transaction_amount as debit",label:"Debit"},
      {fieldname:"transaction_amount as credit",label:"Credit"},
      {fieldname:"modified",label:"Last Modified",fieldtype:"Datetime"},
      {fieldname:"payment_status"},
      

   ],
   filterOptions:[
      {fieldname:"posting_date"},
      {fieldname:"source_transaction_type",label:"Ledger Type", fieldtype:"Link", options:"Ledger Type"},
      {fieldname:"transaction_number",label:"City Ledger", fieldtype:"Link", options:"City Ledger",operator:"="},
      {fieldname:"reservation"},
      {fieldname:"reservation_stay"},
      {fieldname:"account_code",fieldtype:"Tree"},
      {fieldname:"payment_status"},

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