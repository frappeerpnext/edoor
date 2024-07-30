<template>
    <div :class="['lg:col col-12 relative overflow-hidden border-round-xl py-2 px-4 ', bgColor]">
      <div class="h-6rem w-6rem flex justify-content-center align-items-center bg-black absolute -right-6 -top-8 pt-3 pr-2 border-circle" style="background-color: rgba(0, 0, 0, 0.15)">
        <slot name="icon" v-if="$slots.icon"></slot>
      <i v-else :class="[icon, 'text-white', 'text-2xl']"></i>
      </div>
      <div class="text-lg">
        {{ label }}
      </div>
      <div class="text-3xl font-bold">
        <CurrencyFormat :value="value" />

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
    bgColor: {
      type: String,
      default: 'bg-green-200'
    },
    icon: {
      type: String,
      default: 'pi pi-check'
    }
  });
  </script>
  