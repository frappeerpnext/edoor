<template>
    <div class="pb-0 w-6" style="height: 33rem !important;"> 
        <div class="card h-full" style="border-radius: 30px !important;">
             <div class="card-header">
                <div class="title">{{ $t('Bookings by channel') }}</div>
            </div> 
            <ComChart v-if="chartData && !loading" :chartData="chartData" />
        </div>
    </div>
</template>
<script setup>
import {ref} from 'vue'
import { useCMDashboard } from '@/views/channel_managers/channel_manager/hooks/useCMDashboard.js'
import ComChart from "@/components/chart/ComChart.vue"
import { computed, onMounted } from 'vue';

const data = ref([]) 

async function getBookingByChannel(start_date, end_date) {
    const res = await app.getApi("edoor.channel_managers.channel_manager_dashboard.get_reservation_booking_by_channel", {
        property: window.property_name,
        start_date: '2026-03-20',
        end_date: '2026-03-27'
    })

    if (res.data) {
        data.value = res.data
    }
}

onMounted(async() => {
    await getBookingByChannel()
    console.log("Booking by channel", data.value)
})

const chartData = computed(() => {
    return {
        labels: data.value?.map(d => d.business_source) || [],
        datasets: [
            {
                name: 'Bookings',
                type: 'bar',
                data: data.value?.map(d => d.total_booking) || [],
            }
        ]
    }
})


</script>
<style scoped>
.container {
    display: flex;
    gap: 20px;
    padding: 30px;
}

.card {
    flex: 1;
    background: #fff;
    border-radius: 14px;
    padding: 20px;
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.06);
}

.card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 15px;
}

.title {
    font-size: 16px;
    font-weight: 600;
}

 

table {
    width: 100%;
    border-collapse: collapse;
    font-size: 13px;
}

th {
    text-align: left;
    color: #94a3b8;
    font-weight: 500;
    padding-bottom: 8px;
}

td {
    padding: 8px 0;
    border-top: 1px solid #f1f5f9;
}
 
.btn:hover {
    background: #f1f5f9;
}

/* Progress bars */
.progress-item {
    margin-bottom: 14px;
}

.progress-label {
    display: flex;
    justify-content: space-between;
    font-size: 13px;
    margin-bottom: 4px;
}

.progress-bar {
    height: 6px;
    background: #e5e7eb;
    border-radius: 10px;
    overflow: hidden;
}

.progress-fill {
    height: 100%;
    background: linear-gradient(90deg, #4ade80, #22c55e);
    border-radius: 10px;
}
</style>