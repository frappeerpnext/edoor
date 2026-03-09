<template>
    <Stack>
        <h1 class="text-lg">Res #: {{ data.name }}</h1>
        <p class="text-base">Stay: {{ moment(data.arrival_date).format("DD-MM-YYYY") }} to {{ moment(data.departure_date).format("DD-MM-YYYY") }}
            ({{ data.total_active_reservation_stay }} Ns)
<br/>
Source: {{ data.business_source }}

        </p>
    <!-- <Button @click.stop="test">View Reservation Detail</Button> -->

    </Stack>
    
</template>
<script setup>
import {inject} from "@/plugin"
const props = defineProps({
    data:Object
})
const moment = inject("$moment")
function test(){
    window.onOpenLink("view_reservation_detail",props.option.name);
    
}
</script>