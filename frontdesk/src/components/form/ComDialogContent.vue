<template>
    <div  :class="[isDialog ? 'wrap-dialog' : 'bg-white p-2 relative di-page', dialogClass]">
        <div :class="isDialog ? 'wrap-dialog-content overflow-auto' : ''">
            <slot name="default"></slot>
            <div v-if="loading">
                <div  class="overlay-loading-dialog">
                <div class="is-loading-page text-white flex justify-center flex-col">
                    <div><i class="pi pi-spin pi-spinner" style="font-size:35px"></i></div>
                    <div class="text-sm">Loading....</div>
                </div>
                </div>    
            </div>
        </div>
        <div v-if="!hideFooter" :class="[isDialog == false ? 'border-t p-2 page-footer-fixed':'border-t border-gray-200 p-2 pb-0 footer-fixed dialog-ftt', loading ? 'unset-absolute' : '']">
            <div class="overflow-auto lg:overflow-hidden">
                <slot name="footer-top"></slot>
                <div class="flex gap-1 lg:gap-0 justify-between items-center w-max lg:w-full">
                    <div class="flex gap-2">
                        <slot name="footer-left"></slot>
                    </div>
                    <div class="flex gap-2">
                        <slot name="footer-center"></slot>
                    </div>
                    <div class="flex gap-2">
                        <slot name="footer-right"></slot>
                        
                        <Button class="border-none bg-og-edoor" v-if="!hideButtonClose" @click="close()" :label="titleButtonClose" :disabled="loading" >
                            <img class="btn-si__icon mr-2" :src="BtnCloseIcon"/> {{ $t(titleButtonClose ?? '')}}
                        </Button>
                        <Button class="border-none btn-ok_ss" v-if="!hideButtonOK" @click="onOK()" :label="titleButtonOK" :loading="loading">
                            <span v-if="!loading" class="flex align-items-center">
                                <i class="pi pi-check-circle mr-2" v-if="!loading && !hideIcon && titleButtonOK == 'Ok'"></i>
                                <img class="pi pi-check-circle mr-2" v-else-if="!loading && !hideIcon && titleButtonOK == 'Save'" :src="BtnOkIcon" style="height: 13px;"/>
                                {{ $t(titleButtonOK ?? '') }}
                            </span>
                            <span v-else><i class="pi pi-spin pi-spinner mr-2"></i> {{ $t(titleButtonOK ?? '') }}</span>
                        </Button>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>
<script setup>
import BtnCloseIcon from '@/assets/svg/icon-close.svg' 
import BtnOkIcon from '@/assets/svg/icon-save.svg' 
import {i18n} from '@/i18n';
const { t: $t } = i18n.global;

const emit = defineEmits(['onOK', 'onClose', 'onMaximize'])
const props = defineProps({
    loading: {
        type: Boolean,
        default: false
    },
    dialogClass: {
        type: String,
    },
    titleButtonOK: {
        type: String,
        default: 'Save'
    },
    titleButtonClose: {
        type: String,
        default: 'Close'
    },
    hideButtonClose: {
        type: Boolean,
        default: false
    },
    hideButtonOK: {
        type: Boolean,
        default: false
    },
    hideFooter: {
        type: Boolean,
        default: false
    },
    isDialog: {
        type: Boolean,
        default: true
    },
    hideIcon: {
        type: Boolean,
        default:false
    },
    maximizable: {
        type: Boolean,
        default:false
    },
    
})
function onOK() { 
    emit('onOK')
}
function close() {
    emit('onClose')
}
function onMaximize(){
    emit('onMaximize')
}
</script>
<style scoped>
    .bg-og-edoor:hover , .bg-og-edoor:active{
        background-color: var(--bg-og-color);
    }
    .is-loading-page{
    position: absolute;
    left: 50%;
    top: 50%;
    z-index: 11;
    transform: translate(-50%,-50%);
}
.overlay-loading-dialog {
    position: absolute;
    top: 0;
    left: 0;
    z-index: 10;
    background-color: rgba(0, 0, 0, 0.4);
    width: 100%;
    height: 100%;
}
</style>