<template>
    <div>
        <span>Total Room:</span> <span>{{ data?.total_room }}</span>
        <div class="card">
            <ProgressBar :value="value?.total_room"></ProgressBar>
        </div>
    </div>
    <div>
        <span>Occupy:</span> <span>{{ data?.total_room_occupy }}</span>
        <ProgressBar :value="value?.total_room_occupy"></ProgressBar>
    </div>
    <div>
        <span>Vacant:</span> <span>{{ data?.total_room_vacant }}</span>
        <ProgressBar :value="value?.total_room_vacant"></ProgressBar>
    </div>
    <div>
        <span>Today Arrival:</span> <span>{{ data?.arrival }}</span>
        <ProgressBar :value="value?.arrival"></ProgressBar>
    </div>
    <div>
        <span>Today Departure:</span> <span>{{ data?.departure }}</span>
        <ProgressBar :value="value?.departure"></ProgressBar>
    </div>
    <div>
        <span>Stay Over:</span> <span>{{ data?.stay_over }}</span>
        <ProgressBar :value="value?.stay_over"></ProgressBar>
    </div>
    <div>
        <span>Arrival Remaining:</span> <span>{{ data?.arrival_remaining }}</span>
        <ProgressBar :value="value?.arrival_remaining"></ProgressBar>
    </div>
    <div>
        <span>Departure Remaining:</span> <span>{{ data?.departure_remaining }}</span>
        <ProgressBar :value="value?.departure_remaining"></ProgressBar>
    </div>
    <div>
        <span>Unassing Room:</span> <span>{{ data?.unassign_room }}</span>
        <ProgressBar :value="value?.unassign_room"></ProgressBar>
    </div>
    <div>
        <span>Pickup:</span> <span>{{ data?.pick_up }}</span>
        <ProgressBar :value="value?.pick_up"></ProgressBar>
    </div>
    <div>
        <span>Drop Off:</span> <span>{{ data?.drop_off }}</span>
        <ProgressBar :value="value?.drop_off"></ProgressBar>
    </div>
</template>
<script setup>
import { ref, inject } from "@/plugin"
import ProgressBar from 'primevue/progressbar';

const frappe = inject("$frappe")
const call = frappe.call()
const data = ref([])
const working_day = JSON.parse(localStorage.getItem("edoor_working_day"))

const value = ref(data);


call.get('edoor.api.frontdesk.get_dashboard_data', {
    property: JSON.parse(localStorage.getItem("edoor_property")).name,
    date: working_day.date_working_day
}).then((result) => {
    data.value = result.message
})


</script>