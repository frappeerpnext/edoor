<template>
  {{ selectedFolio }}
  <ComDocumentList doctype="Folio Transaction" title="City Ledger Transaction"
    list_view_setting="city_ledger_detail_city_ledger_transaction_list" :options="options"
    @row-dblclick="onRowDoubleClick" wrap-class="surface-50 ">
    <template #action-button>
      <ComFolioActionButton @onClick="AddTransaction" :data="folio_operation" />
      <Button class="conten-btn" @click="viewCityLedgerTransactionReport">
        Print
      </Button>
    </template>


    <template #account_name="{ item, index }">
      {{ item.account_code }} - {{ item.account_name }}
    </template>

    <template #source_transaction_number="{ item, index }">
      <Button v-if="item.source_transaction_number" class="link_line_action1"
        @click="onOpenLink('view_folio_detail', item.source_transaction_number)" link>{{ item.source_transaction_number
        }} </Button>
    </template>

    <template #reservation="{ item, index }">
      <Stack gap="0px" class="flex stack-horizontal">
        <Button v-if="item.reservation" class="link_line_action1"
          @click="onOpenLink('view_reservation_detail', item.reservation)" link>
          {{ item.reservation }}
        </Button>
        <span v-if="item.reservation">|</span>
        <Button v-if="item.reservation_stay" class="link_line_action1"
          @click="onOpenLink('view_reservation_stay_detail', item.reservation_stay)" link>
          {{ item.reservation_stay }}
        </Button>


      </Stack>
    </template>

    <template #debit="{ item, index }">
      <span></span>
      <template v-if="item.type == 'Debit'">

        <CurrencyFormat :value="item.debit" />
      </template>


    </template>

    <template #credit="{ item, index }">
      <span></span>
      <template v-if="item.type == 'Credit'">
        <CurrencyFormat :value="item.credit" />
      </template>

    </template>

    <template #payment_status="{ item, index }">
      <ComStatus :status="item.payment_status" />
    </template>


  </ComDocumentList>
</template>
<script setup>
import { ref, inject, getDialogScrollHeight } from "@/plugin";

import ComAddFolioTransaction from '@/views/reservation/components/ComAddFolioTransaction.vue';
import ComFolioActionButton from '@/views/reservation/components/ComFolioActionButton.vue';
import ComReportServerModal from "@/components/ComReportServerModal.vue";
import { useDialog } from "primevue/usedialog";
const props = defineProps({
  city_ledger: String
})
const selectedFolio = ref(props.city_ledger)
const gv = inject("$gv");
import { i18n } from '@/i18n';
const { t: $t } = i18n.global;
const dialog = useDialog();
const options = {
  fields: [
    { fieldname: "name", label: "Tran. #", action: "view_folio_transaction_detail" },
    { fieldname: "posting_date" },
    { fieldname: "city_ledger_invoice", label: "City Ledger Inv", action: "view_city_ledger_invoice_detail" },
    { fieldname: "source_transaction_number", label: "Source Tran. #" },
    { fieldname: "source_transaction_type", is_hide: true },
    { fieldname: "reservation", label: "Res/Stay" },
    { fieldname: "reservation_stay", label: "Stay. #", is_hide: true },
    { fieldname: "guest", label: "Guest", is_hide: true },
    { fieldname: "guest_name", label: "Guest", action: "view_guest_detail", id_field: "guest" },
    { fieldname: "room_number", label: "Room" },
    { fieldname: "room_type_alias", label: "Room Type", is_hide: true },
    { fieldname: "account_code", label: "Account Code", is_hide: true },
    { fieldname: "account_name", label: "Account Code" },
    { fieldname: "type", is_hide: true },
    { fieldname: "transaction_amount as debit", label: "Debit" },
    { fieldname: "transaction_amount as credit", label: "Credit" },
    { fieldname: "modified", label: "Last Modified", fieldtype: "Datetime" },
    { fieldname: "payment_status" },


  ],
  filterOptions: [
    { fieldname: "posting_date" },
    { fieldname: "reservation" },
    { fieldname: "reservation_stay" },
    { fieldname: "account_code", fieldtype: "Tree" },
    { fieldname: "payment_status" }
  ],
  filters: [["property", "=", window.property_name], ["transaction_number", "=", props.city_ledger], ["transaction_type", "=", "City Ledger"]],
  hideSaveView: false,
  scrollHeight: getDialogScrollHeight(-235)
};

const folio_operation = ref(JSON.parse(window.setting.folio_operation_setting).city_ledger);

function onRowDoubleClick(data) {
  onOpenLink("view_folio_transaction_detail", data.name);
}
function onOpenLink(action, name) {
  window.postMessage(action + "|" + name, "*");
}

function AddTransaction(account_code) {
  // alert("dont forget city ledter balance")
  const dialogRef = dialog.open(ComAddFolioTransaction, {
    data: {
      new_doc: {
        transaction_type: "City Ledger",
        transaction_number: props.city_ledger,
        property: window.property_name,
        account_group: account_code.name
      },
      balance: 111,
      account_code_filter: account_code.filter
    },
    props: {
      header: account_code.label + ' to City Ledger ' + props.name,
      style: {
        width: '60vw',
      },

      modal: true,
      position: "top",
      closeOnEscape: false,
      breakpoints: {
        '960px': '50vw',
        '640px': '100vw'
      },
    },
    onClose: (options) => {
      const data = options.data.message;

      if (data) {

        loadData()
        if ((data.show_print_preview || 0) == 1) {
          if (data.print_format) {
            showPrintPreview(data)
          }
        }
      }

    }
  })
}


function OpenServerReport(report_path, title, parameters = undefined) {

  let params = parameters;
  if (!parameters) {

    params = [
      { name: 'city_ledger', values: [selectedFolio.value] },

    ]
  }
  dialog.open(ComReportServerModal, {
    data: {
      report_path: report_path,
      params: params
    },
    props: {
      header: $t(title),
      style: {
        width: '80vw',
      },
      position: "top",
      modal: true,
      maximizable: true,
      closeOnEscape: false,
      breakpoints: {
        '960px': '80vw',
        '640px': '100vw'
      },
    },
  });
}


function viewCityLedgerTransactionReport() {
  if (window.setting.server_report_url) {

    OpenServerReport("/Front Desk/rptDeskFolioSummary", "Desk Folio Summary Invoice")

  }
  else {
    dialog.open(ComIFrameModal, {
      data: {
        doctype: "Desk%20Folio",
        name: selectedFolio.value,
        report_name: gv.getCustomPrintFormat("eDoor Desk Folio Invoice Summary"),
        show_letter_head: true,
        filter_options: ['invoice_style']
      },
      props: {
        header: "Desk Folio Invoice Summary",
        style: {
          width: '80vw',
        },
        position: "top",
        modal: true,
        maximizable: true,
        breakpoints: {
          '960px': '80vw',
          '640px': '100vw'
        },
      },
    });
  }


}

</script>
