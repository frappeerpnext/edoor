<template>
    <div class="flex align-items-center border-b border-color-edoor font-medium">
        <div class="flex-none pr-4 flex items-center" v-if="icon">
            <span v-html="icon"></span>
        </div>
        <div class="flex-grow">
            <slot name="content"></slot>
        </div>
        <div class="flex-none">
            <div :class="badgeClass" class="px-2 py-1 border-round-lg text-white btn-green-edoor" :style="{ backgroundColor: badgeColor }">{{ value }}
            <template v-if="is_room_block">
                / 
{{ value_room_block }}
            </template>
            </div>
        </div>
    </div>
</template>
<script setup>
const props = defineProps({
    badgeColor: String,
    badgeClass: String,
    icon: String,
    value: [String, Number],
    is_room_block: false,
    value_room_block: [String, Number]
})
</script>
<style lang="">
    
</style>