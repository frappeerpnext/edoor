<template>
       <div>
              <ComDonutFrontdesk/>
              <ComHousekeepingTodaySummary/>
              <ComHousekeepingStatus />
       </div>
</template>
<script setup>
import { ref } from 'vue'
import ComHousekeepingStatus from '@/views/dashboard/components/ComHousekeepingStatus.vue';
import ComRoomStatusDoughnut from '@/views/dashboard/components/ComRoomStatusDoughnut.vue';
import ComDonutFrontdesk from '../../frontdesk/components/ComDonutFrontdesk.vue';
import ComHousekeepingTodaySummary from './ComHousekeepingTodaySummary.vue';
const data = ref({})
</script>