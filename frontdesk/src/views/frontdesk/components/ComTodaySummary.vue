<template>
  
    Total Room: {{ data?.total_room }} <br/>
    Occupy: {{ data?.total_room_occupy }} <br/>
    Vacant: {{ data?.total_room_vacant }} <br/>

Today Arrival: {{data?.arrival}} <br/>
Today Departure: {{data?.departure}}<br/>
Stay Over: {{data?.stay_over}}<br/>
Arrival Remaining: {{ data?.arrival_remaining }} <br/>
Departure Remaining: {{ data?.departure_remaining }} <br/>
Unassing Room:  {{ data?.unassign_room }} <br/>
Pickup: {{ data?.pick_up }} <br/>
Drop Off: {{ data?.drop_off }} <br/>
</template>
<script setup>
import {ref,inject} from "@/plugin"

const frappe = inject("$frappe")
const call = frappe.call()
const data = ref([])
const working_day = JSON.parse(localStorage.getItem("edoor_working_day"))
call.get('edoor.api.frontdesk.get_dashboard_data', {
        property: JSON.parse(localStorage.getItem("edoor_property")).name,
        date: working_day.date_working_day
    }).then((result)=>{
        data.value = result.message
    })


</script>