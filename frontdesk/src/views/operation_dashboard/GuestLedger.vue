<template>

    <ComDocumentList doctype="Reservation Folio" 
    list_view_setting="operation_dashboard_guest_ledger_reservation_folio" 
    router_name ="GuestLedger"
    title="Guest Ledger"
    :options="options"
    >

       

    <template #rooms="{ item, index }">
            {{ item.rooms }} - {{ item.room_types_alias }}
        </template>
        
    <template #status="{ item, index }">
            <ComStatus :status="item.status" />
        </template>
    <template #reservation_status="{ item, index }">
            <ComReservationStatus :statusName="item.reservation_status" />
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
import {ref,useRoute} from "@/plugin"
import ComDocumentList from "@/components/document/ComDocumentList.vue" 


import {i18n} from '@/i18n';
import { useDialog } from 'primevue/usedialog';
import { inject } from "vue";


const dialog = useDialog()
const { t: $t } = i18n.global;
const working_date = window.current_working_date;
const op = inject("$operation_dashboard");
const route = useRoute()
op.page_title = route.meta.title;
op.current_route = route.name;


const options = {
    fields:[
        {fieldname:"name", label:"Folio #",action:"view_reservation_folio_detail"},
        {fieldname:"posting_date", label:"Date"},
        {fieldname:"reservation", label:"Res. #",action:"view_reservation_detail"},
        {fieldname:"reservation_stay", label:"Stay #",action:"view_reservation_stay_detail"},
        {fieldname:"business_source"},
        {fieldname:"rooms"},
        {fieldname:"room_types_alias", is_hide:true},
        {fieldname:"guest", is_hide:true},
        {fieldname:"guest_name", action:"view_guest_detail",id_field:"guest"},
        {fieldname:"total_debit"},
        {fieldname:"total_credit"},
        {fieldname:"balance"},
        {fieldname:"status"},
        {fieldname:"reservation_status"},
        {fieldname:"modified_by", label:"Modified By"},
        {fieldname:"modified",label:"Last Modified",fieldtype:'Datetime'},

        

    ],
    filterOptions:[
        {fieldname:"guest"},
        {fieldname:"business_source"},
        { fieldname: "room_types", fieldtype: 'Link', options: 'Room Type', operator: "like", optionValue: 'label' },
        { fieldname: "rooms", fieldtype: 'Link', options: 'Room', operator: "like", optionValue: 'label',label:"Room" },

    ],
    filters:[
        ["property","=",window.property_name],
        ["status","=",'Open'],
    ],
    hideHeader:true,
    hideSaveView:true,
    scrollHeight: "800px"
    
}

function onOpenLink(action, name) {
    window.postMessage(action + '|' + name, '*')
}

</script>