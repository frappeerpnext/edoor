<template>
  <ComDocumentList
      doctype="Room Block"
      list_view_setting="Room_Block_List"
      router_name="RoomBlock"
      :options= "options"
      @row-dblclick="onRowDblclick"
      v-model:selectedRow="selectedRow"
  >
      <template #action-button>
        <Button class="border-none" @click="onAddNewRommBlock()"> {{ $t('Add New Room Block') }} </Button>
      </template>  

      <!-- <template #room_number="{ item, index }">
         {{ item.room_number }} {{ item.room_type }}
      </template>
      <template #status="{ item, index }">
         <ComStatus :status="item.status"/>
      </template>
      <template #name="{item, index}" >
          <button class="link_line_action1" @click="onOpenLink('view_deposit_ledger_detail', item.name)" link>
              {{ item.name }}
          </button>
      </template> -->


      <template #name="{item, index}" >
          <button class="link_line_action1" @click="onOpenLink('view_room_block_detail', item.name)" link>
              {{ item.name }}
          </button>
      </template>
      


  </ComDocumentList>

</template>

<script setup> 
import {ref, inject} from "@/plugin"
import ComDocumentList from "@/components/document/ComDocumentList.vue"  
import ComEditRoomBlock from "@/views/room_block/components/ComEditRoomBlock.vue"; 
import {i18n} from '@/i18n';
import { useDialog } from 'primevue/usedialog';



const dialog = useDialog()
const { t: $t } = i18n.global;
const gv = inject("$gv")


const options = {
  fields:[
      {fieldname: "name" , label: "Room Block Code"},
      {fieldname: "block_date" , label: "Block Date"},
      {fieldname: "start_date" , label: "Start Date"},
      {fieldname: "end_date" , label: "Release Date"},
      {fieldname: "room_number", label: "Room Number"},
      {fieldname: "room_type", label: "Room Type"},
      {fieldname: "total_night_count" , label: "Total Night(s)"},
      {fieldname: "reason" , label: "Reason", default:true},   
      {fieldname: "unblock_note" , label: "Unblock Note"},     
      {fieldname: "unblock_date" , label: "Unblock Date", fieldtype:"Date"},
      { fieldname: 'is_unblock',extra_field:'docstatus', fieldtype: "Status", label: 'Status' },

      // {fieldname: "status" , label: "Status"}     

  ],
  // filterOptions: [
  //     { fieldname: "guest" },
  //     { fieldname: "posting_date" },
  //     { fieldname: "room_type",fieldtype:'Link',options:"Room Type",optionValue:"label",operator:"like" },
  //     { fieldname: "room_number",fieldtype:'Link',options:"Room",optionValue:"label",operator:"like" }, 
  //     { fieldname: "status" }, 
  // ], 
  filters:[['property','=',window.property_name]],
}

const selectedRow = ref()

function onRowDblclick(event) {

  onOpenLink("view_room_block_detail", event.name)
}


function onOpenLink(action, name) {
  window.postMessage(action + '|' + name, '*')
} 

function loadData(show_loading=true) {
   
   gv.loading = show_loading
   let filters = [
     ["property", "=", property.name]
   ]
   if (filter.value?.keyword) {
     filters.push(["keyword", 'like', '%' + filter.value.keyword + '%'])
   }
   if(filter.value.block_status){
     if(filter.value.block_status == 'Draft'){
       filters.push(["docstatus","=",0])
       filters.push(["is_unblock","=",0])
     }
     else if(filter.value.block_status == 'Blocked'){
       filters.push(["docstatus","=",1])
       filters.push(["is_unblock","=",0])
     }
     else if(filter.value.block_status == 'Unblocked'){
       filters.push(["is_unblock","=",1])
     }
   }
   if (filter.value?.selected_room_id) {
     filters.push(["room_id", '=', filter.value.selected_room_id])
   }
   if (filter.value?.selected_room_type) {
     filters.push(["room_type_id", '=', filter.value.selected_room_type])
   }
   if (filter.value?.search_date_type && filter.value.date_range != null) {
 
     filters.push([filter.value.search_date_type, '>=', dateRange.start])
     filters.push([filter.value.search_date_type, '<=', dateRange.end])
   }
   let fields = [...columns.value.map(r => r.fieldname), ...columns.value.map(r => r.extra_field)]
   fields = [...fields, ...selectedColumns.value]
   fields = [...new Set(fields.filter(x => x))]
 
   getDocList('Room Block', {
     fields: fields,
     orderBy: {
       field: '`tabRoom Block`.' + pageState.value.order_by,
       order: pageState.value.order_type,
     },
     filters: filters,
     limit_start: ((pageState.value?.page || 0) * (pageState.value?.rows || 20)),
     limit: pageState.value?.rows || 20,
   })
     .then((doc) => {
       data.value = doc
       gv.loading = false
     })
     .catch((error) => {
       gv.loading = false
 
     });
 
   getTotalRecord(filters)
 
   localStorage.setItem("page_state_room_block", JSON.stringify(pageState.value))
 
 }

function onAddNewRommBlock(room_block) {
  if(!gv.cashier_shift?.name){
        gv.toast('error', 'Please Open Cashier Shift.')
        return
    }
  dialog.open(ComEditRoomBlock, {
    data: { name: room_block },
    props: {
      header: 'Add New Room Block ',
      style: {
        width: '50vw',
      },
      modal: true,
      position: 'top',
      closeOnEscape: false,
      breakpoints:{
                '960px': '50vw',
                '640px': '100vw'
            },
    },
    onClose: (options) => {
      const result = options.data;
      if (result) {
        loadData()
        window.postMessage("view_room_block_detail|" + result.name, "*")
      }
    }
  })
}

</script>

