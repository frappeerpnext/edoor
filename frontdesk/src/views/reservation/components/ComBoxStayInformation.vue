
<template>
  <h6 v-if="title !== null" class="flex items-center justify-end" :class="titleClass">{{ title }}</h6>
  <span class="mx-2 py-2 px-3 bg-white border-round-lg " :class="valueClass">
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