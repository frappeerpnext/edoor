<template>
   <div>
        <div class="text-2xl font-bold">
            <CurrencyFormat :value="value" />
        </div>
        <div>
            {{$t(label)}}
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
    value: {
      type: Number,
    },
  });
  </script>
  