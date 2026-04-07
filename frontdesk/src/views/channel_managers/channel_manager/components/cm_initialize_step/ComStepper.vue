<template>
    <div class="step" :class="{ 'active': isActive }" >
        <div class="circle">{{ index }}</div>
        <p>{{ $t(title || '') }}</p>
    </div>

</template>
<script setup>
import { computed } from '@/plugin'
const emit = defineEmits(['onStepper']);
const props = defineProps({
    title: String,
    index: Number,
    activeIndex: Number  // Add this prop from parent
})

const isActive = computed(() => props.activeIndex === props.index);

 
</script>
<style scoped>
/* Stepper */ 
.step {
    text-align: center;
    z-index: 1;
    cursor: pointer;
}

.circle {
    width: 36px;
    height: 36px;
    border-radius: 50%;
    background: #e5e7eb;
    display: flex;
    align-items: center;
    justify-content: center;
    margin: auto;
    font-weight: 600;
    color: #6b7280;
}

.step.active .circle {
    background: linear-gradient(135deg, #6366f1, #4f46e5);
    color: white;
    box-shadow: 0 5px 12px rgba(99, 102, 241, 0.4);
}

.step p {
    font-size: 11px;
    margin-top: 8px;
    color: #9ca3af;
}
</style>