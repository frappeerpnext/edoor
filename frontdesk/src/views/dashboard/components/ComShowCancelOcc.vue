<template>
    <div class="col-6 font-medium" @click="onClick">
        {{ title }}
        <div class="flex-none mt-3">
            <span class="px-4 py-2 my-1 border-round-lg text-color-btn bg-gray-edoor">{{ value }}</span>
        </div>
    </div>
</template>
<script setup>
const props = defineProps({
    title: String,
    value: [String, Number]
})
const emit = defineEmits(["onClick"])
function onClick() {
    emit("onClick")
}
</script>