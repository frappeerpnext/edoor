<template>
  <ComDocumentList
    doctype="Room Block"
    list_view_setting="Room_Block_List"
    router_name="RoomBlock"
    title="Room Block List"
    :options="options"
    @row-dblclick="onRowDblclick"
    v-model:selectedRow="selectedRow"
  >
    <template #action-button>
      <Button 
        class="border-none white-space-nowrap"
        :label="$t('Add New Room Block')"
        icon="pi pi-plus"
        @click="onAddNewRoomBlock"
      />
    </template>

    <template #name="{ item }">
      <Button 
        class="p-0 link_line_action1" 
        @click="onOpenLink('view_room_block_detail', item.name)" 
        link
      >
        {{ item.name }}
      </Button>
    </template>

    <template #is_unblock="{ item }">
      <Chip 
        v-if="item.is_unblock == 1" 
        class="text-white surface-400 p-1px px-2"
      >
        <i class="pi pi-lock-open me-2" /> 
        {{ $t('Unblock') }}
      </Chip>
      <Chip 
        v-else-if="item.docstatus == 1 && item.is_unblock == 0" 
        class="text-white bg-black-alpha-90 p-1px px-2"
      >
        <i class="pi pi-lock me-2" /> 
        {{ $t('Block') }}
      </Chip>
      <Chip 
        v-else-if="item.docstatus == 0 && item.is_unblock == 0" 
        class="text-white bg-orange-500 p-1px px-2"
      >
        <i class="pi pi-file-edit me-2" /> 
        {{ $t('Draft') }}
      </Chip>
    </template>
    <template #unblock_date="{ item }">
      <span>{{ formatDate(item.unblock_date) }}</span>
    </template>
  </ComDocumentList>
</template>

<script setup>
import { ref, inject } from 'vue'
import ComDocumentList from "@/components/document/ComDocumentList.vue"
import ComEditRoomBlock from "@/views/room_block/components/ComEditRoomBlock.vue"
import { i18n } from '@/i18n'
import { useDialog } from 'primevue/usedialog'
import Button from 'primevue/button'
import Chip from 'primevue/chip'

const dialog = useDialog()
const { t: $t } = i18n.global
const gv = inject("$gv")
const moment = inject("$moment")
const selectedRow = ref()

const options = ref({
  fields: [
    { fieldname: "name", label: "Room Block Code", fieldtype: "Link" },
    { fieldname: "block_date", label: "Block Date", fieldtype: "Date" },
    { fieldname: "start_date", label: "Start Date", fieldtype: "Date" },
    { fieldname: "end_date", label: "Release Date", fieldtype: "Date" },
    { fieldname: "room_number", label: "Room Number" },
    { fieldname: "room_type", label: "Room Type" },
    { fieldname: "total_night_count", label: "Total Night(s)" },
    { fieldname: "reason", label: "Reason" },
    { fieldname: "unblock_date", label: "Unblock Date", fieldtype:"Date" },
    { fieldname: "unblock_note", label: "Unblock Note" },
    { fieldname: "docstatus", label: "Document Status", fieldtype: "Int",is_hide: true },  
    { fieldname: "is_unblock", label: "Status", fieldtype: "Status" } ,
    { fieldname: "modified_by", label: "Modified By" }, 
    { fieldname: "modified", label: "Last Modified", fieldtype:'Datetime'} 
  ],
  filterOptions: [
    { fieldname: "block_date", fieldtype: "Date" },
    { fieldname: "start_date", fieldtype: "Date" },
    { fieldname: "end_date", fieldtype: "Date" },
    { fieldname: "room_type", fieldtype: "Link", options: "Room Type", optionValue: "label", operator: "like" },
    { fieldname: "room_number", fieldtype: "Link", options: "Room", optionValue: "label", operator: "like" }, 
    { fieldname:  "status"}
  ],
  filters: [['property', '=', window.property_name]],
  contextMenuOptions: [
    {
      label: 'View Details',
      icon: 'pi pi-eye',
      command: () => onRowDblclick({ data: selectedRow.value })
    }
  ]
})

function onRowDblclick(event) {
  if (event) {
    onOpenLink("view_room_block_detail", event.name)
  }
}

function formatDate(date) {
  return date && moment(date).isValid() ? moment(date).format("DD-MM-YYYY") : ''
}

function onOpenLink(action, name) {
  if (name) {
    window.postMessage(`${action}|${name}`, '*')
  }
}

function onAddNewRoomBlock() {
  if (!gv.cashier_shift?.name) {
    gv.toast('error', 'Please Open Cashier Shift.')
    return
  }
  
  dialog.open(ComEditRoomBlock, {
    data: {},
    props: {
      header: $t('Add New Room Block'),
      style: {
        width: '50vw',
      },
      modal: true,
      position: 'top',
      closeOnEscape: false,
      breakpoints: {
        '960px': '50vw',
        '640px': '100vw'
      }
    },
    onClose: (options) => {
      const result = options.data
      if (result) {
        window.postMessage("view_room_block_detail|" + result.name, "*")
        setTimeout(() => {
                    window.postMessage({action:"ComDocumentList"},"*")
                }, 5000);
      }
    }
  })
}
</script>

<style scoped>
.link_line_action1 {
  padding: 0;
  text-align: left;
}

.p-chip {
  margin: 0.25rem;
}
</style>