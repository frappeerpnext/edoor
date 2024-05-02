<template>
    <div>
            <div class="text-2xl font-bold" :class="class">
            {{label}}
            </div>
            <div class="flex gap-6 mt-2">
                <slot></slot>
            </div>
    </div>
</template>
  
  <script setup>
  const props = defineProps({
    label: {
      type: String,
    },
    class: {
      type: String,
    },
  });
  </script>
  