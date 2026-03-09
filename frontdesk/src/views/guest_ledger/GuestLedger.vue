<template>
  <ComDocumentList
    doctype="Reservation Folio"
    list_view_setting="guest_ledger_reservation_folio"
    router_name="GuestLedger"
    title="Guest Ledger"
    :options="options"
  >
    <template #top-summary>
      <div class="my-4">
        <ComLedgerBalanceKPI
          ledgerType="Reservation Folio"
          :startDate="working_date"
          :endDate="working_date"
        >
        </ComLedgerBalanceKPI>
      </div>
    </template>
    <template #name="{ item, index }">
      <Button
        class="link_line_action1"
        @click="onOpenLink('view_reservation_folio_detail', item.name)"
        link
      >
        {{ item.name }}
      </Button>
    </template>
    <template #guest="{ item, index }">
      <Button
        class="link_line_action1"
        @click="onOpenLink('view_guest_detail', item.guest)"
        link
      >
        {{ item.guest_name }}
      </Button>
    </template>
    <template #reservation="{ item, index }">
      <Button
        class="link_line_action1"
        @click="onOpenLink('view_reservation_detail', item.reservation)"
        link
      >
        {{ item.reservation }}
      </Button>
    </template>

    <template #reservation_stay="{ item, index }">
      <Button
        class="link_line_action1"
        @click="
          onOpenLink('view_reservation_stay_detail', item.reservation_stay)
        "
        link
      >
        {{ item.reservation_stay }}
      </Button>
    </template>

    <template #rooms="{ item, index }">
      {{ item.rooms }} - {{ item.room_types_alias }}
    </template>

    <template #status="{ item, index }">
      <ComStatus :status="item.status" />
    </template>
    <template #reservation_status="{ item, index }">
      <ComReservationStatus :statusName="item.reservation_status" />
    </template>
    <template #verified_amount="{ item, index }"> 
      <i v-if="item.mark_as_verified" class="pi pi-verified text-blue-500 text-xl"></i>
      <span v-else></span>
    </template>

    <template #footerGroup="{ data }">
      <Row>
        <Column footer="Total" :colspan="2" />
        <Column :footer="data.length" />
      </Row>
    </template>
  </ComDocumentList>
</template>
<script setup>
import { ref } from "@/plugin";
import ComDocumentList from "@/components/document/ComDocumentList.vue";
import ComLedgerBalanceKPI from "@/components/ComLedgerBalanceKPI.vue";

import { i18n } from "@/i18n";
import { useDialog } from "primevue/usedialog";

const dialog = useDialog();
const { t: $t } = i18n.global;
const working_date = window.current_working_date;

const options = {
  fields: [
    { fieldname: "name", label: "Folio #" },
    { fieldname: "posting_date", label: "Date" },
    { fieldname: "reservation", label: "Res. #" },
    { fieldname: "reservation_stay", label: "Stay #" },
    { fieldname: "business_source", label: "Source" },
    { fieldname: "rooms" },
    { fieldname: "room_types_alias", is_hide: true },
    { fieldname: "guest" },
    { fieldname: "guest_name", is_hide: true },
    { fieldname: "total_debit", label: "Debit" },
    { fieldname: "total_credit", label: "Credit" },
    { fieldname: "balance" },
    { fieldname: "status" },
    { fieldname: "verified_amount", label: "Verified", custom_class:"text-center" },
    { fieldname: "mark_as_verified", is_hide: true },
    { fieldname: "reservation_status", label: "Res. Status" },
    { fieldname: "modified_by", label: "By" },
    { fieldname: "modified", label: "Last Modified", fieldtype: "Datetime" },
  ],
  filterOptions: [
    { fieldname: "posting_date" },
    { fieldname: "guest" },
    { fieldname: "business_source" },
    {
      fieldname: "room_types",
      fieldtype: "Link",
      options: "Room Type",
      operator: "like",
      optionValue: "label",
    },
    {
      fieldname: "mark_as_verified",
      fieldtype: "Data",
      options: "Mark As Verified",
      operator: "like",
      optionValue: "label",
    },
    {
      fieldname: "rooms",
      fieldtype: "Link",
      options: "Room",
      operator: "like",
      optionValue: "label",
      label: "Room",
    },
  ],
  filters: [
    ["property", "=", window.property_name],
    ["status", "=", "Open"],
  ],
};

function onOpenLink(action, name) {
  window.postMessage(action + "|" + name, "*");
}
</script>
