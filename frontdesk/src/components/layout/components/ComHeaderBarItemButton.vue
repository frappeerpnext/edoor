<template>
    <div class="cursor-pointer bg-blue-600 text-center p-2 items-center text-white hover:bg-blue-700" @click="$emit('onClick')">
        <div><i class="pi" :class="icon" style="font-size: 1rem"></i></div>
        <div><slot></slot></div>
    </div>
</template>
<script setup>
    const props = defineProps({
        icon: String
    })
</script>
 