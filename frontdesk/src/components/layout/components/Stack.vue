<template>
    <div :class="stackClass" :style="{ gap: computedGap }">
      <slot></slot>
    </div>
  </template>
  
  <script setup>
  import { defineProps, computed } from 'vue';
  
  // Define component props
  const props = defineProps({
    row: {
      type: Boolean,
      default: false, // Defaults to column (vertical stacking)
    },
    column: {
      type: Boolean,
      default: true, // Defaults to column (vertical stacking)
    },
    gap: {
      type: [String, Number],
      default: '1rem', // Default gap is 1rem
    },
  });
  
  // Compute the Flexbox direction and gap style based on row and column props
  const stackClass = computed(() => {
    if (props.row) {
      return 'stack-horizontal'; // Use horizontal layout if row is true
    }
    if (props.column) {
      return 'stack-vertical'; // Use vertical layout if column is true
    }
    return 'stack-vertical'; // Default to vertical layout if both are false
  });
  
  const computedGap = computed(() => {
    // Return the gap value, can be a string or number (e.g., '1rem' or 16)
    return typeof props.gap === 'number' ? `${props.gap}px` : props.gap;
  });
  </script>
  
  <style scoped>
  .stack-vertical {
    display: flex;
    flex-direction: column;
  }
  
  .stack-horizontal {
    display: flex;
    flex-direction: row;
  }
  
  .stack-vertical,
  .stack-horizontal {
    width: 100%;
  }
  </style>
  