<template>
    <div>Room Type: <span class="font-semibold">{{ data?.room_type_alias }} - {{ data.room_types }}</span></div>
    <div>
        <span class="me-2">Room #:</span><span v-if="data?.rooms"><span class="font-semibold">{{data?.rooms}}</span></span>
        <span @click="onAssignRoom(item.rooms_data,item.name)" class="link_line_action w-auto" v-else>
                <i class="pi pi-pencil"></i>
                {{ $t('Assign Room') }}

        </span>
    </div>
    <div class="flex gap-2 mt-2">
        <!-- {{ data }} -->
        <div class="bg-blue-100  px-2" :style="{width:'fit-content',borderRadius:'50px'}" v-if="data?.business_source">{{ data?.business_source }}</div>
       
    </div>
</template>
<script setup>
const props = defineProps({
    data:Object
})
</script>