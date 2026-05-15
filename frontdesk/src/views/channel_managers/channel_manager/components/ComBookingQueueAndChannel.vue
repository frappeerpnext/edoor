<template>
    <ComPanel title="" :viewAll="true" class="sys-date h-17rem md:h-full ">
        <div class="grid">

        <!-- Recent Bookings -->
        <div class="col-6">
            <div class="card">
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
                        <tr v-for="booking in recentReservationData" :key="booking.name"> 
                            <td>
                                <Button class="link_line_action1" @click="onOpenLink('view_reservation_detail', booking.name)" link>
                                    {{ booking.name }} 
                                </Button>
                            </td>
                            <td>{{ booking.channel_manager_booking_id }}</td>
                            <td class="text-center">{{ booking.room_nights }} / {{ booking.total_active_reservation_stay }}</td>
                            <td>{{ booking.business_source }}</td>
                            <td> <span v-tippy="booking.room_types">{{ booking.room_type_alias }}</span></td>
                            <td class="status">
                                <span :style="{ backgroundColor: booking.status_color }" class="border-round-3xl py-1 px-2 text-white">{{ booking.reservation_status }}</span>
                            </td>
                        </tr> 
                    </tbody>
                </table> 
            </div>
        </div>

        <!-- Bookings by channel -->
        <div class="col-6">
            <div class="card">
                <div class="card-header">
                    <div class="title">Bookings by channel</div>
                </div>

                <div class="progress-item">
                    <div class="progress-label">
                        <span>Booking.com</span>
                        <span>21</span>
                    </div>
                    <div class="progress-bar">
                        <div class="progress-fill" style="width: 80%"></div>
                    </div>
                </div>

                <div class="progress-item">
                    <div class="progress-label">
                        <span>Expedia</span>
                        <span>11</span>
                    </div>
                    <div class="progress-bar">
                        <div class="progress-fill" style="width: 50%"></div>
                    </div>
                </div>

                <div class="progress-item">
                    <div class="progress-label">
                        <span>Agoda</span>
                        <span>8</span>
                    </div>
                    <div class="progress-bar">
                        <div class="progress-fill" style="width: 40%"></div>
                    </div>
                </div>

                <div class="progress-item">
                    <div class="progress-label">
                        <span>Direct / PMS</span>
                        <span>7</span>
                    </div>
                    <div class="progress-bar">
                        <div class="progress-fill" style="width: 35%"></div>
                    </div>
                </div>
            </div>
        </div>
        </div>
    </ComPanel>

</template>
<script setup>
import { useCMDashboard } from '../hooks/useCMDashboard'; 


const {
    recentReservationData
 } = useCMDashboard();

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
        box-shadow: 0 8px 24px rgba(0,0,0,0.06);
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

    .badge {
        background: #e0ecff;
        color: #3b82f6;
        font-size: 12px;
        padding: 4px 10px;
        border-radius: 20px;
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

    .dot {
        width: 8px;
        height: 8px;
        border-radius: 50%;
    }

    .green { background: #22c55e; }
    .yellow { background: #f59e0b; }
    .red { background: #ef4444; }
    .orange { background: #fb923c; }

    .btn {
        margin-top: 15px;
        border: 1px solid #e2e8f0;
        background: transparent;
        padding: 10px;
        border-radius: 10px;
        width: 100%;
        cursor: pointer;
        font-size: 13px;
        transition: 0.2s;
    }

    .btn:hover {
        background: #f1f5f9;
    }

    /* Progress bars */
    .progress-item {
        margin-bottom: 14px;
    }

    .progress-label {
        display: flex;
        justify-content: space-between;
        font-size: 13px;
        margin-bottom: 4px;
    }

    .progress-bar {
        height: 6px;
        background: #e5e7eb;
        border-radius: 10px;
        overflow: hidden;
    }

    .progress-fill {
        height: 100%;
        background: linear-gradient(90deg, #4ade80, #22c55e);
        border-radius: 10px;
    }
</style>