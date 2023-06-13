<template>
    <div class="flex items-center justify-content-between py-3">
        <div class="header-title text-2xl">
            <slot name="start"></slot>
        </div>
        <div>
            <slot name="center"></slot>
        </div>
        <div class="flex gap-2">
            <slot name="end"></slot>
            <Button v-if="isRefresh" @click="onRefresh()" icon="pi pi-refresh" class="d-bg-set btn-inner-set-icon border-none"></Button>
        </div>
    </div>
</template>
<script setup>
const props = defineProps({
    isRefresh: {
        type: Boolean,
        default: false
    }
})
 const emit = defineEmits(['onRefresh'])
 function onRefresh(){
    emit('onRefresh')
 }
</script>
<style scoped>
    
</style>