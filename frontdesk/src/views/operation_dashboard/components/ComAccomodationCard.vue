<template>
    <div>{{ data?.room_type_alias }} - {{ data.room_types }}</div>
    <div class="flex gap-2">
        <div class="bg-blue-100  px-2" :style="{width:'fit-content',borderRadius:'50px'}" v-if="data?.business_source">{{ data?.business_source }}</div>
        <div class="flex gap-2 bg-teal-100 px-2" style="border-radius: 50px;width:fit-content"> 
            <ComIcon icon="broomIcon" style="width: 16px;"/>
            <div>Dirty</div>
        </div>
    </div>
</template>
<script setup>
const props = defineProps({
    data:Object
})
</script>