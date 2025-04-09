<template>
           <ComDocumentList doctype="City Ledger" 
            list_view_setting="recent_city_ledger_account_list"
           :options="options" >
           <template #status="{ item, index }">
      <ComStatus :status="item.status" />
    </template>
            </ComDocumentList>

  </template>
  
  <script setup>
  const options = {
    fields: [
      {fieldname:"name" , action:"view_city_ledger_detail" },
      {fieldname:"city_ledger_name"},
      {fieldname:"city_ledger_type"},
      {fieldname:"business_source" , action:"view_business_source_detail"},
      {fieldname:"total_debit",label:"Debit"},
      {fieldname:"total_credit",label:"Credit"},
      {fieldname: "balance" },
      {fieldname: "owner", fieldtype: "Data", label: "Created By" },
      {fieldname: "modified", fieldtype: "Datetime", label: "Last Modified" },
      {fieldname:"status"},
    ],
    orderBy:{
        field: "modified",
        order: "desc"
       },
    scrollHeight:"400px",
    hideFilter:true,
    hideHeader:true,
    hidePager:true,
    hidesavefilter:true
  };
  
  function onOpenLink(view, name) {
    window.postMessage(view + "|" + name, "*");
  }
  </script>
  