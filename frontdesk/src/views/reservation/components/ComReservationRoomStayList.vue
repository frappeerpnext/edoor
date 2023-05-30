<template lang="">
    <ComReservationStayPanel title="Room Stay">
        <template #content>
            <div class="room-stay-list">
            <DataTable :value="reservation_stay?.stays" tableStyle="min-width: 50rem">
                    <Column field="start_date" header="From"></Column>
                    <Column field="end_date" header="To"></Column>
                    <Column field="room_type" header="Room Type"></Column>
                    <Column field="room_number" header="Room Number"></Column>
            </DataTable>
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
    .room-stay-list .p-datatable-wrapper{
        border-radius: 0.75rem;
    }
</style>