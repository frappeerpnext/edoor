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
  
  const hidePreviouseMonth = localStorage.getItem("rate_plan_hide_previouse_months")
  

  if (selectedYear.value == y) return false;
  selectedYear.value=y
  if (y>moment().year() || y<moment().year() ){
     startDate.value = y + '-01-01'
    endDate.value = y + '-12-31'
  }else  {
    if (hidePreviouseMonth){
       startDate.value = moment().format("YYYY-MM-01")
      endDate.value = y + '-12-31'
    }else {
      startDate.value = y + '-01-01'
      endDate.value = y + '-12-31'
    }
  }
  
 
  selectedDates.value = new Set();
  await reloadRoomRatesData()
}
</script>