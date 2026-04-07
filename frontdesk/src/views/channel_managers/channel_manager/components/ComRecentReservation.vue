<template>
    {{ recentReservationData }}
</template>
<script setup>
import { onMounted } from 'vue';
import { useCMDashboard } from '../hooks/useCMDashboard';
const {
    recentReservationData, 
    getrecentReservationData
}

onMounted(()=>{
    getrecentReservationData();
})

</script>