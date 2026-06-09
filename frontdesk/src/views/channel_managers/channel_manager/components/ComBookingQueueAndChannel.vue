<template>
    <ComPanel :viewAll="true" class="mt-3" style="border-radius: 30px !important;">
        <div class="p-3 flex h-full w-full gap-3"> 
            <!-- Recent Bookings --> 
            <ComRecentBooking :data="recentReservationData" /> 
            <!-- Bookings by channel -->
            <ComBookingByChannel />
        </div>
    </ComPanel> 
</template>
<script setup>
import { useCMDashboard } from '../hooks/useCMDashboard';
import ComRecentBooking from '@/views/channel_managers/channel_manager/components/ComRecentBooking.vue';
import ComBookingByChannel from '@/views/channel_managers/channel_manager/components/ComBookingByChannel.vue';

const {
    recentReservationData
} = useCMDashboard();

function onOpenLink(action, name) {
    window.postMessage(action + '|' + name, '*')
}
</script> 