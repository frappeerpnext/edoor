<template>
    {{ selectedRow }}
    <ComDocumentList doctype="Reservation" list_view_setting="reservation_list" :options="options"
        router_name="ReservationList" @row-dblclick="onRowDoubleClick">
        <template #action-button>


            <NewFITReservationButton />
            <NewGITReservationButton />

        </template>
        <template #name="{ item, index }">
            <Button class="link_line_action1" @click="onOpenLink('view_reservation_detail', item.name)" link>
                {{ item.name }}

            </Button>
        </template>
        <template #guest_name="{ item, index }">
            <Button class="link_line_action1" @click="onOpenLink('view_guest_detail', item.guest)" link>
                {{ item.guest_name }}

            </Button>
        </template>

        <template #reservation_type="{ item, index }">
            {{ item.reservation_type }}
        </template>
        
    </ComDocumentList>
</template>
<script setup>
import {ref} from "@/plugin"
import ComDocumentList from "@/components/document/ComDocumentList.vue"
import NewFITReservationButton from "@/views/reservation/components/NewFITReservationButton.vue"
import NewGITReservationButton from "@/views/reservation/components/NewGITReservationButton.vue"
const selectedRow = ref()
const options = {
    fields: [
        { "fieldname": "name", label: "Res. #", fieldtype: "Data" },
        { "fieldname": "reservation_type", is_hide: true },
        { "fieldname": "guest_name" },
        { "fieldname": "guest" ,is_hide:true},
        { "fieldname": "business_source" },
        { "fieldname": "adr" },
        { "fieldname": "reservation_date" },
        { "fieldname": "arrival_date" },
        { "fieldname": "departure_date" },
        { "fieldname": "adr" },
        { "fieldname": "total_amount" },
        { "fieldname": "modified_by", fieldtype: "Data", label: "Modified" },
        
        { "fieldname": "modified", fieldtype: "Datetime", label: "Last Modified" }
    ]
    ,
    filterOptions: [
        { fieldname: "reservation_date", label: "Reservation Date" },
        { fieldname: "arrival_date", label: "Arrival" },
        { fieldname: "departure_date", label: "Departure" },
        { fieldname: "business_source" },
        { fieldname: "room_types", fieldtype: 'Link', options: 'Room Type', operator: "like", optionValue: 'label' },
        {
            fieldname: "guest",
        }

    ],
    filters: [['property', '=', window.property_name]],
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
    // contextMenuOptions: [
    //     { label: 'View Reservation Detail', icon: 'pi pi-fw pi-search', command: () => alert(selectedRow.value.name) },
    //     // { label: 'Delete', icon: 'pi pi-fw pi-times', command: () => alert("Delete") }
    // ]
}

function onRowDoubleClick(data) {
    onOpenLink("view_reservation_detail", data.name)
}
function onOpenLink(action, name) {
    window.postMessage(action + '|' + name, '*')
}
</script>