<template>
<div>
  <div class="flex w-full rounded-lg gap-2 pe-2" >
      <div class="col font-bold">
        Room Type
      </div>
      <div class="col-fix w-10rem px-3 rounded-lg relative" >
        <div class="font-bold value_room_type_chart">
          Actual
        </div>
      </div>
      <div class="col-fix w-10rem px-3 rounded-lg relative" >
        <div class="font-bold value_room_type_chart">
          Expected
        </div>
      </div>
    </div>
  <div v-for="(room, index) in data?.datasets" :key="index" class="p-2 surface-50 flex w-full rounded-lg mb-2 gap-2 " >
      <div class="col">
        <div class="flex justify-content-between">
          <div>{{ room.name }} - {{ room.room_sold }} / {{ room.total_room }}</div>
          <div>{{ ((room.room_sold / room.total_room) * 100).toFixed(2) }}%</div>
        </div>
        <div class="surface-200" style="height: 5px;">
          <div
            class="h-full"
            :style="{ width: (room.room_sold / room.total_room) * 100 + '%', backgroundColor: room.color }"
          ></div>
        </div>
      </div>
      <div class="col-fix w-10rem px-3 surface-200 rounded-lg relative">
        <div class="font-bold value_room_type_chart">
          <CurrencyFormat :value="room.actual_values" />
        </div>
      </div>
      <div class="col-fix w-10rem px-3 surface-200 rounded-lg relative" >
        <div class="font-bold value_room_type_chart">
          <CurrencyFormat :value="room.expected_values" />
        </div>
      </div>
    </div>
    <hr class="my-2">
    <div class="p-2 surface-50 flex w-full rounded-lg mb-2 gap-2 " >
      <div class="col font-bold">
        Total: {{ getTotal('room_sold') }} / {{ getTotal('total_room') }}
      </div>
      <div class="col-fix w-10rem px-3 surface-200 rounded-lg relative" >
        <div class="font-bold value_room_type_chart">
          <CurrencyFormat :value="getTotal('actual_values')" />
        </div>
      </div>
      <div class="col-fix w-10rem px-3 surface-200 rounded-lg relative" >
        <div class="font-bold value_room_type_chart">
          <CurrencyFormat :value="getTotal('expected_values')" />
        </div>
      </div>
    </div>  
  <div>

  </div>
  </div>
</template>

<script setup>
import { defineProps } from 'vue'

const props = defineProps({
  data: Object
});
const getTotal = (field) => {
  return props.data.datasets.reduce((sum, room) => sum + room[field], 0);
};
</script>
