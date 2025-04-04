<template>
  <ComDocumentList 
  doctype="Folio Transaction" 
  list_view_setting="foliotransaction_list"
  :options="options"
   router_name="FolioTransaction"
   @row-dblclick="onRowDoubleClick"
   >
      <template #name="{ item, index }">
          <Button   class="link_line_action1"
                              @click="onOpenLink('view_folio_transaction_detail',item.name)" link>
                              {{ item.name }}
                              
                          </Button> 
      </template>
      <template #reservation="{ item, index }">
          <Button   class="link_line_action1"
                              @click="onOpenLink('view_reservation_detail',item.reservation)" link>
                              {{ item.reservation }}
                              
                          </Button> 
      </template>
      <template #reservation_stay="{ item, index }">
          <Button   class="link_line_action1"
                              @click="onOpenLink('view_reservation_stay_detail',item.reservation_stay)" link>
                              {{ item.reservation_stay }}
                              
                          </Button> 
      </template>
      <template #transaction_number="{ item, index }">
          <Button   class="link_line_action1"
                              @click="onOpenLink('view_folio_detail',item.transaction_number)" link>
                              {{ item.transaction_number }}
                              
                          </Button> 
      </template>
      <template #guest="{ item, index }">
         <Button   class="link_line_action1"
                              @click="onOpenLink('view_guest_detail',item.guest)" link>
                              {{ item.guest }} {{ item.guest_name }}
                              
                          </Button> 
      </template>
      <template #account_code="{ item, index }">
                              {{ item.account_code }}-{{ item.account_name }}
      </template>
  </ComDocumentList>
</template>
<script setup>
import ComDocumentList from "@/components/document/ComDocumentList.vue"
  const options  ={
     fields:[
          { "fieldname": "name",label:"Folio Transaction", fieldtype:"Data" },
          { "fieldname": "reservation",label:"Reservation #"},
          { "fieldname": "reservation_stay",label:"Stay #" },
          { "fieldname": "transaction_number",label:"Folio #" },
          { "fieldname": "room_number", label: "Rooms" },
          { "fieldname": "guest",label:"Guest"},
          { "fieldname": "guest_name",is_hide:true},
          { "fieldname": "account_code", label:"Account Code"},
          { "fieldname": "account_name",is_hide:true},
          { "fieldname": "amount"},
          { "fieldname": "discount"},
          { "fieldname": "total_tax"},
          { "fieldname": "bank_fee"},
          { "fieldname": "total_amount"},
          { "fieldname": "modified_by", fieldtype:"Data", label:"Modified By"},
          { "fieldname": "modified", fieldtype:"Datetime", label: "Last Modified"},
      ]
,
    //  filterOptions:[
    //   {
    //      fieldname:"guest",
    //   },
    //   {
    //       fieldname:"status",
    //   },
    //   {
    //       fieldname:"room_type",
    //   },
    //   {
    //       fieldname:"room_number",
    //   },
    //   {
    //       fieldname:"posting_date",
    //   },

    //  ],
     settingMenus: [

      {
          label: 'Refresh',
          icon: 'pi pi-refresh'
      },
      {
          label: 'Export',
          icon: 'pi pi-upload'
      }

  ],
  }

  function onRowDoubleClick(data){
      onOpenLink("view_desk_folio_detail",data.name)
  }
  function onOpenLink(action,name){
      window.postMessage(action + '|' +name,'*')
  }
</script>