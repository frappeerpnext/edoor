<template>
  <ComDocumentList
    doctype="Desk Folio"
    list_view_setting="deskfolio_list"
    :options="options"
    router_name="DeskFolio"
    @row-dblclick="onRowDoubleClick"
  >
    <template #action-button>
      <Button
        class="border-none"
        :label="$t('Add New Desk Folio')"
        icon="pi pi-plus"
        @click="onAddDeskFolio()"
      />
    </template>
    <template #name="{ item, index }">
      <Button
        class="link_line_action1"
        @click="onOpenLink('view_desk_folio_detail', item.name)"
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
        {{ item.guest }} {{ item.guest_name }}
      </Button>
    </template>
    <template #status="{ item, index }">
      <ComStatus :status="item.status" />
    </template>
  </ComDocumentList>
</template>
<script setup>
import { inject } from "@/plugin";
import ComDocumentList from "@/components/document/ComDocumentList.vue";
import ComAddDeskFolio from "@/views/desk_folio/components/ComAddDeskFolio.vue";
import { useDialog } from "primevue/usedialog";
const gv = inject("$gv");
const dialog = useDialog();
const options = {
  fields: [
    { fieldname: "name", label: "Desk Folio #", fieldtype: "Data" },
    { fieldname: "room_number", label: "Room" },
    { fieldname: "reference_number" },
    { fieldname: "room_type", label: "Room Type" },
    { fieldname: "guest" },
    { fieldname: "guest_name", is_hide: true },
    { fieldname: "posting_date", label: "Desk Folio. Date" },
    { fieldname: "total_debit", label: "Debit" },
    { fieldname: "total_credit", label: "Credit" },
    { fieldname: "balance" },
    { fieldname: "owner", fieldtype: "Data", label: "Created By" },
    { fieldname: "creation", fieldtype: "Datetime", label: "Creation" },
    { fieldname: "status" },
  ],
  filterOptions: [
    {
      fieldname: "guest",
    },
    {
      fieldname: "status",
    },
    {
      fieldname: "room_type",
    },
    {
      fieldname: "room_number",
    },
    {
      fieldname: "posting_date",
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
  onOpenLink("view_desk_folio_detail", data.name);
}
function onOpenLink(action, name) {
  window.postMessage(action + "|" + name, "*");
}
function onAddDeskFolio(data) {
  if (!gv.cashier_shift?.name) {
    gv.toast("error", "Please Open Cashier Shift.");
    return;
  }
  dialog.open(ComAddDeskFolio, {
    data: { data },
    props: {
      header: `Add New Desk folio`,
      style: {
        width: "50vw",
      },

      modal: true,
      closeOnEscape: false,
      position: "top",
      breakpoints: {
        "960px": "50vw",
        "640px": "100vw",
      },
    },
    onClose: (options) => {
      const result = options.data;
      if (result) {
        loadData();
        window.postMessage("view_desk_folio_detail|" + result.name, "*");
      }
    },
  });
}
</script>
