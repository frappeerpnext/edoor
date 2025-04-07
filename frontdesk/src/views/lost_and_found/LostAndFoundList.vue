<template>
  <ComDocumentList
    ref="docListRef"
    doctype="Lost and Found"
    title="Lost and Found List"
    list_view_setting="lostandfound_list"
    :options="options"
    router_name="LostAndFound"
    @row-dblclick="onRowDoubleClick"
  >
    <template #action-button>
      <Button
        class="border-none"
        :label="$t('Add New Lost and Found')"
        @click="onAddNew()"
      />
    </template>
    <template #name="{ item, index }">
      <Button
        class="link_line_action1"
        @click="onOpenLink('view_lost_and_found_detail', item.name)"
        link
      >
        {{ item.name }}
      </Button>
    </template>
    <template #taken_date="{ item, index }">
        {{item.taken_date ? moment(item.taken_date).format("DD-MM-YYYY") : ''}} 
    </template>
  </ComDocumentList>
</template>
<script setup>
import { ref, inject } from "@/plugin";
import ComDocumentList from "@/components/document/ComDocumentList.vue";
import ComAddLostAndFound from "@/views/lost_and_found/components/ComAddLostAndFound.vue";
import { useDialog } from "primevue/usedialog";
import { i18n } from "@/i18n";
const { t: $t } = i18n.global;
const moment = inject("$moment")
const docListRef = ref(null);
const gv = inject("$gv");
const dialog = useDialog();
const options = {
  fields: [
    { fieldname: "name", label: "Lost and Found Code", fieldtype: "Data" },
    { fieldname: "posting_date", label: "Date", fieldtype: "Date" },
    { fieldname: "location", label: "Location" },
    { fieldname: "status", label: "Status" },
    { fieldname: "note", label: "Note" },
    { fieldname: "is_taken", label: "Is Taken", fieldtype: "Check" },
    { fieldname: "taken_date", label: "Taken Date", fieldtype: "Date" },
    { fieldname: "taken_by", label: "Taken By" },
  ],
  filterOptions: [
    { fieldname: "status" },
    { fieldname: "location" },
    { fieldname: "posting_date" },
    { fieldname: "taken_date" },
  ],
};

function onRowDoubleClick(data) {
  onOpenLink("view_lost_and_found_detail", data.name);
}
function onOpenLink(action, name) {
  window.postMessage(action + "|" + name, "*");
}
function onAddNew() {
  if (!gv.cashier_shift?.name) {
    gv.toast("error", "Please Open Cashier Shift.");
    return;
  }
  dialog.open(ComAddLostAndFound, {
    props: {
      header: "Add New Lost and Found ",
      style: {
        width: "50vw",
      },
      modal: true,
      position: "top",
      closeOnEscape: false,
      breakpoints: {
        "960px": "50vw",
        "640px": "100vw",
      },
    },
    onClose: (options) => {
      const result = options.data;
      if (result) {
        loadData();
        window.postMessage("view_lost_and_found_detail|" + result.name, "*");
      }
    },
  });
}
</script>
