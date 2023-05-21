<template>
    <div class="progress-bar cursor-pointer text-center pt-2 pb-1 px-3 items-center text-white white-space-nowrap overflow-hidden text-overflow-ellipsis"
        :class="current_page == currentPage ? 'active' : ''" @click="$emit('onClick')">
        <div class="flex justify-center pb-1">
            <slot name="icon"></slot>
        </div>
        <div class="pro-navbar-txt">
            <slot name="defualt"></slot>
        </div>
    </div>
</template>
<script setup>
import { useRoute, computed } from '@/plugin'
const current_page = computed(() => useRoute().name)
const props = defineProps({
    icon: String,
    currentPage: String
})
</script>
