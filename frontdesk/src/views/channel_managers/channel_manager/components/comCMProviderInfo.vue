<template>
    <div class="integration-card cursor-pointer" @click="onOpenProviderDetails()">
        <div class="integration-content">
            <div class="integration-row">
                <div class="logo-box">
                    <Image :src="data.edoor_logo" :alt="data.name" :width="40" />
                </div>
                <div class="sync-icon">⇄</div>
                <div class="brand">
                    <Image :src="data.provider_logo" :alt="data.provider" :width="90" />
                </div>
            </div>
            <div class="property-code">
                {{ $t('Property Code') }}:
                <span>{{ data?.property_code }}</span>
            </div>
        </div>
    </div>
</template>
<script setup>
import { ref, onMounted, computed } from 'vue'
import Image from 'primevue/image';
import { useCMDashboard } from '@/views/channel_managers/channel_manager/hooks/useCMDashboard.js';
import ComProviderInfoDetail from '@/views/channel_managers/channel_manager/components/ComProviderInfoDetail.vue';
const {
    channelManagerData
} = useCMDashboard();

const data = computed(() => {
    return channelManagerData.value
})

async function onOpenProviderDetails() {
    await app.utils.openDialog(ComProviderInfoDetail, "Channel Manager Provider Details")
}


</script>
<style scoped>
.integration-card {
    position: relative;
    overflow: hidden;

    background: rgba(255, 255, 255, 0.75);
    backdrop-filter: blur(16px);

    border-radius: 30px;
    padding: 16px;

    border: 1px solid rgba(255, 255, 255, 0.7);

    box-shadow:
        0 12px 40px rgba(0, 0, 0, 0.06),
        inset 0 1px 1px rgba(255, 255, 255, 0.8);

    text-align: center;
    transition: 0.3s ease;
}

.integration-card:hover {
    transform: translateY(-4px);
    box-shadow:
        0 18px 35px rgba(0, 0, 0, 0.08),
        inset 0 1px 1px rgba(255, 255, 255, 0.8);
}

 
.integration-content {
    position: relative;
    z-index: 2;
}

.integration-row {
    display: flex;
    justify-content: center;
    align-items: center;
    gap: 26px;
    margin-bottom: 5px;
    flex-wrap: wrap;
}


.logo-box svg {
    width: 36px;
    height: 36px;
    stroke: white;
}

.sync-icon {
    font-size: 30px;
    font-weight: 700;
    color: #64748b;
}

.brand {
    font-size: 58px;
    font-weight: 800;
    letter-spacing: -2px;

    background: linear-gradient(135deg, #4c1d95, #7c3aed);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.property-code {
    display: inline-flex;
    align-items: center;
    gap: 10px;

    background: rgba(99, 102, 241, 0.08);
    color: #334155;

    padding: 6px 22px;
    border-radius: 999px;

    font-size: 14px;
    font-weight: 700;

    border: 1px solid rgba(99, 102, 241, 0.12);
}

.property-code span {
    color: #4f46e5;
    font-weight: 800;
}
</style>