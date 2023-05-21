<template>
    <div class="bg-white p-2 h-full">
        <div class="font-bold pl-1 text-lg">
            {{ title }}
        </div>
        <div>
            <slot></slot>
        </div>
    </div>
</template>
<script setup>
    const props = defineProps({
        title: String
    })
</script>
<style scoped>
    .sys-date {
        background-color: rgb(94, 27, 202) !important;
    }
</style>