<template>
    <div class="grid gap-1 md:gap-3">
        <div class="mb-2 lg:mb-0">
            <div :style="{ background: data_status[6]?.color }"
                class="text-white grow p-1 border-round-lg border-none cursor-pointer">
                <div class="flex justify-between align-items-center h-full">
                    <span class="ms-1"> {{ $t('Confirmed')}} </span>
                    <span class="border-round-lg text-center line-height-4 w-2rem h-2rem ml-2"
                        style="color:#fff;background: #00000021;">
                        {{ rs.reservation.total_confirmed }}
                    </span>
                </div>
            </div>
        </div>
        <div class="mb-2 lg:mb-0">
            <div :style="{ background: data_status[2]?.color }"
                class="text-white grow p-1 border-round-lg border-none cursor-pointer">
                <div class="flex justify-between align-items-center h-full">
                    <span class="ms-1">{{ $t('Reserved')}} </span>
                    <span class="border-round-lg text-center line-height-4 w-2rem h-2rem ml-2"
                        style="color:#fff;background: #00000021;">
                        {{ rs.reservation.reserved }}
                    </span>
                </div>
            </div>
        </div>
        <div class="mb-2 lg:mb-0">
            <div :style="{ background: data_status[0]?.color }"
                class="text-white grow p-1 border-round-lg border-none cursor-pointer">
                <div class="flex justify-between align-items-center h-full">
                    <span class="ms-1">{{ $t('Checked in')}}</span>
                    <span class="border-round-lg text-center line-height-4 w-2rem h-2rem ml-2"
                        style="color:#fff;background: #00000021;">
                        {{ rs.reservation.total_checked_in }}
                    </span>
                </div>
            </div>
        </div>
        <div class="mb-2 lg:mb-0">
            <div :style="{ background: data_status[1]?.color }"
                class="text-white grow p-1 border-round-lg border-none cursor-pointer">
                <div class="flex justify-between align-items-center h-full">
                    <span class="ms-1">{{ $t('Checked Out')}}</span>
                    <span class="border-round-lg text-center line-height-4 w-2rem h-2rem ml-2"
                        style="color:#fff;background: #00000021;">
                        {{ rs.reservation.total_checked_out }}
                    </span>
                </div>
            </div>
        </div>
        <div class="mb-2 lg:mb-0">
            <div :style="{ background: data_status[3]?.color }"
                class="text-white grow p-1 border-round-lg border-none cursor-pointer">
                <div class="flex justify-between align-items-center h-full">
                    <span class="ms-1">{{ $t('No Show')}}</span>
                    <span class="border-round-lg text-center line-height-4 w-2rem h-2rem ml-2"
                        style="color:#fff;background: #00000021;">
                        {{ rs.reservation.total_no_show }}
                    </span>
                </div>
            </div>
        </div>
        <div class="mb-2 lg:mb-0">
            <div :style="{ background: data_status[4]?.color }"
                class="text-white grow p-1 border-round-lg border-none cursor-pointer">
                <div class="flex justify-between align-items-center h-full">
                    <span class="ms-1">{{ $t('Cancelled')}}</span>
                    <span class="border-round-lg text-center line-height-4 w-2rem h-2rem ml-2"
                        style="color:#fff;background: #00000021;">
                        {{ rs.reservation.total_cancelled }}
                    </span>
                </div>
            </div>
        </div>
        <div class="mb-2 lg:mb-0">
            <div :style="{ background: data_status[5]?.color }"
                class="text-white grow p-1 border-round-lg border-none cursor-pointer">
                <div class="flex justify-between align-items-center h-full">
                    <span class="ms-1">{{ $t('Void')}}</span>
                    <span class="border-round-lg text-center line-height-4 w-2rem h-2rem ml-2"
                        style="color:#fff;background: #00000021;">
                        {{ rs.reservation.total_void }}
                    </span>
                </div>
            </div>
        </div>
        <div class="mb-2 lg:mb-0">
            <div class="text-white grow p-1 border-round-lg border-none cursor-pointer bg-primary-600">
                <div class="flex justify-between align-items-center h-full">
                    <span class="ms-1">{{ $t('Total Stay')}}</span>
                    <span class="border-round-lg text-center line-height-4 w-2rem h-2rem ml-2"
                        style="color:#fff;background: #00000021;">
                        {{ rs.reservation.total_reservation_stay }}
                    </span>
                </div>
            </div>
        </div>
        <div class="mb-2 lg:mb-0">
            <div class="text-white grow p-1 border-round-lg border-none cursor-pointer bg-yellow-400">
                <div class="flex justify-between align-items-center h-full">
                    <span class="ms-1">{{ $t('Total Active Stay')}}</span>
                    <span v-if="rs.reservationStays"   class="border-round-lg text-center line-height-4 w-2rem h-2rem ml-2"
                        style="color:#fff;background: #00000021;">
                        {{ rs.reservationStays.filter(r=>r.is_active_reservation == 1).length }}
                    </span>
                </div>
            </div>
        </div>

        <div class="mb-2 lg:mb-0">
            <div class="text-white grow p-1 border-round-lg border-none cursor-pointer bg-cyan-500">
                <div class="flex justify-between align-items-center h-full">
                    <span class="ms-1">{{ $t('Pickup')}}</span>
                    <span class="border-round-lg text-center line-height-4 w-2rem h-2rem ml-2"
                        style="color:#fff;background: #00000021;">
                        <span v-if="rs.reservationStays">
                            {{ rs.reservationStays.filter(r=>r.require_pickup && r.is_active_reservation == 1).length }}
                        </span>
                        <span v-else>0</span>
                    </span>
                </div>
            </div>
        </div>
        <div class="mb-2 lg:mb-0">
            <div class="text-white grow p-1 border-round-lg border-none cursor-pointer bg-pink-500">
                <div class="flex justify-between align-items-center h-full">
                    <span class="ms-1">{{ $t('Drop Off')}}</span>
                    <span class="border-round-lg text-center line-height-4 w-2rem h-2rem ml-2"
                        style="color:#fff;background: #00000021;"> 
                        <span v-if="rs.reservationStays">
                            {{ rs.reservationStays.filter(r=>r.require_drop_off && r.is_active_reservation == 1).length }}
                        </span>
                        <span v-else>0</span>
                    </span>
                </div>
            </div>
        </div>
    </div>
</template>
<script setup>
import { ref, inject, getDocList } from '@/plugin';
import {i18n} from '@/i18n';
const { t: $t } = i18n.global; 
const data_status = ref([])
getDocList('Reservation Status', {
    fields: ['name', 'color'],
    orderBy: {
        field: 'sort_order',
        order: 'asc',
    },
})
    .then((docs) => {
        data_status.value = docs
    })

const rs = inject('$reservation')



</script>
