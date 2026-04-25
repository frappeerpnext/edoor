<template>
    <div>
        <!-- {{ data }} -->
        <div class="notif-container">
            <div class="notif-list">
                <div v-if="data?.length > 0" v-for="d in data" @click="onViewLogDetail(d.name)" class="cursor-pointer">
                    <div class="notif-item" :class="d.status == 'Success' ? 'success' : 'warning'">
                        <span class="icon">{{ d.status == 'Success' ? '✔' : '⚠' }}</span>
                        <div class="content">
                            <div class="title">{{ d.title }}</div>
                            <div class="time">
                                <ComTimeago :date="d.creation" />
                            </div>
                        </div>
                    </div>
                </div>
                <div v-else class="flex flex-column align-items-center w-full h-23rem justify-content-center">
                    <div
                        class="h-30rem align-items-center text-center flex justify-content-center align-content-center h-full">

                        <div>
                            <div>
                                <i class="pi pi-bell text-6xl" />
                            </div>

                            <strong>{{ $t('No Notification') }}</strong>
                            <p>
                                {{ $t(`There's no notification for you`) }}
                            </p>
                        </div>

                    </div>
                </div>
            </div>
        </div>



    </div>
</template>
<script setup>

const props = defineProps({
    data: Object
})
function onViewLogDetail(docname) {
    window.postMessage("view_channel_manager_sync_log|" + docname, "*")
}
</script>
<style scoped>
.notif-container {
    border-radius: 12px;
    overflow: hidden;
}

/* List */
.notif-list {
    max-height: 300px;
    overflow-y: auto;
    /* padding: 10px; */
}

/* Item */
.notif-item {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 10px;
    border-radius: 10px;
    transition: 0.2s;
    background: #eef2ff;
    margin-bottom: 10px;
}

.notif-item:hover {
    background: #f5f7fb;
}

/* Icon */
.icon {
    font-size: 16px;
}

/* Content */
.content .title {
    font-size: 14px;
    font-weight: 600;
}

.content .time {
    font-size: 11px;
    color: #999;
}

/* Status Colors */
.success .icon {
    color: #22c55e;
}

.warning .icon {
    color: #f59e0b;
}

.failed .icon {
    color: #ef4444;
}

/* Footer */
.footer {
    padding: 10px;
    border-top: 1px solid #eee;
}

.view-all {
    width: 100%;
    padding: 10px;
    background: #3b82f6;
    color: white;
    border: none;
    border-radius: 8px;
    cursor: pointer;
}
</style>