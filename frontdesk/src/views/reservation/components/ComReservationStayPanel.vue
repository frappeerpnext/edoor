
<template>
<div class="bg-card-info border-round-xl pt-2 pb-3 px-3">
    <div class="flex justify-between">
        <div class="text-lg line-height-4 flex items-center font-semibold mb-2" :class="titleClass" >{{title}}</div>
        <div class="mx-0 my-auto">
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
  titleClass: String,
  title: String,
  value: [String,Number]
})
 
</script>