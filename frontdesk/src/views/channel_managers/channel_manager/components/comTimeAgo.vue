<template>
    <span>{{ display_time }}</span>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from "vue";
import { timeAgo } from "@/views/channel_managers/channel_manager/hooks/helper.js";

const props = defineProps({
    date: [String, Date, Number]
});

const display_time = ref("");

let interval = null;

function updateTime() {
    display_time.value = timeAgo(props.date);
}

onMounted(() => {
    updateTime();

    interval = setInterval(() => {
        updateTime();
    }, 1000);
});

onUnmounted(() => {
    clearInterval(interval);
});
</script>