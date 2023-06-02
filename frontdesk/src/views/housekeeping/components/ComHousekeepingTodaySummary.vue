<template>
    <div class="td_guest_cs px-1">
        <ComTodaySummarySep title="All Rooms">{{ data?.total_room }}</ComTodaySummarySep>
        <ComTodaySummarySep title="Arrival" :totalValue="data.arrival + data.arrival_remaining" :value="data.arrival">
            <span title="Checked-in">{{ data?.arrival }}</span>/<span title="Remain check-in">{{ data?.arrival_remaining
            }}</span>
        </ComTodaySummarySep>
        <ComTodaySummarySep title="Departure" :totalValue="data.departure + data.departure_remaining"
            :value="data.departure">
            <span title="Departure">{{ data.departure }}</span>/<span titel="Departure Remain">{{ data?.departure_remaining
            }}</span>
        </ComTodaySummarySep>
        <ComTodaySummarySep title="Unassign Room">{{ data?.unassign_room }}</ComTodaySummarySep>
        <ComTodaySummarySep title="Pickup">{{ data?.pick_up }}</ComTodaySummarySep>
        <ComTodaySummarySep title="Drop Off">{{ data?.drop_off }}</ComTodaySummarySep>
    </div>
</template>
<script setup>
import { ref, inject } from "@/plugin"
import ComTodaySummarySep from '@/views/frontdesk/components/ComTodaySummarySep.vue';

const frappe = inject("$frappe")
const call = frappe.call()
const data = ref([])
const working_day = JSON.parse(localStorage.getItem("edoor_working_day"))

call.get('edoor.api.frontdesk.get_dashboard_data', {
    property: JSON.parse(localStorage.getItem("edoor_property")).name,
    date: working_day.date_working_day
}).then((result) => {
    data.value = result.message
})
</script>