<template>
    <ComPanel :title="$t('Recent Sync Logs')" :viewAll="true" class="sys-date h-17rem md:h-full mt-3 p-5" style="border-radius: 30px !important;">
        <template #viewAll>
            <div class="panel-header justify-content-end">
                <button class="view-all" @click="onViewSyncLog()">{{ $t('View Sync Log Details') }}</button>
            </div>
        </template> 
        <div class="logs"> 
                <div class="log-item cursor-pointer" v-for="(d, index) in filteredLogs" :key="d.name" @click="onViewLogDetail(d.name)">
                    <!-- LEFT -->
                    <div class="log-left"> 

                        <div class="log-status">
                            {{ d.title }}

                            <Badge v-if="d.status" :severity="getStatusSeverity(d.status)">
                                {{ d.status }}
                            </Badge>
                            <Badge>{{ d.provider || 'Unknown' }}</Badge>
                        </div>

                        <div v-if="d?.response_text" class="log-message">
                            {{ d.response_text }}
                        </div>
                        <div class="log-message font-italic" v-else>
                            {{ $t('No Message Available') }}
                        </div>
                    </div>

                    <!-- RIGHT -->
                    <div class="log-right h-full">
                        <div class="log-time"> 
                            <comTimeAgo :date="d.creation"/>
                        </div>

                        <Badge class="cursor-pointer">{{ $t('View Details') }}</Badge>
                    </div>

                </div> 
        </div>
    </ComPanel>
</template>

<script setup>
import { onMounted, ref, computed, onUnmounted } from 'vue'
import Tag from 'primevue/tag';
import comTimeAgo from '@/views/channel_managers/channel_manager/components/comTimeAgo.vue'; 
import { useCMDashboard } from '@/views/channel_managers/channel_manager/hooks/useCMDashboard.js'; 
import ChannelManagerSyncLog from "@/views/channel_managers/channel_manager/components/ChannelManagerSyncLog.vue"
const {
    getLastSyncLogList
} = useCMDashboard(); 
 
const data = computed(() => {
    return getLastSyncLogList.value
})

const filteredLogs = computed(() => {
    return data.value.filter(item => item.status || item.creation || item.provider)
})

const statusClass = (status) => {
    if (!status) return 'default'
    return status.toLowerCase() // success / warning
}

function onViewLogDetail(docname) {
    window.postMessage("view_channel_manager_sync_log|" + docname, "*")
}

const getStatusSeverity = (status) => {
    const severityMap = {
        Success: 'success',
        Warning: 'warning',
        Error: 'danger',
    }

    return severityMap[status] || 'info'
}

function socketEvent(arg) { 
    if (arg.property = window.property.name && arg.action == "update_last_sync_log" ) {
        getLastSyncLogList.value = arg.sync_log_list
    }
}

async function onViewSyncLog(){
     await app.utils.openDialog(ChannelManagerSyncLog,"Channel Manager Sync Log")

}

onMounted(async () => {
    window.socket.on("ChannelManagerUpdate", socketEvent ) 
})

onUnmounted(() => {
    window.socket.off("ChannelManagerUpdate",socketEvent)
})
</script>


<style scoped>
.logs {
    display: flex;
    flex-direction: column;
    gap: 12px;
    padding: 8px 4px;
}

/* Each Log Card */
.log-item {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    gap: 16px;

    padding: 16px;
    border-radius: 14px;

    background: #ffffff;
    border: 1px solid #edf0f5;

    transition: all 0.2s ease;
}

.log-item:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 18px rgba(0, 0, 0, 0.06);
    border-color: #dfe5ee;
}

/* Left Section */
.log-left {
    flex: 1;
    min-width: 0;
}

/* Provider Tag */
:deep(.p-tag) {
    font-size: 11px;
    font-weight: 600;
    border-radius: 999px;
    padding: 4px 10px;
}

/* Title */
.log-status {
    display: flex;
    align-items: center;
    gap: 8px;

    margin-top: 10px;

    font-size: 15px;
    font-weight: 600;
    color: #1f2937;
}

/* Message */
.log-message {
    margin-top: 6px;

    font-size: 13px;
    line-height: 1.5;
    color: #6b7280;

    max-width: 700px;
    word-break: break-word;
}

/* Right Side */
.log-right {
    display: flex;
    flex-direction: column;
    align-items: flex-end;
    gap: 12px;
}

/* Time */
.log-time {
    font-size: 12px;
    color: #9ca3af;
    white-space: nowrap;
}

/* View Detail Button */
.view-btn {
    border: none !important;
    border-radius: 999px !important;

    padding: 6px 14px !important;

    font-size: 12px !important;
    font-weight: 600 !important;

    background: #6366f1 !important;

    transition: all 0.2s ease;
}

.view-btn:hover {
    opacity: 0.9;
    transform: scale(1.03);
}

/* Mobile */
@media (max-width: 768px) {
    .log-item {
        flex-direction: column;
    }

    .log-right {
        width: 100%;
        flex-direction: row;
        justify-content: space-between;
        align-items: center;
    }

    .log-message {
        max-width: 100%;
    }
}
.view-all {
    font-family: inherit;
    font-size: 0.82rem;
    font-weight: 600;
    color: var(--accent);
    text-decoration: none;
    display: flex;
    align-items: center;
    gap: 0.3rem;
    transition: gap 0.2s ease;
}

.view-all:hover {
    gap: 0.5rem;
}

.view-all::after {
    content: '›';
    font-size: 1rem;
    line-height: 1;
}
</style>