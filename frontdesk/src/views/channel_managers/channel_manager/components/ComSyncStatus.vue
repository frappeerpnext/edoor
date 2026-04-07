<template>
    <ComPanel title="Recent Sync Logs" :viewAll="true" class="sys-date h-17rem md:h-full mt-2">
        <div class="logs"> 
            <div class="filters">
                <button class="active">All</button>
                <button>Success</button>
                <button>Failed</button>
            </div>

            <div class="log-item">
                <div>
                    <div class="log-status success">SUCCESS</div>
                    <div class="log-message">Availability synced successfully for 150 dates</div>
                </div>
                <div class="log-time">2026-03-19 07:15:00</div>
            </div>

            <div class="log-item">
                <div>
                    <div class="log-status failed">FAILED</div>
                    <div class="log-message">Connection timeout while fetching property info</div>
                </div>
                <div class="log-time">2026-03-19 06:45:00</div>
            </div>

            <div class="log-item">
                <div>
                    <div class="log-status success">SUCCESS</div>
                    <div class="log-message">Service codes updated from Exely</div>
                </div>
                <div class="log-time">2026-03-19 05:30:00</div>
            </div>

            <div class="log-item">
                <div>
                    <div class="log-status pending">PENDING</div>
                    <div class="log-message">Syncing room rates for April 2026</div>
                </div>
                <div class="log-time">2026-03-19 04:15:00</div>
            </div>

            <div class="log-item">
                <div>
                    <div class="log-status success">SUCCESS</div>
                    <div class="log-message">Initial property handshake complete</div>
                </div>
                <div class="log-time">2026-03-19 03:00:00</div>
            </div>
        </div>
    </ComPanel>
</template>
<style scoped>
.container {
    display: flex;
    gap: 40px;
    flex-wrap: wrap;
}

/* Services Table */
.services {
    background-color: #fff;
    border-radius: 12px;
    padding: 20px;
    flex: 1;
    min-width: 300px;
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
}

.services input {
    width: 100%;
    padding: 10px 15px;
    border-radius: 8px;
    border: 1px solid #ddd;
    margin-bottom: 20px;
    font-size: 0.9rem;
}

table {
    width: 100%;
    border-collapse: collapse;
}

th,
td {
    text-align: left;
    padding: 12px 10px;
}

th {
    font-weight: 600;
    font-size: 0.95rem;
    color: #666;
    border-bottom: 1px solid #eee;
}

td {
    font-size: 0.9rem;
    vertical-align: top;
}

.code {
    background-color: #f0f2f5;
    padding: 2px 6px;
    border-radius: 6px;
    font-family: monospace;
    font-size: 0.85rem;
}

.category {
    font-weight: 600;
}

.category.standard {
    color: #22c55e;
}

.category.deluxe {
    color: #6366f1;
}

.category.suite {
    color: #f97316;
}

/* Recent Logs */
.logs { 
    border-radius: 12px;
    padding: 20px;
    flex: 1;
    min-width: 300px; 
}

.log-item {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    padding: 15px 0;
    border-bottom: 1px solid #eee;
}

.log-item:last-child {
    border-bottom: none;
}

.log-status {
    font-weight: 600;
    margin-bottom: 4px;
}

.log-message {
    font-size: 0.9rem;
    color: #555;
}

.log-time {
    font-size: 0.8rem;
    color: #aaa;
    white-space: nowrap;
    margin-left: 10px;
}

.success {
    color: #22c55e;
}

.failed {
    color: #ef4444;
}

.pending {
    color: #fbbf24;
}

/* Filter Buttons */
.filters {
    display: flex;
    gap: 10px;
    margin-bottom: 15px;
}

.filters button {
    padding: 6px 12px;
    border: none;
    border-radius: 6px;
    background-color: #f0f2f5;
    cursor: pointer;
    font-size: 0.85rem;
    transition: all 0.2s;
}

.filters button.active,
.filters button:hover {
    background-color: #6366f1;
    color: white;
}
</style>