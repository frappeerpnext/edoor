
<template>
<div class="bg-card-info border-round-xl pt-2 pb-3  px-3">
    <div class="flex justify-between">
        <div class="text-lg line-height-4 font-bold">{{title}}</div>
        <div class="">
            <slot name="btn"></slot>
        </div>
    </div>
        <div>
            <slot name="content"></slot>
        </div>
</div>
</template>
<script setup>
const props = defineProps({
  title: String,
  value: [String,Number]
})
</script>