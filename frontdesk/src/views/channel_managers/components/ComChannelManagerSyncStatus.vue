<template>
    <div class="sync-container">
        <div class="sync-header">
            <h2>Channel Manager Sync Status</h2>
        </div>

        <div class="sync-list">

            <div class="sync-card success">
                <div class="sync-left">
                    <span class="sync-title">Prices Update</span>
                    <span class="sync-provider">Exely</span>
                </div>
                <div class="sync-right">
                    <span class="sync-status">Success</span>
                    <span class="sync-time">2026-04-22 16:55</span>
                </div>
            </div>

            <div class="sync-card success">
                <div class="sync-left">
                    <span class="sync-title">Restriction Update</span>
                    <span class="sync-provider">Exely</span>
                </div>
                <div class="sync-right">
                    <span class="sync-status">Success</span>
                    <span class="sync-time">2026-04-22 16:55</span>
                </div>
            </div>

            <div class="sync-card success">
                <div class="sync-left">
                    <span class="sync-title">Availability Update</span>
                    <span class="sync-provider">Exely</span>
                </div>
                <div class="sync-right">
                    <span class="sync-status">Success</span>
                    <span class="sync-time">2026-04-22 16:55</span>
                </div>
            </div>

        </div>
    </div>
    <div>Channel manger sync status all status</div>
    {{ data }}
</template>
<script setup>
import { onMounted, ref } from 'vue';

const data = ref()
const property = JSON.parse(localStorage.getItem("edoor_property"))
async function getData() {
    const res = await app.getApi("edoor.channel_managers.utils.get_all_cm_sync_status", {
        property: property.name
    })
    if (res.data) {
        data.value = res.data
    }
}

onMounted(async () => {
    await getData()
})

</script>
<style scoped>
.sync-container {
    width: 600px;
    margin: 30px auto;
    background: #fff;
    border-radius: 12px;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05);
    overflow: hidden;
}

.sync-header {
    padding: 16px 20px;
    border-bottom: 1px solid #eee;
    background: #fafafa;
}

.sync-header h2 {
    margin: 0;
    font-size: 18px;
    color: #333;
}

.sync-list {
    max-height: 350px;
    overflow-y: auto;
}

.sync-card {
    display: flex;
    justify-content: space-between;
    padding: 14px 20px;
    border-bottom: 1px solid #f0f0f0;
    transition: 0.2s;
}

.sync-card:hover {
    background: #f9fbff;
}

.sync-left {
    display: flex;
    flex-direction: column;
}

.sync-title {
    font-weight: 600;
    color: #333;
}

.sync-provider {
    font-size: 12px;
    color: #888;
}

.sync-right {
    text-align: right;
}

.sync-status {
    display: inline-block;
    padding: 4px 10px;
    border-radius: 20px;
    font-size: 12px;
    margin-bottom: 5px;
}

/* Status Colors */
.success .sync-status {
    background: #e6f7ec;
    color: #28a745;
}

.failed .sync-status {
    background: #fdecea;
    color: #dc3545;
}

.pending .sync-status {
    background: #fff4e5;
    color: #ff9800;
}

.sync-time {
    display: block;
    font-size: 11px;
    color: #aaa;
}
</style>