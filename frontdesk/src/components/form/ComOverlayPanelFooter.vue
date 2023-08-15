<template lang="">
    <div class="pt-2">
        <div class="border-t border-gray-200 pt-2">
            <div class="flex justify-between items-center">
                <div class="flex gap-2">
                    <slot name="footer-left"></slot>
                </div>
                <div class="flex gap-2">
                    <slot name="footer-center"></slot>
                </div>
                <div class="flex gap-2">
                    <slot name="footer-right"></slot>
                    <Button class="border-none btn-close" v-if="!hideButtonClose" @click="onClose()" 
                        :disabled="loading" ><img class="btn-si__icon mr-2" :src="BtnCloseIcon"/> {{titleButtonCancel}} </Button>
                    <slot name="af-cancel-position"></slot>
                    <Button class="border-none" :icon="icon" v-if="!hideButtonOK" @click="onSave()" :label="titleButtonSave"
                        :loading="loading"></Button>
                </div>
            </div>
        </div>
    </div>
</template>
<script setup>
import BtnCloseIcon from '@/assets/svg/icon-close.svg' 
    const props = defineProps({
        loading: {
            type: Boolean,
            default: false
        },
        hideButtonOK:{
            type: Boolean,
            default: false
        },
        hideButtonClose:{
            type: Boolean,
            default: false
        },
        titleButtonSave:{
            type: String,
            default: 'Save'
        },
        titleButtonCancel:{
            type: Boolean,
            default: 'Cancel'
        },
        icon: {
            type: String,
            default: 'pi pi-save'
        }
    })
    const emit = defineEmits(['onCancel','onSave'])
    function onSave(){
        emit('onSave')
    }
    function onClose(){
        emit('onClose')
    }
</script>
<style lang="">
    
</style>