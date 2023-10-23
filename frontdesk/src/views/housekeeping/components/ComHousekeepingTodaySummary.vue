<template>
    <div class="td_guest_cs px-1 cursor-pointer">

    <ComTodaySummarySep dialogKey="all_rooms" title="All Rooms">{{ data?.total_room }}</ComTodaySummarySep>
        <tippy :content="((data?.arrival || 0) - (data?.arrival_remaining || 0)) + ' Checked-in '  + ' and ' + ' Total Arrival ' + (data?.arrival|| 0)  ">
            <ComTodaySummarySep dialogKey="arrival" title="Arrival" :totalValue="data.arrival" :value="((data.arrival || 0) -(data.arrival_remaining || 0))">
                <span>{{ (data?.arrival || 0) -(data?.arrival_remaining || 0) }}</span>/<span>{{ (data?.arrival || 0) }}</span>
            </ComTodaySummarySep>
        </tippy>
        <tippy :content="((data?.departure ||0) - (data?.departure_remaining ||0)) + ' Checked-out' + ' And '+ 'Total Departure ' +  (data?.departure ||0)   ">
            <ComTodaySummarySep dialogKey="departure" title="Departure" :totalValue="data.departure" :value="data.departure - data?.departure_remaining">
            <span title="Departure">{{ (data?.departure ||0) - (data?.departure_remaining ||0) }}</span>/<span titel="Departure Remain">{{ data?.departure || 0 }}</span>
            </ComTodaySummarySep>
        </tippy>
        <ComTodaySummarySep :isHousekeeping="isHousekeeping" dialogKey="stay_over" title="Stay Over">{{ data?.stay_over }}</ComTodaySummarySep>
  
        <ComTodaySummarySep :isHousekeeping="isHousekeeping" dialogKey="unassign_room" title="Unassign Room">{{ data?.unassign_room }}</ComTodaySummarySep>
        <tippy :content="'Group Arrival '+  data?.git_reservation_arrival + ' Group(s) and ' + data?.git_stay_arrival + ' Stay(s)'">
            <ComTodaySummarySep   dialogKey="git_arrival" title="GIT Arrival">{{ (data?.git_reservation_arrival ||0) + '/' +  (data?.git_stay_arrival ||0) }}</ComTodaySummarySep>
        </tippy>
        <ComTodaySummarySep :isHousekeeping="isHousekeeping"  dialogKey="pickup_drop_off" title="Pickup / Drop Off">{{ data?.pick_up }} / {{ data?.drop_off }} </ComTodaySummarySep>
        <ComTodaySummarySep  dialogKey="no_show" title="No Show">{{data?.total_no_show || 0}}</ComTodaySummarySep>
        <ComTodaySummarySep  dialogKey="cancelled" title="Cancelled">{{data?.total_cancelled || 0}}</ComTodaySummarySep>
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