<template>
    <div style="min-width: 250px;">
        <slot></slot>
        <ComOverlayPanelFooter v-if="!hideFooter" :loading="loading" @onSave="onClickSave" @onClose="onClickCancel"></ComOverlayPanelFooter>
    </div>
</template>
<script setup>
    const emit = defineEmits(['onSave', 'onCancel'])
    const props = defineProps({
        hideFooter: {
            type: Boolean,
            default: false
        },
        loading: {
            type: Boolean,
            defualt: false
        },
    })
    function onClickSave(){
        emit('onSave')
    }
    function onClickCancel(){
        emit('onCancel')
    }
</script>
<style lang="">
    
</style>