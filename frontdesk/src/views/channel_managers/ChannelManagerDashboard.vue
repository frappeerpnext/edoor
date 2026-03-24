<template>
    <ComHeader>
        <template #start>
            <div class="flex">
                <div class="flex align-items-center justify-content-between w-full">
                    <div @click="onRefresh()" class="text-xl md:text-2xl white-space-nowrap">{{ $t('Exely Channel Manager Dashboard') }}</div>
                </div>
            </div>
        </template>
        <template #end>

            <div class="flex gap-2 w-full justify-content-between md:justify-content-end"> 
                <Button class="w-full md:w-auto border-none" :label="$t('Retry Failed Sync')" icon="pi pi-exclamation-circle" @click="onRetryFailedSync"/>
            </div>
        </template>
    </ComHeader>
    <template v-if="1!=1">
        <div class="grid">
            <div class="col-12 lg:col-6 xl:col-3">
                <KPISummaryCard :data="data.total_services" :title="$t('Total Service')" icon="pi-box"/>
            </div>
            <div class="col-12 lg:col-6 xl:col-3">
                <KPISummaryCard :data="data.total_room_types" :title="$t('Total Room Types')" icon="pi-building"/>
            </div>
            <div class="col-12 lg:col-6 xl:col-3">
                <KPISummaryCard :data="data.sync_success" :title="$t('Sync Success')" icon="pi-check-circle"/>  
            </div>  
            <div class="col-12 lg:col-6 xl:col-3">
                <KPISummaryCard :data="data.last_sync_time" :title="$t('last Sync Time')" icon="pi-clock"/>  
            </div>  
        </div>
        <div>
            <ComConnectedBusinessSource />
        </div>
        <div> 
            <ComSyncStatus /> 
        </div>
    </template>
    <template v-else>
        <div><Button class="w-full md:w-auto border-none" :label="$t('Initialize Channel Manager')" @click="onRetryFailedSync"/></div>
        
    </template>
</template>
<script setup>
    import KPISummaryCard from "@/views/channel_managers/components/KPISummaryCard.vue"
    import ComSyncStatus from "./components/ComSyncStatus.vue"
    import ComConnectedBusinessSource from "./components/ComConnectedBusinessSource.vue"
    import { ref, inject } from '@/plugin'
    const moment = inject("$moment")

    const data = ref({
        total_services: 10,
        total_room_types: 40,
        sync_success: 5,
        last_sync_time: moment().format('HH:mm:ss')
    })

    
</script>