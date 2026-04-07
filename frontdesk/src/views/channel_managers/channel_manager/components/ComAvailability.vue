<template>
    <!-- Standard -->
    <div class="availability-item align-items-center" :class="isRoomMapping ? 'success' : 'warning'">
        <template v-if="isRoomMapping">
             <div class="icon">
                <i class="pi pi-times" style="color: white"></i>
            </div>
        </template>
        <template v-else>
            <div class="icon">
                <i class="pi pi-check" style="color: white"></i>
            </div>
        </template>
        <div class="content">
            <div class="font-bold">{{ $t(roomTypeName) }} - ({{ roomTypeCode }})</div>
            <div>
                <template v-if="isRoomMapping">
                    <span>{{ totalRoom }} Rooms</span>
                </template>
                <template v-else>
                    <span>{{$t('No code assigned')}}</span>
                </template>
            </div>
            <div>
                <template v-if="isRoomMapping">
                    <span class="highlight">{{ dayCover }} days covered</span>
                </template>
                <template v-else>
                    <span class="warning-text">{{$t('Will be skipped')}}</span>
                </template>
            </div>
        </div>
    </div> 
</template>
<script setup>
const props = defineProps({
    roomTypeName: String,
    roomTypeCode: String,
    totalRoom: [String, Number],
    dayCover: [String, Number],
    isRoomMapping: {
        type: Boolean,
        default: true
    }
})
</script>
<style scoped>
.availability-item {
    display: flex;
    gap: 14px;
    padding: 16px;
    border-radius: 12px;
    margin-bottom: 12px;
    align-items: flex-start;
    transition: all 0.2s ease;
}

.availability-item:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 18px rgba(0, 0, 0, 0.06);
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

/* CONTENT */
.content strong {
    display: block;
    font-weight: 600;
    margin-bottom: 4px;
}

.content span {
    display: block;
    font-size: 13px;
    opacity: 0.85;
}

/* SUCCESS */
.success {
    background: linear-gradient(135deg, #e6f9f0, #f3fffa);
    border: 1px solid #b7f0d1;
}

.success .icon {
    background: #22c55e;
    color: white;
}

.success .highlight {
    color: #16a34a;
    font-weight: 500;
}

/* WARNING */
.warning {
    background: linear-gradient(135deg, #fff4e5, #fff9f0);
    border: 1px solid #ffd8a8;
}

.warning .icon {
    background: #f59e0b;
    color: white;
}

.warning-text {
    color: #d97706;
    font-weight: 500;
}
</style>