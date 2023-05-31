<template lang="">
    <ComReservationStayPanel title="Room Stay">
        <template #content>
            <div class="room-stay-list">
            <DataTable class="p-datatable-sm" :value="reservation_stay?.stays"  tableStyle="min-width: 50rem">
                    <Column field="start_date" header="Arrival"></Column>
                    <Column field="end_date" header="Departure"></Column>
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
            <div class="flex justify-end mt-4">
                <Button >Add Room Charge</Button>
            </div>
            
        </template>
    </ComReservationStayPanel>
</template>
<script setup>
import ComReservationStayPanel from './ComReservationStayPanel.vue';
const props = defineProps({
    reservation_stay: Object
})
</script>
<style scoped>
    .p-datatable > .p-datatable-wrapper {
        border-radius: 0.75rem !important;
    }
</style>