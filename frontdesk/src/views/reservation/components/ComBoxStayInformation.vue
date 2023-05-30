
<template>
  <span v-if="title !== null" class="flex items-center justify-end text-right" :class="titleClass">{{ title }}</span>
  <span v-tooltip.top="value" class="py-2 px-3 border-round-lg overflow-hidden text-overflow-ellipsis whitespace-nowrap border border-white" style="background-color: #fff;" :class="valueClass">
    <slot>
      
    </slot>
    {{ value }}
  </span>
</template>
<script setup>
const props = defineProps({
  titleClass:{type: String , default: 'w-6rem'},
  title: {type: String , default: null},
  value: [String, Number],
  valueClass: String
})

</script>