<template>
    <div class="flex py-2 align-items-center border-b border-color-edoor font-medium cursor-pointer px-1" @click="onClick">
        <div class="flex-grow">
            {{ title }}
        </div>
        <div class="flex-none">
            <div class="px-2 py-1 border-round-lg text-white " :class="class" :style="style">{{ value }}</div>
        </div>
    </div>
</template>
<script setup>
const props = defineProps({
    value: [String, Number],
    title: String,
    class: String,
    style: String
})
const emit = defineEmits(["onClick"])
function onClick (){
    emit("onClick")
}
</script>
<style scoped>
.flex.py-2.align-items-center.border-b.border-color-edoor.font-medium.cursor-pointer:hover{
    background: #f0f0f0;

}
</style>