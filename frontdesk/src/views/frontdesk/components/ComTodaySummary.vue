<template>
    <div> 
        <ComChartDoughnut :data="chartData" v-if="chartData.length > 0" show-percentage="Occupied" class="doughnut__chart_ds"/>
    </div>
    <div class="td_guest_cs px-1 mt-3">
        <ComTodaySummarySep title="All Rooms">{{ data?.total_room }}</ComTodaySummarySep>
        <ComTodaySummarySep dialogKey="arrival" title="Arrival" :totalValue="data.arrival + data.arrival_remaining" :value="data.arrival">
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
import { useDialog } from 'primevue/usedialog';
import ComTodaySummarySep from '@/views/frontdesk/components/ComTodaySummarySep.vue';
import ComRoomStatusDoughnut from '@/views/dashboard/components/ComRoomStatusDoughnut.vue';
import ComIFrameModal from "../../../components/ComIFrameModal.vue";


const frappe = inject("$frappe")
const call = frappe.call()
const data = ref([])
const working_day = JSON.parse(localStorage.getItem("edoor_working_day"))
const gv = inject("$gv")
const chartData = ref([])

const dialog = useDialog();

call.get('edoor.api.frontdesk.get_dashboard_data', {
    property: JSON.parse(localStorage.getItem("edoor_property")).name,
    date: working_day.date_working_day
}).then((result) => {
    data.value = result.message
    const documentStyle = getComputedStyle(document.body);
    chartData.value.push({label: 'Occupied', value: data.value.total_room_occupy, color: documentStyle.getPropertyValue('--bg-btn-green-color')})
    chartData.value.push({label: 'Vacant', value: data.value.total_room_vacant, color: documentStyle.getPropertyValue('--bg-warning-color')})
})
</script>