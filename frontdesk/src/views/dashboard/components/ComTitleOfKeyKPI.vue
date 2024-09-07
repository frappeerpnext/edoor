<template>
    <div>
            <div class="text-2xl font-bold" :class="class">
            {{$t(label)}}
            </div>
            <div class="grid  gap-6 mt-2">
                <slot></slot>
            </div>
    </div>
</template>
  
  <script setup>
     import {i18n} from '@/i18n';
     const { t: $t } = i18n.global;
  const props = defineProps({
    label: {
      type: String,
    },
    class: {
      type: String,
    },
  });
  </script>
  