<template>
    <div class="p-2 surface-50 flex w-full rounded-lg mb-2">
      <div class="col">
        <div class="flex justify-content-between">
          <div>{{ roomType }} - {{roomSold}} / {{totalRoomSold}} </div>
          <div>{{ (( roomSold / totalRoomSold ) * 100).toFixed(2) }}%</div>
        </div>
        <div class="surface-200" style="height:5px;">
          <div class="h-full" :style="{ width: ( roomSold / totalRoomSold ) * 100 + '%', backgroundColor: color }"></div>
        </div>
      </div>
      <div class="col-fix w-10rem px-3 surface-200 rounded-lg flex justify-content-center item-content-center">
        <div class="m-auto font-bold">
          <CurrencyFormat :value="value" />
        </div>
      </div>
    </div>
  </template>
  
  <script setup>
  import { defineProps } from 'vue'
  
  const props = defineProps({
    roomType: String,
    roomSold: Number,
    totalRoomSold:Number,
    value: Number,
    color: {
        type: String,
        default: "red"
    },
  })
  </script>