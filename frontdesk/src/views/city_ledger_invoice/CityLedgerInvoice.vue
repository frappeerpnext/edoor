<template>
    <ComDocumentList
      doctype="City Ledger Invoice"
      list_view_setting="city_ledger_invoice_list"
      :options="options"
      router_name="CityLedgerINvoice"
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
  import { inject } from "@/plugin";
  import ComDocumentList from "@/components/document/ComDocumentList.vue";
  import ComAddCityLedgerInvoice from '@/views/city_ledger_invoice/components/ComAddCityLedgerInvoice.vue';
import ComCityLedgerInvoiceDetail from '@/views/city_ledger_invoice/components/ComCityLedgerInvoiceDetail.vue';

  import { useDialog } from "primevue/usedialog";
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
      { fieldname: "city_ledger_name",action:"view_city_ledger_detail",id_field:"city_ledger" },
      { fieldname: "city_ledger",is_hide:true },
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
        fieldname: "city_ledger",
      },
      {
        fieldname: "payment_status",
      },
      {
        fieldname: "status",
      },

      
    ],
    settingMenus: [
      {
        label: "Refresh",
        icon: "pi pi-refresh",
      },
      {
        label: "Export",
        icon: "pi pi-upload",
      },
    ],
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
            // name: name.value,
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
  