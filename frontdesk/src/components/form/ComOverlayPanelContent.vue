<template>
    <div class="">
        <div :style="[{minWidth: width}, {maxWidth: width}]">
            <span class="font-semibold text-lg mb-3">{{ title }}</span>
            <slot name="default"></slot>
            <ComOverlayPanelFooter :titleButtonCancel="titleButtonCancel" :icon="icon" :hideButtonOK="hideButtonOK" :titleButtonSave="titleButtonSave" :hideButtonClose="hideButtonClose" v-if="!hideFooter" :loading="loading" @onSave="onClickSave" @onClose="onClickCancel">
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