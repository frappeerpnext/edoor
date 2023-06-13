<template>
<div>
    <div :style="{minWidth: width}">
        <span class="font-semibold text-lg mb-3">{{ title }}</span>
        <slot name="default"></slot>
        <ComOverlayPanelFooter v-if="!hideFooter" :loading="loading" @onSave="onClickSave" @onClose="onClickCancel">
            <template #footer-right>
                <slot name="footer-right"></slot>
            </template>
        </ComOverlayPanelFooter>
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
        title:String,
        width:{
            type: String,
            defualt: '250px'
        }
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