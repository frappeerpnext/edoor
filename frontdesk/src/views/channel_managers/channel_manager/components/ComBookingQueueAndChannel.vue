<template>
    <ComPanel title="Connected Business Sources" :viewAll="true" class="sys-date h-17rem md:h-full ">
        <div class="grid">

        <!-- Recent Bookings -->
        <div class="card col-6">
            <div class="card-header">
                <div class="title">Recent bookings</div>
                <div class="badge">Live</div>
            </div>

            <table>
                <thead>
                    <tr>
                        <th>Booking ID</th>
                        <th>Channel</th>
                        <th>Room</th>
                        <th>Status</th>
                    </tr>
                </thead>

                <tbody>
                    <tr>
                        <td>20241226-3388</td>
                        <td>Booking.com</td>
                        <td>STD</td>
                        <td class="status">
                            <span class="dot green"></span> Confirmed
                        </td>
                    </tr>

                    <tr>
                        <td>20241226-3389</td>
                        <td>Expedia</td>
                        <td>DLX</td>
                        <td class="status">
                            <span class="dot yellow"></span> Pending
                        </td>
                    </tr>

                    <tr>
                        <td>20241226-3390</td>
                        <td>Direct</td>
                        <td>STD</td>
                        <td class="status">
                            <span class="dot green"></span> Confirmed
                        </td>
                    </tr>

                    <tr>
                        <td>20241226-3391</td>
                        <td>Agoda</td>
                        <td>STE</td>
                        <td class="status">
                            <span class="dot red"></span> Undelivered
                        </td>
                    </tr>

                    <tr>
                        <td>20241226-3392</td>
                        <td>Booking.com</td>
                        <td>DLX</td>
                        <td class="status">
                            <span class="dot orange"></span> Modified
                        </td>
                    </tr>
                </tbody>
            </table> 
        </div>

        <!-- Bookings by channel -->
        <div class="card col-6">
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
    </ComPanel>

</template>
<script setup></script>
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