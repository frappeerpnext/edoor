<template lang="">
    {{rs.reservationStays}}
    <ComReservationStayPanel title="Reservation Room List">
        <template #content>
            <div class="flex justify-end">
                <div>
                    <ComBoxStayInformation valueClass="border-1">
                        <span class="bg-gray-edoor rounded-xl px-2 mr-1">No Show</span> 
                        <span class="bg-gray-edoor rounded-xl px-2 mr-1">In house</span>
                        <span class="bg-gray-edoor rounded-xl px-2">Canceled</span>
                    </ComBoxStayInformation>
                </div>
            </div>
            <div class="room-stay-list text-center mt-4">
                <DataTable class="p-datatable-sm" :value="rs.reservationStays" dataKey="id" tableStyle="min-width: 50rem">
                    <Column selectionMode="multiple" headerStyle="width: 3rem"></Column>
                    <Column field="arrival_date" header="Arrival"></Column>
                    <Column field="departure_date" header="Departure"></Column>
                    <Column field="room_types" header="Room Type"></Column>
                    <Column field="rooms" header="Room"></Column>
                    <Column field="guest_name" header="Guest Name"></Column>
                    <Column field="pax" header="Pax"></Column>
                    <Column field="total_charge" header="Total Charge"></Column>
                    <Column field="paid" header="Paid"></Column>
                    <Column field="balance" header="Balance"></Column>
                    <Column field="reservation_status" header="Status"></Column>
                </DataTable>
            </div>
        </template>
    </ComReservationStayPanel>
</template>
<script setup>
import {inject} from '@/plugin'
import ComReservationStayPanel from '@/views/reservation/components/ComReservationStayPanel.vue';
import ComBoxStayInformation from '@/views/reservation/components/ComBoxStayInformation.vue';

const moment = inject('$moment')
const rs = inject("$reservation")

</script>
<style scoped>
    .p-datatable > .p-datatable-wrapper {
        border-radius: 0.75rem !important;
    }
</style>