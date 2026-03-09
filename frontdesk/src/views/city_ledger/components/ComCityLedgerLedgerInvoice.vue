<template>
     <ComDocumentList doctype="City Ledger Invoice" 
            list_view_setting="recent_city_ledger_invoice_list"
           :options="options" >
           <template #status="{ item, index }">
      <ComStatus :status="item.status" />
    </template>
    <template #payment_status="{ item, index }">
      <ComStatus :status="item.payment_status" />
    </template>
            </ComDocumentList>

</template>
<script setup>
const options = {
  fields: [
    { fieldname: "name", action: "view_city_ledger_invoice_detail" },
    { fieldname: "city_ledger_name" },
    { fieldname: "total_debit", fieldtype: "Currency", align: "right" },
    { fieldname: "total_credit", fieldtype: "Currency", align: "right" },
    { fieldname: "balance", fieldtype: "Currency", align: "right" },
  
    { fieldname: "owner", label: "Created By" },
    { fieldname: "creation", fieldtype: "Datetime", label: "Created Date" },
      { fieldname: "status" },
    { fieldname: "payment_status" },
  ],
  filters: [["property", "=", window.property_name]],
  limit:10,
  scrollHeight:"470px",
    hideFilter:true,
    hideHeader:true,
    hidePager:true,
    hidesavefilter:true,
    hideSaveView:true
}
</script>