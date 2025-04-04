<template>
     
    <ComDocumentList doctype="Reservation Stay" 
    list_view_setting="reservation_stay_list"
        router_name="ReservationStayList" :options="options" @row-dblclick="onRowDblclick"
        v-model:selectedRow="selectedRow"
        >
        <template #action-button>


            <NewFITReservationButton />
            <NewGITReservationButton />

        </template>
        <template #name="{ item, index }">
            <Button class="link_line_action1" @click="onOpenLink('view_reservation_stay_detail', item.name)" link>
                {{ item.name }}

            </Button>
        </template>
        <template #reservation="{ item, index }">
            <Button class="link_line_action1" @click="onOpenLink('view_reservation_detail', item.reservation)" link>
                {{ item.reservation }}

            </Button>
        </template>
        <template #guest_name="{ item, index }">
            <Button class="link_line_action1" @click="onOpenLink('view_guest_detail', item.guest)" link>
                {{ item.guest_name }}

            </Button>
        </template>


    </ComDocumentList>
</template>
<script setup>
import ComDocumentList from "@/components/document/ComDocumentList.vue"
import NewFITReservationButton from "@/views/reservation/components/NewFITReservationButton.vue"
import NewGITReservationButton from "@/views/reservation/components/NewGITReservationButton.vue"
const options = {
    fields: [
        { fieldname: "name", label: "Stay. #" },
        { fieldname: "reservation", label: "Res. #" },
        { fieldname: "reservation_type", label: "Res. Type" },
        { fieldname: "guest", label: "guest", is_hide: true },
        { fieldname: "guest_name", label: "Guest" },
        { fieldname: "reservation_date", label: "Res. Date" },
        { fieldname: "arrival_date", label: "Arrival" },
        { fieldname: "departure_date", label: "Departure" },
        { fieldname: "room_nights", label: "Nights" },
        { fieldname: "room_type_alias", label: "Room Type" },
        { fieldname: "reservation_status", label: "Status" },
        { fieldname: "rooms", label: "Rooms" },
        { fieldname: "modified", label: "Last Modified", fieldtype: "Datetime" }

    ],
    filterOptions: [
        { fieldname: "reservation_date" },
        { fieldname: "arrival_date" },
        { fieldname: "departure_date" },
        { fieldname: "business_source" },
        { fieldname: "reservation_status" }
    ],
    filters:[['property','=',window.property_name]],
}

const selectedRow = ref()

function onRowDblclick(event) {

    onOpenLink("view_reservation_stay_detail", event.name)
}


function onOpenLink(action, name) {
    window.postMessage(action + '|' + name, '*')
}

</script>