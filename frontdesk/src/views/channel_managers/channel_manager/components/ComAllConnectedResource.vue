<template>
    <ComPanel title="Connected Resource" :viewAll="true" border-rounded="border-round-3xl"
        class="sys-date hero-card relative overflow-hidden">
        <div class="resource-grid p-3">
            <ComConnectedResourceCard v-for="item in connectedResources" :key="item.label" :label="item.label"
                :value="channelManagerData?.[item.key]?.length" />
        </div>
    </ComPanel>
</template>

<script setup>
import { computed } from 'vue'
import ComConnectedResourceCard from '@/views/channel_managers/channel_manager/components/ComConnectedResourceCard.vue'
import { useCMDashboard } from '@/views/channel_managers/channel_manager/hooks/useCMDashboard.js'

const { channelManagerData } = useCMDashboard()

const connectedResources = computed(() => [
    { label: 'Business Source', key: 'business_source' },
    { label: 'Room Type', key: 'room_types' },
    { label: 'Rate Plan', key: 'rate_plans' },
    { label: 'Payment Type', key: 'payment_types' },
    { label: 'Service', key: 'services' },
    { label: 'Package', key: 'package_rule_mapping' }
])
</script>
<style scoped>
.resource-grid{
    display:grid;
    grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
    gap:10px;

    /* ADD THIS */
    grid-auto-rows: 1fr;
}
</style>