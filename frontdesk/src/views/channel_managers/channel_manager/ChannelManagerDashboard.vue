<template> 
    <template v-if="data?.initialized_data_upload == 1">  
        <ComSyncLogWarningAlert/>
        <ComPendingSyncDataStatus :types="['Room Rate','Restriction']"/> 
        <div class="grid">
            <div class="col-3">
                <comCMProviderInfo/>
            </div> 
            <div class="col-9">  
                <div class="grid">
                    <div class="col-4">
                        <todayBookingSummaryKPI/>
                    </div>
                    <div class="col-4">
                        <ComTodayCancelBookingSummaryKPI/>
                    </div>
                    <div class="col-4">
                        <ComLastTimeSync/>
                    </div>
                </div> 
            </div>  
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
import { ref, inject, onMounted } from '@/plugin'
import { useCMDashboard } from './hooks/useCMDashboard'; 
import KPISummaryCard from "@/views/channel_managers/channel_manager/components/KPISummaryCard.vue"
import todayBookingSummaryKPI from "@/views/channel_managers/channel_manager/components/todayBookingSummaryKPI.vue"
import ComTodayCancelBookingSummaryKPI from "@/views/channel_managers/channel_manager/components/ComTodayCancelBookingSummaryKPI.vue"
import ComLastTimeSync from "@/views/channel_managers/channel_manager/components/ComLastTimeSync.vue"
import ComSyncStatus from "./components/ComSyncStatus.vue"
import ComConnectedBusinessSource from "./components/ComConnectedBusinessSource.vue"
import ComBookingQueueAndChannel from "./components/ComBookingQueueAndChannel.vue"
import comCMProviderInfo from "@/views/channel_managers/channel_manager/components/comCMProviderInfo.vue"
import ComAllConnectedResource from "@/views/channel_managers/channel_manager/components/ComAllConnectedResource.vue"
import ComSyncLogWarningAlert from '@/views/channel_managers/channel_manager/components/ComSyncLogWarningAlert.vue'
import ComPendingSyncDataStatus from '@/views/channel_managers/components/ComPendingSyncDataStatus.vue';


const {
    recentReservationData
 } = useCMDashboard();

const moment = inject("$moment")
const frappe = inject('$frappe')
const db = frappe.db();
const data = ref({}) 
const property = JSON.parse(localStorage.getItem('edoor_property'))

const KPIData = ref([ 
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
<style scoped>
.summary-kpi-cs { 
    display:flex;
    /* flex-direction:column; */
    gap:15px;
}
</style>