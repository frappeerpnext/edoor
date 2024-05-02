<template>
   <div>
        <div class="text-2xl font-bold">
            <CurrencyFormat :value="value" />
        </div>
        <div>
            {{label}}
        </div>
    </div>
</template>
  
  <script setup>
  const props = defineProps({
    label: {
      type: String,
    },
    value: {
      type: Number,
    },
  });
  </script>
  