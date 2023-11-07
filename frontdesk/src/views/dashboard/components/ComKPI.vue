<template>
    <div v-tippy="tooltip" class="col-3 p-1" @click="onClick">
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
    tooltip: String,
    class: String
})

const emit = defineEmits(["onClick"])

function onClick (){
    emit("onClick")
}
</script>