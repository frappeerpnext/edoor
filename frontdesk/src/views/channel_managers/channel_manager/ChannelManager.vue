<template>
    <ComHeader>
        <template #start>
            <div class="flex">
                <div class="flex align-items-center justify-content-between w-full">
                    <div @click="onRefresh()" 
                        class="text-xl md:text-2xl white-space-nowrap">
                        {{ $t(`${channelManagerData.provider || ''} Channel Manager Dashboard`) }}
                    </div>
                </div>
            </div>
        </template>
        
        <template #end v-if="channelManagerData.initialized_data_upload == 1">

            <div class="flex gap-2 w-full justify-content-between md:justify-content-end">
                <Button class="w-full md:w-auto border-none" :label="$t('Retry Failed Sync')"
                    icon="pi pi-exclamation-circle" @click="onRetryFailedSync" />
                <Button class="w-full md:w-auto border-none" :label="$t('Reupload Data')"
                    icon="pi pi-exclamation-circle" @click="onReuploadData" />
            </div>
        </template>
    </ComHeader> 

    <component :is="currentCMComponent" />
    <!-- <ChannelManagerDashboard />
    <ComCMInit/> -->
</template>
<script setup>
import { onUnmounted, ref } from 'vue';
import { useCMDashboard } from './hooks/useCMDashboard'; 
import ChannelManagerDashboard from "@/views/channel_managers/channel_manager/ChannelManagerDashboard.vue"
import ComCMInit from "@/views/channel_managers/channel_manager/components/cm_initialize_step/ComCMInit.vue"

const { 
    resetData,
    channelManagerData,
    currentCMComponent
} = useCMDashboard();



onUnmounted(() => { 
    resetData()
})

</script>