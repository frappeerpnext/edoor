<template>
     
    <ComDocumentList doctype="Reservation Stay" 
    :title="$t('Unassign Rooms')"
    list_view_setting="reservation_stay_unassign_room_list"
        router_name="UnAssignRoomList" 
        :options="options" @row-dblclick="onRowDblclick"
        v-model:selectedRow="selectedRow"
        >
        <template #action-button>


            <NewFITReservationButton />
            <NewGITReservationButton />

        </template>
        
        <template #room_types="{ item, index }">
           
            {{ item.room_type_alias }}
        </template>
        
        <template #rooms="{ item, index }">
            <div v-tippy="item.rooms" v-if="item && item?.rooms">
                <div class="inline-block">
                    <roomIDDisplay :item="item.rooms.split(',')" />
                </div>
            </div>
            <div @click="onAssignRoom(item.rooms_data,item.name)" class="link_line_action w-auto" v-else>
                <i class="pi pi-pencil"></i>
                {{ $t('Assign Room') }}

            </div>
        </template>

        <template #reservation_status="{ item, index }">
             
                <ComReservationStatus :statusName="item.reservation_status" />
        </template>


    </ComDocumentList>
</template>
<script setup>
import {ref} from "@/plugin"
import ComDocumentList from "@/components/document/ComDocumentList.vue"
import NewFITReservationButton from "@/views/reservation/components/NewFITReservationButton.vue"
import NewGITReservationButton from "@/views/reservation/components/NewGITReservationButton.vue"
import ComReservationStatus from "@/components/label/ComReservationStatus.vue"
const options = {
    fields: [
        { fieldname: "name", label: "Stay. #",action:"view_reservation_stay_detail" },
        { fieldname: "reservation", label: "Res. #",action:"view_reservation_detail" },
        { fieldname: "reservation_type", label: "Res. Type" },
        { fieldname: "guest", label: "guest", is_hide: true },
        { fieldname: "guest_name", label: "Guest",action:"view_guest_detail",id_field:"guest" },
        { fieldname: "reservation_date", label: "Res. Date" },
        { fieldname: "arrival_date", label: "Arrival" },
        { fieldname: "departure_date", label: "Departure" },
        { fieldname: "room_nights", label: "Nights" },
        { fieldname: "room_types", label: "Room Type" },
        { fieldname: "room_type_alias", is_hide:true },
        { fieldname: "rooms", label: "Rooms" },
        { fieldname: "adr", label: "ADR" },
        { fieldname: "total_amount", label: "Charge" },
        { fieldname: "reservation_status", label: "Status" },
        { fieldname: "modified", label: "Last Modified", fieldtype: "Datetime" },
        { fieldname: "rooms_data", is_hide:true }

    ],
    filterOptions: [
        { fieldname: "reservation_date" },
        { fieldname: "arrival_date" },
        { fieldname: "departure_date" },
        { fieldname: "room_types", fieldtype: 'Link', options: 'Room Type', operator: "like", optionValue: 'label' },
        { fieldname: "business_source" },
        
    ],
    filters:[['property','=',window.property_name],["reservation_status","=","Confirmed"]],
}

const selectedRow = ref()

function onRowDblclick(event) {

    onOpenLink("view_reservation_stay_detail", event.name)
}


function onOpenLink(action, name) {
    window.postMessage(action + '|' + name, '*')
}

function onAssignRoom(room_name, reservation_stay){
    window.postMessage('assign_room|' + reservation_stay + '|' + JSON.parse(room_name)[0].name, '*')
}

</script>