<template>
    <ComOwnerContentTitle label="Today's Room Type Sales">  
        <div class="card">
        <TabView>
            <TabPanel>
        <template #header>
            <div class="flex align-items-center gap-2 ">
                <span class="font-bold white-space-nowrap">Actual</span>
                <span style="background:#0000001f" class="text-sm rounded-lg px-2 py-1 "  >  <CurrencyFormat :value="totalAmountActual" />  </span>
            </div>
        </template>
        <div>
<div class="col w-full p-0">

    <Skeleton v-if="loading" class="mb-2" v-for="index in 3" :key="index" width="100%" height="50px"></Skeleton>
    <template v-else>
    <ComOwnerBarChartLine  v-for="(room, index) in data?.datasets_actual" :key="index" :roomType="room.name" :color="room.color" :roomSold="room.room_sold" :totalRoomSold="totalRoomActual" :value="room.values" />
    </template>
</div>
        </div>
    </TabPanel>
    <TabPanel>
        <template #header>
            <div class="flex align-items-center gap-2">
                <span class="font-bold white-space-nowrap">Expected</span>
                <span style="background:#0000001f" class="text-sm rounded-lg px-2 py-1 "> <CurrencyFormat :value="totalAmountExpected" /> </span>
            </div>
        </template>
        <div>
            <ComOwnerBarChartLine v-for="(room, index) in data?.datasets_expected" :key="index" :roomType="room.name" :color="room.color" :roomSold="room.room_sold" :totalRoomSold="totalRoomExpected" :value="room.values" />
        </div>
    </TabPanel>
           
        </TabView>
    </div>
</ComOwnerContentTitle>    
</template>
<script setup>
import {  ref, onMounted,getApi ,computed  } from '@/plugin'
import ComOwnerContentTitle from '@/views/dashboard/components/ComOwnerContentTitle.vue'
import ComOwnerBarChartLine from '@/views/dashboard/components/ComOwnerBarChartLine.vue'
import TabView from 'primevue/tabview';
const loading = ref(true)
const data = ref({})
function renderdata() {
    loading.value = true 
const doc = getApi('frontdesk.get_room_type_chart_data', {
        property: JSON.parse(localStorage.getItem("edoor_property")).name,
        date: JSON.parse(localStorage.getItem("edoor_working_day")).date_working_day
    })
    .then((result) => {
        loading.value = false 
            data.value = result.message 
        })
        .catch((error) => {
            loading.value = true 
  });
    }
const totalRoomActual = computed(() => {
  if (!data.value || !data.value.datasets_actual) return 0;
  return data.value.datasets_actual.reduce((acc, curr) => acc + curr.room_sold, 0);
});
const totalAmountActual = computed(() => {
  if (!data.value || !data.value.datasets_actual) return 0;
  return parseFloat(data.value.datasets_actual.reduce((acc, curr) => acc + curr.values, 0).toFixed(2));
});
const totalRoomExpected = computed(() => {
  if (!data.value || !data.value.datasets_expected) return 0;
  return data.value.datasets_expected.reduce((acc, curr) => acc + curr.room_sold, 0);
});
const totalAmountExpected = computed(() => {
  if (!data.value || !data.value.datasets_expected) return 0;
  return parseFloat(data.value.datasets_expected.reduce((acc, curr) => acc + curr.values, 0).toFixed(2));
});

    onMounted(() => {
    renderdata()
    
})         
</script>
<style scope>
.p-tabview-panels {
    padding: 10px 0px 0px 0px;
}
</style>