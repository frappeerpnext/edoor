<template>
    <ComDocumentList doctype="Reservation Folio" list_view_setting="guest_folio_reservation_folio"
        router_name="GuestFolio" title="Guest Folios" :options="options"
         @row-dblclick="onRowDblclick"
        >
       

        <template #status="{ item, index }">
            <ComStatus :status="item.status" />
        </template>
    </ComDocumentList>
</template>
<script setup>

import { ref } from "@/plugin"
import ComDocumentList from "@/components/document/ComDocumentList.vue"

import { i18n } from '@/i18n';
import { useDialog } from 'primevue/usedialog';

const dialog = useDialog()
const { t: $t } = i18n.global;
const options = {
    fields: [
        { fieldname: "name", label: "Folio #", action:"view_reservation_folio_detail" },
        { fieldname: "posting_date", label: "Date" },
        { fieldname: "reservation_stay", label: "Stay #",action:"view_reservation_stay_detail" },
        { fieldname: "rooms", label: "Room" },
        { fieldname: "room_types", label: "Room Type" },
        { fieldname: "guest_name", label: "Guest",action:"view_guest_detail",id_field:"guest" },
        { fieldname: "guest", is_hide: true },
        { fieldname: "total_debit" },
        { fieldname: "total_credit" },
        { fieldname: "balance" },
        { fieldname: "modified_by",label:"Modified By" },
        { fieldname: "modified", fieldtype: "Datetime",label:"Last Modified" },
        { fieldname: "status" },
        { fieldname: "mark_as_verified"},
    ],
    filterOptions:[
        {fieldname:"posting_date"},
        { fieldname: "room_types", fieldtype: 'Link', options: 'Room Type', operator: "like", optionValue: 'label' },
        { fieldname: "rooms", fieldtype: 'Link', options: 'Room', operator: "like", optionValue: 'label' },
        { fieldname: "guest"},
        { fieldname: "reservation"},
        { fieldname: "reservation_stay"},
        { fieldname: "business_source"},
        { fieldname: "status"},
        { fieldname: "mark_as_verified"},
    ]
}



function onRowDblclick(event) {

    onOpenLink("view_reservation_folio_detail", event.name)
}


function onOpenLink(action, name) {
    window.postMessage(action + '|' + name, '*')
}


</script>