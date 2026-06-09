<template>
    
    <Message :closable="false" severity="warn" class="warning-banner" v-if="data?.status == 'Warning' || data?.status == 'Fail'">
        <div class="warning-left">
            <div class="warning-content">
                <div class="warning-title font-bold text-2xl" v-if="data?.status == 'Warning'">
                    {{ data?.request_type }} - <comTimeAgo :date="data.creation"/>
                </div>

                <div class="warning-text">
                    {{data?.response_text}}
                </div>

            </div>
        </div>

        <Button class="border-0" @click="onViewLogDetail(data?.name)">
            View Sync Log
        </Button>
    </Message>
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
    if (arg.property = window.property.name && arg.action == "update_last_sync_log") {
        cmLastSyncLog.value = arg.data
    }
}

onMounted(() => {
    window.socket.on("ChannelManagerUpdate", socketEvent)
})

onUnmounted(() => {
    window.socket.off("ChannelManagerUpdate", socketEvent)
})

async function onViewLastSyncLog() {
    await app.utils.openDialog(ChannelManagerSyncLog, "Channel Manager Sync Log")

}

function onViewLogDetail(docname) {
    window.postMessage("view_channel_manager_sync_log|" + docname, "*")
}
</script>
<style scoped>
 
</style>