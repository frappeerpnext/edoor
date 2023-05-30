<template>
    <div class="col-3 p-1">
        <div class="p-2 h-full h-9rem justify-content-between flex flex-column text-center" :class="class">
            <div class="text-6xl">{{ value }}</div>
            <div class="text-base">{{ title }}</div>
        </div>
    </div>
</template>
<script setup>
const props = defineProps({
    value: [String, Number],
    title: String,
    class: String
})
</script>
<style lang="">
    
</style>