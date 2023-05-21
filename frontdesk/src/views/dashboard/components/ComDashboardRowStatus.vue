<template>
    <div class="flex py-2 align-items-center border-b border-color-edoor font-medium">
        <div class="flex-none " v-if="icon">
            <i class="pi mr-3" :class="icon"></i>
        </div>
        <div class="flex-grow">
            <slot></slot>
        </div>
        <div class="flex-none">
            <div :class="badgeClass" class="px-2 py-1 my-1 border-round-lg text-white" :style="{backgroundColor: badgeColor}">{{ value }}</div>
        </div>
    </div>
</template>
<script setup>
 const props = defineProps({
    badgeColor: String,
    badgeClass: String,
    icon:String,
    value: [String,Number]
 })
</script>
<style lang="">
    
</style>