<template>
    <div class="flex py-2 align-items-center border-b border-color-edoor font-medium ">
        <div class="flex-grow">
            {{ title }}
        </div>
        <div class="flex-none">
            <div class="px-2 py-1 my-1 border-round-lg text-white " :class="class" >{{ value }}</div>
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