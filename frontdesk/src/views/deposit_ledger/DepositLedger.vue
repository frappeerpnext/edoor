<template>
    <ComDocumentList 
        doctype="Deposit Ledger"
        list_view_setting="deposit_ledger_list"
        router_name="DepositLedger"
        :options= "options"
    >

    </ComDocumentList>

</template>

<script setup> 
import ComDocumentList from "@/components/document/ComDocumentList.vue"


const options = {
    fields:[
        {fieldname: "name" , label: "Deposit #"},
        {fieldname: "posting_date" , label: "Posting Date"},
        {fieldname: "guest" , label: "Guest"},
        {fieldname: "room_number", label: "Room"},
        {fieldname: "room_type", label: "Room Type"},
        {fieldname: "total_debit" , label: "Debit"},
        {fieldname: "total_credit" , label: "Credit"},
        {fieldname: "name" , label: "Deposit #"},
        {fieldname: "name" , label: "Deposit #"}
    ],
}

</script>