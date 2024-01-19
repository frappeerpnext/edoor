<template>
    <DataTable :value="data"  paginator :rows="20" :rowsPerPageOptions="[5, 10, 20, 50]">
        <Column header="No" headerClass="text-center" bodyClass="text-center">
            <template #body="slotProps">
                {{ data.indexOf(slotProps.data) + 1 }}
            </template>
        </Column>
        <Column field="reservation" header="Reservation #" headerClass="text-center" bodyClass="text-center">
            <template #body="slotProps">
                <Button class="p-0 link_line_action1"
                    @click="onViewDetail('view_reservation_detail', slotProps.data.reservation)" link>
                    {{ slotProps.data.reservation }}
                </Button>
            </template>
        </Column>


        <Column field="reservation_stay" header="Stay #" headerClass="text-center" bodyClass="text-center">
            <template #body="slotProps">
                <Button class="p-0 link_line_action1"
                    @click="onViewDetail('view_reservation_stay_detail', slotProps.data.name)" link>
                    {{ slotProps.data.reservation }}
                </Button>
            </template>
        </Column>
        <Column field="reference_number" header="Ref #" headerClass="text-center" headerStyle="min-width:100px;" bodyClass="text-center" />
        <Column header="Pax(A/C)" headerClass="text-center" bodyClass="text-center">
            <template #body="slotProps">
                {{ slotProps.data.adult }} / {{ slotProps.data.child }}

            </template>

        </Column>
        <Column field="reservation_type" header="Type" headerClass="text-center" bodyClass="text-center" />
        <Column header="Stay Date" headerClass="text-center" bodyClass="text-center">
            <template #body="slotProps">
                {{ moment(slotProps.data.arrival_date).format("DD-MM-YYYY") }} to {{
                    moment(slotProps.data.departure_date).format("DD-MM-YYYY") }}

            </template>

        </Column>
        <Column header="Rooms" headerClass="text-center" bodyClass="text-center">
            <template #body="slotProps">
                {{ slotProps.data.room_type_alias }} 
                <span v-if="slotProps.data.rooms">/ {{ slotProps.data.rooms }}</span>
            </template>

        </Column>
        <Column field="guest" header="Guest">
            <template #body="slotProps">
                <Button class="p-0 link_line_action1"
                    @click="onViewDetail('view_guest_detail', slotProps.data.guest)" link>
                    {{ slotProps.data.guest }} - {{ slotProps.data.guest_name }}
                </Button>

            </template>
        </Column>
        
        <Column field="business_source" header="Source"/>
        <Column header="Time" headerClass="text-center" bodyClass="text-center">
            <template #body="slotProps">
                <span v-if="slotProps.data.time">
                    {{ slotProps.data.time.split(":")[0] }} : 
                    {{ slotProps.data.time.split(":")[1] }} 
                </span>
                
            </template>

        </Column>
        <Column field="mode" header="Mode"/>
        <Column field="flight_number" header="Flight #" headerStyle="min-width:100px;"/>
        <Column field="location" header="Location"/>
        <Column field="driver_name" header="Driver"/>
        <Column field="driver_phone_number" header="Phone #"/>
        <Column header="Type" headerClass="text-center" bodyClass="text-center">
            <template #body="slotProps">
                {{ slotProps.data.type }}
            </template>
        </Column>
        <Column field="note" header="Note"/>
        
    </DataTable>
</template>
<script setup>
import { inject } from '@/plugin';
const moment = inject("$moment")
const props = defineProps({
    data: Object
})
function onViewDetail(action, name) {

    window.postMessage(action + "|" + name, "*")
}    
</script>