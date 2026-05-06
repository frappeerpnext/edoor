<template>  
<div class="status-item align-items-center" :class="statusClass">

    <!-- ICON -->
    <div class="icon">

        <template v-if="isAuthenticated">
            <i class="pi pi-check" style="color: white"></i>
        </template>

        <template v-else-if="loading">
            <ProgressSpinner
                strokeWidth="8"
                fill="transparent"
                animationDuration=".8s"
            />
        </template>

        <template v-else>
            <i class="pi pi-times" style="color: white"></i>
        </template>

    </div>

    <!-- CONTENT -->
    <div class="status-content">
        <div class="font-bold">{{ label || 'Label' }}</div>
        <span>
            {{ valueData }} — {{ loading ? 'Checking...' : status }}
        </span>
    </div>

</div>
</template>
<script setup>
import { ref, onMounted, inject, computed , watch } from '@/plugin'
const props = defineProps({
    label: String,
    valueData: [String, Number],
    status: String,
    isAuthenticated: {
        type: Boolean,
        default: false
    },
    loading: {
        type: Boolean,
        default: false
    }
})
const statusClass = computed(() => {
  if (props.loading) return 'warning'
  if (props.isAuthenticated) return 'success'
  return 'error'
})
import ProgressSpinner from 'primevue/progressspinner';
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
    transition: all 0.3s ease;
}

.success .icon {
    background: #22c55e;
    color: white;
}

/* Error */
.error {
    background: linear-gradient(135deg, #ffecec, #fff5f5);
    border: 1px solid #ffc9c9;
    transition: all 0.3s ease;
}

.error .icon {
    background: #ef4444;
    color: white;
}

/* Warning */
.warning {
    background: linear-gradient(135deg, #fff7e6, #fffdf5);
    border: 1px solid #ffe0a3;
    transition: all 0.5s ease;
}

.warning .icon {
    background: #f59e0b;
    color: white;
}
.status-item {
    transition: all 0.5s ease;
}

.status-item .icon {
    transition: transform 0.4s ease;
}

.status-item.success .icon {
    transform: scale(1.05);
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