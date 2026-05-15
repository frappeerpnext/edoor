<template> 
    <template v-if="data?.initialized_data_upload == 1"> 
        <div class="grid"> 
            <todayBookingSummaryKPI/>
            <KPISummaryCard 
                v-for="value in KPIData" 
                :key="value.title" 
                :data="value.value" 
                :title="$t(value.title)" 
                :icon="value.icon" /> 
        </div>
        <div>
            <ComConnectedBusinessSource />
        </div>
        <div>
            <ComBookingQueueAndChannel/>
        </div>
        <div>
            <ComSyncStatus />
        </div>
    </template>
     
</template>
<script setup>
import { useCMDashboard } from './hooks/useCMDashboard'; 
import KPISummaryCard from "@/views/channel_managers/channel_manager/components/KPISummaryCard.vue"
import todayBookingSummaryKPI from "@/views/channel_managers/channel_manager/components/todayBookingSummaryKPI.vue"
import ComSyncStatus from "./components/ComSyncStatus.vue"
import ComConnectedBusinessSource from "./components/ComConnectedBusinessSource.vue"
import ComBookingQueueAndChannel from "./components/ComBookingQueueAndChannel.vue"
import { ref, inject, onMounted } from '@/plugin'

const {
    recentReservationData
 } = useCMDashboard();

const moment = inject("$moment")
const frappe = inject('$frappe')
const db = frappe.db();
const data = ref({}) 
const property = JSON.parse(localStorage.getItem('edoor_property'))

const KPIData = ref([
    { title: 'Booking Today', value: 0, icon: 'pi-box' },
    { title: 'Undelivered Bookings', value: 0, icon: 'pi-building' }, 
    { title: 'Last Sync Time', value: 0, icon: 'pi-clock' }
])


const getChannelManagerIntegrationData = async () => {
    await db.getDoc('Channel Manager Integration', property.name)
        .then((doc) => { 
            data.value = doc
        }).catch((error) => console.error(error));
}

onMounted(() => {
    getChannelManagerIntegrationData();
})
 
</script> 