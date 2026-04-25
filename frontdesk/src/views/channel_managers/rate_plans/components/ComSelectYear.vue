<template>
  <ButtonGroup>
    
            <Button 
            class="border-0"
            :severity="selectedYear==y?'warning':''"
            :label="y" v-for="y in years" :key="y" 
            @click="onChangeYear(y)"
            />
            
        </ButtonGroup>
</template>
<script setup>
import { useRatePlan } from '@/views/channel_managers/rate_plans/hooks/useRatePlan.js';
import { inject } from 'vue';
const {years,selectedYear,startDate,endDate,reloadRoomRatesData,selectedDates } = useRatePlan();
const moment = inject("$moment")
async function onChangeYear(y){
  if (selectedYear.value == y) return false;
  selectedYear.value=y
  startDate.value = y + '-01-01'
  endDate.value = y + '-12-31'
  selectedDates.value = new Set();
  await reloadRoomRatesData()
}
</script>