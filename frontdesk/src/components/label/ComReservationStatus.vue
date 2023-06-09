<template>
    <span v-if="status" class="px-2 rounded-lg me-2 text-white p-1px" :class="class"  :style="{ background: status?.color}">
        {{ status.name }}
    </span>
</template>
<script setup>
const props = defineProps({
    statusName: String,
    class: String
})
const setting = JSON.parse(localStorage.getItem('edoor_setting'))
const status = setting.reservation_status.find((r)=>r.name == props.statusName)
</script>
<style lang="">
    
</style>