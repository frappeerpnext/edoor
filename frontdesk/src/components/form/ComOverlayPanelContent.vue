<template>
    <div class="">
        <div :style="[{minWidth: width ? width : ''}, {maxWidth: width ? width : ''}]">
            <slot name="top"></slot>
            <h1 class="font-semibold text-lg" :class="ttl_header">{{ $t(title ?? '') }}</h1>
            <slot name="default"></slot>
            <ComOverlayPanelFooter :titleButtonCancel="$t(titleButtonCancel ?? '')" :icon="icon" :hideButtonOK="hideButtonOK" :titleButtonSave="$t(titleButtonSave ?? '')" :hideButtonClose="hideButtonClose" v-if="!hideFooter" :loading="loading" @onSave="onClickSave" @onClose="onClickCancel">
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
    import {i18n} from '@/i18n';
const { t: $t } = i18n.global;
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
        },
        panelClass: String
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