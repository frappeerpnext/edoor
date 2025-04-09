<template>
    <ComDocumentList
      doctype="City Ledger Invoice"
      list_view_setting="city_ledger_detail_city_ledger_invoice_list"
      :options="options"
      @row-dblclick="onRowDoubleClick"
    >
      <template #action-button>
        <Button
          class="border-none"
          :label="$t('New City Ledger Invoice')"
          icon="pi pi-plus"
          @click="onAddCityLedgerInvoice"
        />
      </template>
      
      
      <template #payment_status="{ item, index }">
        <ComStatus :status="item.payment_status" />
      </template>
      <template #status="{ item, index }">
        <ComStatus :status="item.status" />
      </template>
      <template #footer="{ item }">
        <Column :footer="$t('Total') + ':'" :colspan="7"
        footerStyle="text-align:right" />
      </template>
    </ComDocumentList>
  </template>
  <script setup>
  import { inject ,getDialogScrollHeight} from "@/plugin";
  
  import ComAddCityLedgerInvoice from '@/views/city_ledger_invoice/components/ComAddCityLedgerInvoice.vue';

  
  import { useDialog } from "primevue/usedialog";
  const props = defineProps({
    city_ledger:String
  })
  const gv = inject("$gv");
  import { i18n } from '@/i18n';
const { t: $t } = i18n.global;
  const dialog = useDialog();
  const options = {
    fields: [
      { fieldname: "name", label: "Tran. #",action:"view_city_ledger_invoice_detail" },
      { fieldname: "payment_status", label: "Payment Status" },
      { fieldname: "posting_date", label: "Date" },
      { fieldname: "reference_number", label: "Ref #" },
      { fieldname: "contact_name" },
      { fieldname: "phone_number" },
      { fieldname: "total_debit", label: "Debit" },
      { fieldname: "total_credit", label: "Credit" },
      { fieldname: "balance" },
      { fieldname: "modified_by",  label: "Modified by" },
      { fieldname: "modified", fieldtype: "Datetime", label: "Last Modified" },
      { fieldname: "status" },
    ],
    filterOptions: [
      
      {
        fieldname: "posting_date",
      },
      {
        fieldname: "payment_status",
      },
      {
        fieldname: "status",
      },

      
    ],
    filters:[["property","=",window.property_name],["city_ledger","=",props.city_ledger]],
    hideSaveView:true,
    scrollHeight:getDialogScrollHeight(-245)
    
  };
  
  function onRowDoubleClick(data) {
    onOpenLink("view_city_ledger_invoice_detail", data.name);
  }
  function onOpenLink(action, name) {
    window.postMessage(action + "|" + name, "*");
  }
  
function onAddCityLedgerInvoice() {
    
    dialog.open(ComAddCityLedgerInvoice, {
        data: {
            city_ledger:props.city_ledger
        },
        props: {
            header: $t(`Add New City Ledger Invoice`),
            style: {
                width: '65vw',
            },
            modal: true,
            closeOnEscape: false,
            position: 'top',
            breakpoints:{
                '960px': '50vw',
                '640px': '100vw'
            },
        },
        onClose: (options) => {
            const data = options.data;
            if (data) {
              window.postMessage({action:"ComDocumentList"},"*")
       
       window.postMessage("view_city_ledger_invoice_detail|" + data.name, "*");

            }
        }
    });
}

  </script>
  