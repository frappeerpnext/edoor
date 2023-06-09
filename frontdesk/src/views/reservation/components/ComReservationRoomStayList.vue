<template lang="">
    <ComReservationStayPanel title="Room Stay">
        <template #content>
            <div class="room-stay-list text-center">
            <DataTable class="p-datatable-sm" :value="rs.reservationStay?.stays"  tableStyle="min-width: 50rem">
                    <Column field="start_date" header="Stay Date" >
                        <template #body="{ data }">
                            {{ moment(data.start_date).format('DD-MM-yyyy') }} to {{ moment(data.end_date).format('DD-MM-yyyy') }}
                        </template>
                    </Column>
                   
                    <Column field="room_nights" header="Nights"></Column>
                    <Column field="room_type" header="Room Type"></Column>
                    <Column field="room_number" header="Room Name"></Column>
                    <Column  header="">
                        <template #body="slotProps" class="flex justify-end h-full" >
                            <div class="text-end">
                                <Button icon="pi pi-ellipsis-h" class="w-2rem h-2rem " text rounded aria-label="Filter" />
                            </div>
                        </template>
                    </Column>
            </DataTable>
            </div>
            <div class="flex justify-end mt-3">
                <Button class="border-none" ><ComIcon icon="iconBed" class="me-2" /> Upgrade Room</Button>
            </div>
            
        </template>
    </ComReservationStayPanel>
</template>
<script setup>
import ComReservationStayPanel from './ComReservationStayPanel.vue';
import {inject} from 'vue'
const moment = inject('$moment')
const rs = inject("$reservation_stay")
</script>
<style scoped>
    .p-datatable > .p-datatable-wrapper {
        border-radius: 0.75rem !important;
    }
</style>