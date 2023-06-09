<template>
<div>
    <div style="min-width: 250px;">
        <span class="font-semibold text-lg mb-3">{{ title }}</span>
        <slot></slot>
        <ComOverlayPanelFooter v-if="!hideFooter" :loading="loading" @onSave="onClickSave" @onClose="onClickCancel"></ComOverlayPanelFooter>
    </div>
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
        title:String
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