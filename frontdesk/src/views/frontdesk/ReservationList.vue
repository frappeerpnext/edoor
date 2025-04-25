<template>
    <ComDocumentList ref="reservationList" doctype="Reservation" list_view_setting="reservation_list" :options="options"
        router_name="ReservationList" @row-dblclick="onRowDoubleClick" v-model:selectedRow="selectedRow"
        @onBeforeContextMenuShow="onContextMenuBeforeShow"
        >
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
import { ref,getDocumentList } from "@/plugin"
import ComDocumentList from "@/components/document/ComDocumentList.vue"
import NewFITReservationButton from "@/views/reservation/components/NewFITReservationButton.vue"
import NewGITReservationButton from "@/views/reservation/components/NewGITReservationButton.vue"
import ComReservationListContextMenuHeader from "@/views/frontdesk/components/ComReservationListContextMenuHeader.vue"
const reservationList = ref(null)
const selectedRow = ref()

const options = ref({
    fields: [
        { "fieldname": "name", label: "Res. #", fieldtype: "Data" },
        { "fieldname": "reference_number", label: "Ref. #" },
        { "fieldname": "reservation_type", is_hide: true },
        { "fieldname": "guest_name" },
        { "fieldname": "guest", is_hide: true },
        { "fieldname": "business_source" },
 
        { "fieldname": "reservation_date" },
        { "fieldname": "arrival_date" },
        { "fieldname": "departure_date" },
        { "fieldname": "total_active_reservation_stay",label:"Total Stays" },

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
    contextMenuOptions: [
        {label: 'General Info', is_header:true,header_component:ComReservationListContextMenuHeader,header_prop:selectedRow.value },
        {
            label: 'View Reservation Detail', icon: 'pi pi-calendar', command: () => {
                window.onOpenLink("view_reservation_detail", selectedRow.value.name);
            }
        },
        {
            label: 'View Guest Detail', icon: 'pi pi-id-card', command: () => {
                window.onOpenLink("view_guest_detail", selectedRow.value.guest);
            }
        },
    ]
})

function onRowDoubleClick(data) {
    onOpenLink("view_reservation_detail", data.name)
}

function onOpenLink(action, name) {
    window.postMessage(action + '|' + name, '*')
}

async function onContextMenuBeforeShow(){

    const menus = []
    const folioMenu =await getFolioMenu()

    if(folioMenu){
        menus.push(folioMenu)
    }
    const reservationStayMenu =await getReservationStayMenu()
    if(reservationStayMenu ) menus.push(reservationStayMenu)

 
    reservationList.value.addContextMenu(menus);
}

async function getFolioMenu(){
    const folios = await getDocumentList("Reservation Folio", {filters:[["reservation","=",selectedRow.value.name]]})
    if(folios.data){

        const folioMenu = {
                label: 'Guest Folio', icon: 'pi pi-file', 
                is_dynamic:true,
                badge: folios.data.length,
                items:[]
             
            }
          
        folios.data.forEach(f=>{
            folioMenu.items.push(
                {
                label: f.name,
                command: () => {
                    window.onOpenLink("view_reservation_folio_detail", f.name);
                }

            },
            )
        })
        
        return folioMenu;
    }
return null
}

async function getReservationStayMenu(){
    const res = await getDocumentList("Reservation Stay", {fields:["name","rooms","room_type_alias","reservation_status"],filters:[["reservation","=",selectedRow.value.name]]})
    if(res.data){

        const menu = {
                label: 'Reservation Stay', icon: 'pi pi-building', 
                is_dynamic:true,
                badge: res.data.length,
                items:[]
             
            }
          
            res.data.forEach(f=>{
            menu.items.push(
                {
                label: `${f.name} - ${f.room_type_alias} (${f.reservation_status})`,
                command: () => {
                    window.onOpenLink("view_reservation_stay_detail", f.name);
                }

            },
            )
        })
        
        return menu;
    }
return null
}
</script>