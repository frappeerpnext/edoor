<template>
    <div>

         <ComDocumentList doctype="Folio Transaction" :options="options">
            <template #account_code="{ item, index }">
         {{ item.account_code }} - {{ item.account_name }}</template>
      <template #debit="{ item, index }">
         <CurrencyFormat  :value="item.type == 'Debit' ? item.debit : 0" />
      </template>
      <template #credit="{ item, index }">
         <CurrencyFormat  :value="item.type == 'Credit' ? item.credit : 0" />
      </template>
      <template #reservation_status="{ item, index }">
      <ComReservationStatus :statusName="item.reservation_status" />
    </template>
    </ComDocumentList>
    </div>
</template>
<script setup>
    const options = {
        fields:[
            {"fieldname":"name" , label:"Tran#" , action:"view_folio_transaction_detail"},
            {"fieldname":"posting_date" } ,
            {"fieldname":"transaction_number",is_hide:true } ,
            {"fieldname":"city_ledger_name", id_field:"transaction_number", action:"view_city_ledger_detail",label:"City Ledger" } ,
            {"fieldname":"reservation_stay",label:"Stay#",action:"view_reservation_stay_detail"},
            {"fieldname":"source_transaction_type",label:"Source Type"},
            {"fieldname":"reference_number" , label:"Source#" , action:"view_folio_transaction_detail"},
            {"fieldname":"account_name",label:"account_name", is_hide:true},
            {"fieldname":"type",label:"account_name", is_hide:true},
            {"fieldname":"transaction_amount as debit",label:"Debit"},
            {"fieldname":"transaction_amount as credit",label:"Credit"},
            { "fieldname": "total_amount" },
            { "fieldname": "reservation_status"  },
        { "fieldname": "owner", fieldtype: "Data", label: "Created By" },
        { "fieldname": "modified", fieldtype: "Datetime", label: "Last Modified" }
        ],
       limit:10,

       filters:[
        ["property","=",window.property_name],
        ["transaction_type","=",'City Ledger'],
    ],
       orderBy:{
        field: "creation",
        order: "desc"
       },
       scrollHeight:"473px",
        hideFilter:true,
        hideHeader:true,
        hidePager:true,
        hidesavefilter:true,
        hideSaveView:true
    }
    function onOpenLink(action, name) {
        window.postMessage(action + '|' + name, '*')
    }
</script>
 
 