<template>  
    <div class="status-item align-items-center" :class="isAuthenticated ? 'success' : 'error'">
        <template v-if="isAuthenticated">
             <div class="icon">
                <i class="pi pi-check" style="color: white"></i>
            </div>
        </template>
        <template v-else>
            <div class="icon" style="background: #ef4444;">
                <i class="pi pi-times" style="color: white"></i>
            </div>
        </template>  
        <div class="status-content">
            <div class="font-bold">{{label || 'Label'}}</div>
            <span>{{ valueData }} — {{status}}</span>
        </div>
    </div>  
</template>
<script setup>
const props = defineProps({
    label: String,
    valueData: [String, Number],
    status: String,
    isAuthenticated: {
        type: Boolean,
        default: false
    }
})
</script>
<style scoped> 
.status-item {
    display: flex;
    align-items: flex-start;
    gap: 12px;
    padding: 14px 16px;
    border-radius: 12px;
    margin-bottom: 12px;
    font-size: 14px;
}

.status-icon {
    width: 22px;
    height: 22px;
    flex-shrink: 0;
}

.status-content strong {
    display: block;
    font-weight: 600;
    margin-bottom: 2px;
}

.status-content span {
    font-size: 13px;
    opacity: 0.85;
}

/* Success */
.success {
    background: linear-gradient(135deg, #e6f9f0, #f3fffa);
    border: 1px solid #b7f0d1;
}

.success .icon {
    background: #22c55e;
    color: white;
}

/* Error */
.error {
    background: linear-gradient(135deg, #ffecec, #fff5f5);
    border: 1px solid #ffc9c9;
}

.error .icon {
    background: #ef4444;
    color: white;
}

/* ICON */
.icon {
    width: 26px;
    height: 26px;
    border-radius: 50%;
    font-size: 14px;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
    font-weight: bold;
}
</style>