<template>
  <ComDocumentList
    ref="docListRef"
    doctype="Customer"
    title="Guest Database"
    list_view_setting="guestdatabase_list"
    :options="options"
    router_name="GuestDatabase"
    @row-dblclick="onRowDoubleClick"
  >
    <template #action-button>
      <Button
        class="border-none"
        :label="$t('Add New Guest')"
        icon="pi pi-plus"
        @click="onAddNewGuest()"
      />
    </template>
    <template #name="{ item, index }">
      <Button
        class="link_line_action1"
        @click="onOpenLink('view_guest_detail', item.name)"
        link
      >
        {{ item.name }}
      </Button>
    </template>
    <template #date_of_birth="{ item, index }">
      {{item.date_of_birth ? moment(item.date_of_birth).format("DD-MM-YYYY") : ''}} 
    </template>
  </ComDocumentList>
</template>
<script setup>
import { ref, inject } from "@/plugin";
import ComDocumentList from "@/components/document/ComDocumentList.vue";
import ComAddGuest from "@/views/guest/components/ComAddGuest.vue";
import { useDialog } from "primevue/usedialog";
import { i18n } from "@/i18n";
const { t: $t } = i18n.global;
const moment = inject("$moment")
const docListRef = ref(null);
const gv = inject("$gv");
const dialog = useDialog();
const options = {
  fields: [
    { fieldname: "name", label: "Customer Code", fieldtype: "Data" },
    { fieldname: "customer_name_en", label: "Customer Name" },
    { fieldname: "gender", label: "Gender" },
    { fieldname: "date_of_birth", fieldtype: "Date" },
    { fieldname: "company_name", label: "Company" },
    { fieldname: "country", label: "Country" },
    { fieldname: "customer_group", label: "Guest Type" },
    { fieldname: "phone_number", label: "Phone Number" },
    { fieldname: "email_address", label: "Email" },
    { fieldname: "identity_type", label: "Identity Type" },
    { fieldname: "owner", label: "Created By" },
    { fieldname: "creation", fieldtype: "Datetime", label: "Creation" },
    { fieldname: "modified_by", label: "Modified By" },
    { fieldname: "modified", fieldtype: "Datetime", label: "Last Modified" },
  ],
  filterOptions: [
    { fieldname: "customer_group" },
    { fieldname: "gender" },
    { fieldname: "country" },
  ],
};

function onRowDoubleClick(data) {
  onOpenLink("view_guest_detail", data.name);
}
function onOpenLink(action, name) {
  window.postMessage(action + "|" + name, "*");
}
function onAddNewGuest() {
  if (!gv.cashier_shift?.name) {
    gv.toast("error", "Please Open Cashier Shift.");
    return;
  }

  dialog.open(ComAddGuest, {
    data: {
      // name: name.value,
    },
    props: {
      header: $t(`Add New Guest`),
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
      const data = options.data;
      if (data) {
        loadData();
      }
    },
  });
}
</script>
