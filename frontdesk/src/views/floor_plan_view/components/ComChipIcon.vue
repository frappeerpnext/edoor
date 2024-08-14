<template>
    <span
      class="rounded-full border-1 border-400 flex justify-center items-center"
      :style="{ width: size, height: size ,backgroundColor: bgColor }"
    >
      <ComIcon v-if="svgIcon" :icon="svgIcon" :height="iconHeight" />
      <i v-if="icon" :class="['text-white pi ', icon]" :style="{ fontSize: iconHeight + 'px' }" />
      <slot></slot>
    </span>
  </template>
  
  <script setup>
  import { computed } from 'vue';
  
  // Props
  const props = defineProps({
    svgIcon: {
      type: String,
    },
    icon: {
      type: String,
    },
    iconHeight: {
      type: String,
      default: '14px',
    },
    size: {
      type: String,
      default: '26px',
    },
    bgColor: {
      type: String,
    },
  });
  </script>