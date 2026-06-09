<template>
    <div class="h-full w-6" style="height: 33rem !important;">
        <div class="card h-full" style="border-radius: 30px !important;">
            <div class="card-header">
                <div class="title">{{ $t('Recent bookings') }}</div>
            </div>

            <table>
                <thead>
                    <tr>
                        <th>{{ $t('Booking ID') }}</th>
                        <th>{{ $t('Channel ID') }}</th>
                        <th class="text-center">{{ $t('Nights / Room') }}</th>
                        <th>{{ $t('Channel') }}</th>
                        <th>{{ $t('Room') }}</th>
                        <th>{{ $t('Status') }}</th>
                    </tr>
                </thead>

                <tbody>
                    <tr v-for="booking in data" :key="booking.name">
                        <td>
                            <Button class="link_line_action1"
                                @click="onOpenLink('view_reservation_detail', booking.name)" link>
                                {{ booking.name }}

                            </Button>
                        </td>
                        <td>{{ booking.channel_manager_booking_id }}</td>
                        <td class="text-center">{{ booking.room_nights }} / {{ booking.total_active_reservation_stay }}
                        </td>
                        <td>{{ booking.business_source }}</td>
                        <td> <span v-tippy="booking.room_types">{{ booking.room_type_alias }}</span></td>
                        <td class="status">
                            <span :style="{ backgroundColor: booking.status_color }"
                                class="border-round-3xl py-1 px-2 text-white">{{ booking.reservation_status }}</span>
                        </td>
                    </tr>
                </tbody>
            </table>
        </div>
    </div>
</template>
<script setup>

const props = defineProps({
    data: Object
})
function onOpenLink(action, name) {
    window.postMessage(action + '|' + name, '*')
}
</script>
<style scoped>
.container {
    display: flex;
    gap: 20px;
    padding: 30px;
}

.card {
    flex: 1;
    background: #fff;
    border-radius: 14px;
    padding: 20px;
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.06);
}

.card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 15px;
}

.title {
    font-size: 16px;
    font-weight: 600;
}



table {
    width: 100%;
    border-collapse: collapse;
    font-size: 13px;
}

th {
    text-align: left;
    color: #94a3b8;
    font-weight: 500;
    padding-bottom: 8px;
}

td {
    padding: 8px 0;
    border-top: 1px solid #f1f5f9;
}

.status {
    display: flex;
    align-items: center;
    gap: 6px;
    font-weight: 500;
}
</style>