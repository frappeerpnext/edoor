<template>
    <ComDialogContent  :loading="loading" :hideButtonOK="true" @onClose="onClose()" :hideButtonClose="false">

        <div class="card-body">
            <div class="cm-section__label">
                <i class="pi pi-building" />
                <span>{{$t('Property Identity')}}</span>
            </div>
            <div class="task-card mt-3">
                <div class="">
                    <div class="info-grid">
                        <div class="info-item">
                            <div class="info-label">{{ $t('Property Code') }}</div>
                            <div class="info-value">{{ data?.property_code }}</div>
                        </div>
                        <div class="info-item">
                            <div class="info-label">{{ $t('Provider') }}</div>
                            <div class="info-value">
                                {{ data?.provider }}
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <div class="cm-section__label">
                <i class="pi pi-arrow-right-arrow-left" />
                <span>{{$t('Data Flow Configuration')}}</span> 
            </div> 

            <div class="grid cm-section__grid mb-5 mt-3">
            <div v-for="flow in rightFields" :key="flow.key" class="col-12 sm:col-6 lg:col-3">
                <div class="cm-flow-card border-1">
                <div class="cm-flow-card__icon">
                    <i class="pi pi-lock" />
                </div>
                <div class="cm-flow-card__info">
                    <span class="cm-flow-card__label">{{ flow.label }}</span>
                    <span class="cm-flow-card__value">{{ data?.[flow.key] }}</span>
                </div>
                </div>
            </div>
            </div>

            <div class="cm-section__label">
                <i class="pi pi-lock" />
                <span>{{$t('Restriction Settings')}}</span> 
            </div> 

            <div class="grid mb-5 mt-3">
                <div class="col-3" v-for="r in restrictionOptions" :key="r.key">
                    <div class="cm-restrict border border-round-3xl flex gap-2 align-items-center">
                        <i class="pi pi-check-circle" />
                        <span>{{r.label}}</span>
                    </div>
                </div>
            </div>

            <div class="cm-section__label">
                <i class="pi pi-box" />
                <span>{{$t('Room Type Mapping')}}</span> 
            </div> 

            <div class="mb-5 mt-3">
                <ComRoomTypeMappingInfo />
            </div>

            <div class="cm-section__label">
                <i class="pi pi-dollar" />
                <span>{{$t('Rate Plan Mapping')}}</span> 
            </div> 

            <div class="mb-5 mt-3">
                <ComRatePlanMappingInfo />
            </div>

            <div class="cm-section__label">
                <i class="pi pi-wallet" />
                <span>{{$t('Payment Type Mapping')}}</span> 
            </div> 

            <div class="mb-5 mt-3">
                <ComPaymentTypeMappingInfo />
            </div>

            <div class="cm-section__label">
                <i class="pi pi-receipt" />
                <span>{{$t('Service Mapping')}}</span> 
            </div> 

            <div class="mb-5 mt-3">
                <ComServiceMappingInfo />
            </div>

            <div class="cm-section__label">
                <i class="pi pi-briefcase" />
                <span>{{$t('Business Source Mapping')}}</span> 
            </div> 

            <div class="mb-5 mt-3">
                <ComBusinessSourceMappingInfo />
            </div>
        </div>
    </ComDialogContent>
</template>

<script setup>
import { computed, inject } from 'vue'
import Accordion from 'primevue/accordion';
import AccordionTab from 'primevue/accordiontab';

import { useCMDashboard } from '@/views/channel_managers/channel_manager/hooks/useCMDashboard.js'
import ComBoxStayInformation from '@/views/reservation/components/ComBoxStayInformation.vue'
import ComRoomTypeMappingInfo from '@/views/channel_managers/channel_manager/components/ComRoomTypeMappingInfo.vue'
import ComRatePlanMappingInfo from '@/views/channel_managers/channel_manager/components/ComRatePlanMappingInfo.vue'
import ComPaymentTypeMappingInfo from '@/views/channel_managers/channel_manager/components/ComPaymentTypeMappingInfo.vue'
import ComServiceMappingInfo from '@/views/channel_managers/channel_manager/components/ComServiceMappingInfo.vue'
import ComBusinessSourceMappingInfo from '@/views/channel_managers/channel_manager/components/ComBusinessSourceMappingInfo.vue'

const dialogRef = inject("dialogRef");
const { channelManagerData } = useCMDashboard()

const data = computed(() => {
    return channelManagerData.value
}) 

const rightFields = computed(() => {
    const fields = [
        {
            key: 'rooms_availability',
            label: 'Rooms Availability'
        },
        {
            key: 'prices_for_accommodation',
            label: 'Prices for Accommodation'
        },
        {
            key: 'prices_for_extra_services',
            label: 'Prices for extra services'
        },
        {
            key: 'restrictions',
            label: 'Restrictions'
        },
    ]

    return fields.filter(field => data.value?.[field.key])
})


const restrictionOptions = computed(() => {
    const fields = [
        {
            key: 'closed',
            label: 'Close'
        },
        {
            key: 'minlos',
            label: 'MinLOS'
        },
        {
            key: 'minlosarrival',
            label: 'MinLosArrival'
        },
        {
            key: 'fullpatternlos',
            label: 'FullPatternLos'
        },
        {
            key: 'maxlos',
            label: 'MaxLos'
        },
        {
            key: 'maxlosarrival',
            label: 'MaxLosArrival'
        },
        {
            key: 'minadvbooking',
            label: 'MinAdvBooking'
        },
        {
            key: 'maxadvbooking',
            label: 'MaxAdvBooking'
        },
        {
            key: 'cta',
            label: 'Cta'
        },
        {
            key: 'ctd',
            label: 'Ctd'
        }
    ]

    return fields.filter(field => data.value?.[field.key])

})

const onClose = () => { 
    dialogRef.value.close(true)
}
</script>
<style>
:root {
  --cm-bg: #0f1623;
  --cm-surface: #161e2e;
  --cm-surface-2: #1d2842;
  --cm-border: rgba(255,255,255,0.07);
  --cm-accent: #3b82f6;
  --cm-accent-glow: rgba(59,130,246,0.15);
  --cm-teal: #0ea5e9;
  --cm-green: #10b981;
  --cm-amber: #f59e0b;
  --cm-text: #e2e8f0;
  --cm-text-muted: #64748b;
  --cm-text-dim: #94a3b8;
  --cm-radius: 12px;
  --cm-radius-sm: 8px;
  /* --font-display: 'Syne', sans-serif;
  --font-body: 'DM Sans', sans-serif; */
}
.task-card {
    width: 100%;
    background: #ffffff;
    border-radius: 28px;
    /* overflow: hidden; */
    transition: all 0.2s ease;
}

.card-body {
    padding: 24px 28px 28px 28px;
}

.info-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 18px 24px;
    margin-bottom: 28px;
}

.info-item {
    display: flex;
    flex-direction: column;
    gap: 6px;
}

.info-label {
    font-size: 0.75rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    color: #64748b;
    display: flex;
    align-items: center;
    gap: 6px;
}

.info-value {
    font-size: 1rem;
    font-weight: 500;
    color: #0f172a;
    background: #fafcff;
    padding: 8px 0;
    border-bottom: 1px dashed #e2e8f0;
    padding-left: 10px;
}

.info-value.light-meta {
    color: #475569;
    font-size: 0.9rem;
}

.cm-section__label {
    display: flex;
    align-items: center;
    gap: 8px;
    font-family: var(--font-display);
    font-size: 12px;
    font-weight: 600;
    letter-spacing: 1px;
    text-transform: uppercase;
    color: var(--cm-text-muted);
}
.cm-flow-card {
  background: #f4f5fa;
  border: 1px solid var(--cm-border);
  border-radius: var(--cm-radius);
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 10px;
  position: relative;
  overflow: hidden;
  transition: transform 0.15s, box-shadow 0.15s;
}
.cm-flow-card__icon {
  width: 34px; height: 34px;
  border-radius: 8px;
  display: flex; align-items: center; justify-content: center;
  font-size: 14px;
}
 
.cm-flow-card__icon { background: rgba(59,130,246,0.12); color: var(--cm-accent); } 


.cm-flow-card__info { display: flex; flex-direction: column; gap: 3px; }
.cm-flow-card__label { font-size: 11px; color: var(--cm-text-muted); font-weight: 500; }
.cm-flow-card__value { font-size: 13px; font-weight: 600; }
.cm-flow-card__badge { position: absolute; top: 12px; right: 12px; }
.cm-restrict {
    background: #f4f5fa;
    padding: 10px;
    border-color: rgba(59,130,246,0.25) !important;
}
</style>