<template>    
    <div class="card h-full cursor-pointer" @click="onViewLogDetail(data?.name)">
        <div class="left">
            <div class="main-number mb-2">
                <comTimeAgo :date="data.creation"/>
            </div>

            <div class="title">
                {{$t('Last Sync Time')}}
            </div>

            <div class="subtitle">
                <span class="label mt-2">{{data?.request_type}} - </span>
                <Badge v-if="data?.status == 'Success'" :value="data?.status" severity="success"></Badge>
                <Badge v-if="data?.status == 'Warning'" :value="data?.status" severity="warning"></Badge>
                <Badge v-if="data?.status == 'Fail'" :value="data?.status" severity="danger"></Badge>
            </div>
        </div>

        <div class="icon-box">
            <svg fill="none" viewBox="0 0 24 24" stroke-width="1.8">
                <path stroke-linecap="round" stroke-linejoin="round"
                    d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z" />
                <path stroke-linecap="round" stroke-linejoin="round" d="M3.3 7l8.7 5 8.7-5" />
                <path stroke-linecap="round" stroke-linejoin="round" d="M12 22V12" />
            </svg>
        </div>
    </div>
 
</template>
<script setup>
import { ref, onMounted, watch, onUnmounted } from '@/plugin'
import { useCMDashboard } from '@/views/channel_managers/channel_manager/hooks/useCMDashboard.js'; 
import comTimeAgo from '@/views/channel_managers/channel_manager/components/comTimeAgo.vue'; 
import ChannelManagerSyncLog from "@/views/channel_managers/channel_manager/components/ChannelManagerSyncLog.vue"
import { computed } from 'vue';

const {
    cmLastSyncLog
} = useCMDashboard(); 

const data = computed(() => {
    return cmLastSyncLog.value
}) 

function socketEvent(arg) {
    if (arg.property = window.property.name && arg.action == "update_last_sync_log" ) {
        cmLastSyncLog.value = arg.data
    }
}

onMounted(() => {
    window.socket.on("ChannelManagerUpdate", socketEvent)
})

onUnmounted(() => {
    window.socket.off("ChannelManagerUpdate",socketEvent)
})

function onViewLogDetail(docname) {
    window.postMessage("view_channel_manager_sync_log|" + docname, "*")
}

</script>
<style scoped>
.card {
    position: relative;
    overflow: hidden;
    background: rgba(255, 255, 255, 0.75);
    backdrop-filter: blur(16px);
    border-radius: 30px;
    padding: 16px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    border: 1px solid rgba(255, 255, 255, 0.7);

    box-shadow:
        0 10px 30px rgba(0, 0, 0, 0.06),
        inset 0 1px 1px rgba(255, 255, 255, 0.8);

    transition: 0.3s ease;
}

.card:hover {
    transform: translateY(-4px);
    box-shadow:
        0 18px 35px rgba(0, 0, 0, 0.08),
        inset 0 1px 1px rgba(255, 255, 255, 0.8);
}
 

.left {
    position: relative;
    z-index: 2;
}

.main-number span{
    font-size: 26px;
    font-weight: 800;
    line-height: 1;
    color: #1e3a5f;
    margin-bottom: 8px;
    letter-spacing: -2px;
} 

.title {
    font-size: 14px;
    font-weight: 700;
    color: #243b63;
    margin-bottom: 10px;
}

.subtitle {
    font-size: 10px;
    letter-spacing: 1.4px;
    text-transform: uppercase;
    color: #64748b;
    font-weight: 700;
    display: flex;
    align-items: center;
    gap: 10px;
}

.badge {
    background: linear-gradient(135deg, #f59e0b, #fbbf24);
    color: white;
    padding: 5px 10px;
    border-radius: 999px;
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 0;
    text-transform: none;
}

.icon-box {
    width: 60px;
    height: 62px;
    /* min-width: 78px; */
    border-radius: 24px;

    background: linear-gradient(135deg, #818cf8, #6366f1);

    display: flex;
    justify-content: center;
    align-items: center;

    box-shadow:
        0 12px 24px rgba(99, 102, 241, 0.3),
        inset 0 1px 1px rgba(255, 255, 255, 0.3);

    position: relative;
    z-index: 2;
}

.icon-box svg {
    width: 26px;
    height: 26px;
    stroke: white;
}
</style>