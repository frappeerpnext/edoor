<template>

    <ComDocumentList doctype="Reservation Stay" 
    list_view_setting="operation_dashboard_daily_reservation" 
    router_name ="DailyReservation"
    title="Daily Reservation"
    :options="options"
    >

       
    <template #arrival_date="{ item, index }">
        {{item.arrival_date}}
    </template>
    <template #reservation_status="{ item, index }">
        <ComReservationStatus :statusName="item.reservation_status" />
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
        {fieldname:"reservation", label:"Reservation #",action:"view_reservation_detail"},
        {fieldname:"name", label:"Stay #",action:"view_reservation_stay_detail"},
        {fieldname:"reference_number", label:"Ref #"},
        {fieldname:"group_code", label:"Group Code"},
        {fieldname:"reservation_date", label:"Res. Date"},
        {fieldname:"arrival_date"},
        {fieldname:"departure_date"},
        {fieldname:"room_nights", label:"Nights"},
        {fieldname:"rooms", label:"Room #"},
        {fieldname:"guest_name", label:"Guest"},
        {fieldname:"business_source"},
        {fieldname:"adr"},
        {fieldname:"total_room_rate"},
        {fieldname:"reservation_status"},

        

    ],
    filterOptions:[
        {fieldname:"guest"},
        {fieldname:"business_source"},
        { fieldname: "room_types", fieldtype: 'Link', options: 'Room Type', operator: "like", optionValue: 'label' },
        { fieldname: "rooms", fieldtype: 'Link', options: 'Room', operator: "like", optionValue: 'label',label:"Room" },

    ],
    filters:[
        ["property","=",window.property_name],
        // ["status","=",'Open'],
    ],
    hideHeader:true,
    hideSaveView:true,
    scrollHeight: "800px"
    
}

function onOpenLink(action, name) {
    window.postMessage(action + '|' + name, '*')
}

</script>