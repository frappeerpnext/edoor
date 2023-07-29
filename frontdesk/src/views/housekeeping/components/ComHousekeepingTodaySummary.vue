<template>
    <div class="td_guest_cs px-1 cursor-pointer">
    <ComTodaySummarySep dialogKey="all_rooms" title="All Rooms">{{ data?.total_room }}</ComTodaySummarySep>
        <ComTodaySummarySep :isHousekeeping="isHousekeeping"  dialogKey="arrival" title="Arrival" :totalValue="data.arrival + data.arrival_remaining" :value="data.arrival">
            <span title="Checked-in">{{ data?.arrival }}</span>/<span title="Remain check-in">{{ data?.arrival_remaining
            }}</span>
        </ComTodaySummarySep>
        <ComTodaySummarySep :isHousekeeping="isHousekeeping" dialogKey="departure" title="Departure" :totalValue="data.departure + data.departure_remaining"
            :value="data.departure">
            <span title="Departure">{{ data.departure }}</span>/<span titel="Departure Remain">{{ data?.departure_remaining
            }}</span>
        </ComTodaySummarySep>
        <ComTodaySummarySep :isHousekeeping="isHousekeeping" dialogKey="stay_over" title="Stay Over">{{ data?.stay_over }}</ComTodaySummarySep>
        <ComTodaySummarySep :isHousekeeping="isHousekeeping" dialogKey="unassign_room" title="Unassign Room">{{ data?.unassign_room }}</ComTodaySummarySep>
        <ComTodaySummarySep :isHousekeeping="isHousekeeping"  dialogKey="pickup_drop_off" title="Pickup / Drop Off">{{ data?.pick_up }} / {{ data?.drop_off }} </ComTodaySummarySep>
    </div>
</template>
<script setup>
import { ref, inject } from "@/plugin"
import ComTodaySummarySep from '@/views/frontdesk/components/ComTodaySummarySep.vue';

const props = defineProps({
    isHousekeeping: {
        type:Boolean,
        default:false
    }
})

const frappe = inject("$frappe")
const call = frappe.call()
const data = ref([])
const working_day = JSON.parse(localStorage.getItem("edoor_working_day"))

call.get('edoor.api.frontdesk.get_dashboard_data', {
    property: JSON.parse(localStorage.getItem("edoor_property")).name,
    date: working_day?.date_working_day
}).then((result) => {
    data.value = result.message
})
</script>