<template lang="">
    <div class="pt-2 pb-1 border-b border-color-edoor">
        <div class="flex justify-between align-items-center mb-1">
            <div class="flex align-items-center h-full font-medium">{{title}}</div>
            <div class="flex-grow px-1">
                
            </div>
            <div class="px-2 py-1 font-medium border-round-lg text-white badge-td-guest">
                <slot></slot>
            </div>
        </div>
        <ProgressBar v-if="progress != null" :value="progress" class="progress-perentage" :showValue="false"></ProgressBar>
    </div>
</template>
<script setup>
import { ref, computed } from "@/plugin"
import ProgressBar from 'primevue/progressbar';
const data = ref([])
const props = defineProps({
    title: String,
    value: {
        type: Number,
        default: null
    },
    totalValue: {
        type: Number,
        default: null
    }
})
const progress = computed(() => {
    if (props.totalValue != null && props.value != null) {
        return (props.value / props.totalValue) * 100
    } else {
        return null
    }

})
</script>
<style>
.progress-perentage {
    height: 3px !important;
    border-radius: 2px !important;
}
</style>