<template>
    <div class="">
        <div :style="[{minWidth: width}, {maxWidth: width}]">
            <slot name="top"></slot>
            <h1 class="font-semibold text-lg" :class="ttl_header">{{ title }}</h1>
            <slot name="default"></slot>
            <ComOverlayPanelFooter :titleButtonCancel="titleButtonCancel" :icon="icon" :hideButtonOK="hideButtonOK" :titleButtonSave="titleButtonSave" :hideButtonClose="hideButtonClose" v-if="!hideFooter" :loading="loading" @onSave="onClickSave" @onClose="onClickCancel">
                <template #footer-left>
                    <slot name="footer-left"></slot>
                </template>
                <template #footer-right>
                    <slot name="footer-right"></slot>
                </template>
                <template #af-cancel-position>
                    <slot name="af-cancel-position"></slot>
                </template>
            </ComOverlayPanelFooter>
        </div>
    </div>
</template>
<script setup>
    const emit = defineEmits(['onSave', 'onCancel'])
    const props = defineProps({
        ttl_header: String,
        hideFooter: {
            type: Boolean,
            default: false
        },
        hideButtonOK: {
            type: Boolean,
            default: false
        },
        hideButtonClose: {
            type: Boolean,
            default: false
        },
        titleButtonSave: {
            type: String,
            default: 'Save'
        },
        loading: {
            type: Boolean,
            defualt: false
        },
        title:String,
        width:{
            type: String,
            defualt: '250px'
        },
        icon: {
            type: String,
            default: 'pi pi-save'
        },
        titleButtonCancel: {
            type: String,
            default: 'Close'
        }
    })
    const onClickSave = () => {
        emit('onSave')
    }
    const onClickCancel = () => {
        emit('onCancel')
    }
</script>
<style lang="">
    
</style>