<template>
    <div class="flex  flex-wrap gap-3">
        <div>
            <div :style="{ background: data_status[6]?.color }"
                class="text-white grow p-1 border-round-lg border-none cursor-pointer">
                <div class="flex justify-between align-items-center h-full">
                    <span class="ms-1">Confirmed </span>
                    <span class="border-round-lg text-center line-height-4 w-2rem h-2rem ml-2"
                        style="color:#fff;background: #00000021;">
                        {{ rs.reservation.total_confirmed }}
                    </span>
                </div>
            </div>
        </div>
        <div>
            <div :style="{ background: data_status[2]?.color }"
                class="text-white grow p-1 border-round-lg border-none cursor-pointer">
                <div class="flex justify-between align-items-center h-full">
                    <span class="ms-1">Reserved </span>
                    <span class="border-round-lg text-center line-height-4 w-2rem h-2rem ml-2"
                        style="color:#fff;background: #00000021;">
                        {{ rs.reservation.reserved }}
                    </span>
                </div>
            </div>
        </div>
        <div>
            <div :style="{ background: data_status[0]?.color }"
                class="text-white grow p-1 border-round-lg border-none cursor-pointer">
                <div class="flex justify-between align-items-center h-full">
                    <span class="ms-1">Checked in</span>
                    <span class="border-round-lg text-center line-height-4 w-2rem h-2rem ml-2"
                        style="color:#fff;background: #00000021;">
                        {{ rs.reservation.total_checked_in }}
                    </span>
                </div>
            </div>
        </div>
        <div>
            <div :style="{ background: data_status[1]?.color }"
                class="text-white grow p-1 border-round-lg border-none cursor-pointer">
                <div class="flex justify-between align-items-center h-full">
                    <span class="ms-1">Checked Out</span>
                    <span class="border-round-lg text-center line-height-4 w-2rem h-2rem ml-2"
                        style="color:#fff;background: #00000021;">
                        {{ rs.reservation.total_checked_out }}
                    </span>
                </div>
            </div>
        </div>
        <div>
            <div :style="{ background: data_status[3]?.color }"
                class="text-white grow p-1 border-round-lg border-none cursor-pointer">
                <div class="flex justify-between align-items-center h-full">
                    <span class="ms-1">No Show</span>
                    <span class="border-round-lg text-center line-height-4 w-2rem h-2rem ml-2"
                        style="color:#fff;background: #00000021;">
                        {{ rs.reservation.total_no_show }}
                    </span>
                </div>
            </div>
        </div>
        <div>
            <div :style="{ background: data_status[4]?.color }"
                class="text-white grow p-1 border-round-lg border-none cursor-pointer">
                <div class="flex justify-between align-items-center h-full">
                    <span class="ms-1">Cancelled</span>
                    <span class="border-round-lg text-center line-height-4 w-2rem h-2rem ml-2"
                        style="color:#fff;background: #00000021;">
                        {{ rs.reservation.total_cancelled }}
                    </span>
                </div>
            </div>
        </div>
        <div>
            <div :style="{ background: data_status[5]?.color }"
                class="text-white grow p-1 border-round-lg border-none cursor-pointer">
                <div class="flex justify-between align-items-center h-full">
                    <span class="ms-1">Void</span>
                    <span class="border-round-lg text-center line-height-4 w-2rem h-2rem ml-2"
                        style="color:#fff;background: #00000021;">
                        {{ rs.reservation.total_void }}
                    </span>
                </div>
            </div>
        </div>
        <div>
            <div class="text-white grow p-1 border-round-lg border-none cursor-pointer bg-primary-600">
                <div class="flex justify-between align-items-center h-full">
                    <span class="ms-1">Total Stay</span>
                    <span class="border-round-lg text-center line-height-4 w-2rem h-2rem ml-2"
                        style="color:#fff;background: #00000021;">
                        {{ rs.reservation.total_reservation_stay }}
                    </span>
                </div>
            </div>
        </div>
        <div>
            <div class="text-white grow p-1 border-round-lg border-none cursor-pointer bg-yellow-400">
                <div class="flex justify-between align-items-center h-full">
                    <span class="ms-1">Total Active Stay</span>
                    <span v-if="rs.reservationStays"   class="border-round-lg text-center line-height-4 w-2rem h-2rem ml-2"
                        style="color:#fff;background: #00000021;">
                        {{ rs.reservationStays.filter(r=>r.is_active_reservation == 1).length }}
                    </span>
                </div>
            </div>
        </div>

        <div>
            <div class="text-white grow p-1 border-round-lg border-none cursor-pointer bg-cyan-500">
                <div class="flex justify-between align-items-center h-full">
                    <span class="ms-1">Pickup</span>
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
        <div>
            <div class="text-white grow p-1 border-round-lg border-none cursor-pointer bg-pink-500">
                <div class="flex justify-between align-items-center h-full">
                    <span class="ms-1">Drop Off</span>
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


const hexToRgbA = (hex, alpha) => {
    let color;
    if (/^#([A-Fa-f0-9]{3}){1,2}$/.test(hex)) {
        color = hex.substring(1).split('');
        if (color.length == 3) {
            color = [color[0], color[0], color[1], color[1], color[2], color[2]];
        }
        color = '0x' + color.join('');
        return 'rgba(' + [(color >> 16) & 255, (color >> 8) & 255, color & 255].join(',') + ',' + alpha + ')';
    }
    throw new Error('Bad Hex');
}



</script>
