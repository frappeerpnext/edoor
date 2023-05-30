<template>
    <div class="bg-white p-2 h-full border-round-xl">
        <div class="font-semibold text-lg px-1">
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