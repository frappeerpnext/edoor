<template>
    <div class="px-3 py-1 text-white" :style="{background:data?.status_color,width:'fit-content','border-radius':'50px'}">
        {{ data?.reservation_status }}
    </div>
</template>
<script setup>
const props = defineProps({
    data:Object
})
</script>