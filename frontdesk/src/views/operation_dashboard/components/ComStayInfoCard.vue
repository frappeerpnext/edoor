<template>
    <div>{{ moment(data?.arrival_date).format("DD-MM-YYYY") }} &#8594; {{ moment(data?.departure_date).format("DD-MM-YYYY") }}</div>
    
    <div class="flex gap-2">
        <div class="flex gap-2 bg-purple-200 border-round py-1 px-2 align-items-center" style="width:fit-content"> 
            <div>{{ data?.room_nights }}</div>
            <div><ComIcon icon="moonIcon" style="width:16px"/></div>
        </div>
        <div class="flex gap-2 bg-purple-200 border-round py-1 px-2 align-items-center" style="width:fit-content"> 
            <div>{{ data?.adult }}</div>
            <div><ComIcon icon="adultIcon" style="width:16px"/></div>
        </div>
        <div class="flex gap-2 bg-purple-200 border-round py-1 px-2 align-items-center" style="width:fit-content"> 
            <div>{{ data?.child }}</div>
            <div><ComIcon icon="childIcon" style="width:16px"/></div>
        </div>
    </div>
</template>
<script setup> 
import { inject } from '@/plugin';
const moment = inject("$moment")
const props = defineProps({
    data:Object
})
</script>