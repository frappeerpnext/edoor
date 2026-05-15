<template>
    <!-- Standard -->
    <div class="availability-item align-items-center" @click="$emit('onClick')">
           
             <div class="icon">
                 <slot name="status">
                
            </slot>
                
            </div>
     <div class="content p-3 border-round border-1 border-200 bg-gray-50 w-full">
    <!-- Header: Name and Code -->
    <div class="flex align-items-center justify-content-between mb-2">
        <div class="text-900 font-bold text-lg">
            {{ $t(roomTypeName) }} ({{ roomTypeCode }})
        </div>
        <!-- Status Indicator -->
        <Tag :severity="isRoomMapping ? 'success' : 'warning'" :value="isRoomMapping ? $t('Mapped') : $t('Unmapped')" />
    </div>

    <!-- Details Row -->
    <div class="flex gap-4 text-sm">
        <div class="flex align-items-center gap-2">
            <i class="pi pi-home text-400"></i>
            <span v-if="isRoomMapping" class="text-700 font-medium">{{ totalRoom }} Rooms</span>
            <span v-else class="text-400 italic">{{ $t('No code assigned') }}</span>
        </div>

        <div class="flex align-items-center gap-2 border-left-1 border-300 pl-4">
            <i class="pi pi-calendar text-400"></i>
            <span v-if="isRoomMapping" class="text-primary font-bold">{{ dayCover }} days covered</span>
            <span v-else class="text-orange-500 font-medium">{{ $t('Will be skipped') }}</span>
        </div>
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
    padding-left: 10px;
    border-radius: 12px;
    margin-bottom: 12px;
    align-items: flex-start;
    transition: all 0.2s ease;
    cursor: pointer;
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