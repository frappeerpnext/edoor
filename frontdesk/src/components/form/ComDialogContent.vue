<template>
    <div :class="isDialog ? 'wrap-dialog' : 'bg-white p-2'">
        <div :class="isDialog ? 'wrap-dialog-content overflow-auto' : ''">
            <slot name="default"></slot>
            <div v-if="loading">
                <div  class="overlay-loading-dialog">
                <span class="is-loading-page text-white flex justify-center flex-col">
                    <i  class="pi pi-spin pi-spinner w-4rem h-4rem" style="font-size:4rem"></i>
                    <span class="text-sm mt-1">Loading....</span>
                </span>
                </div>    
            </div>
        </div>
        <div v-if="!hideFooter" :class="[is_page ? 'border-t border-gray-200 p-2 footer-fixed':'border-t border-gray-200 p-2 pb-0 footer-fixed dialog-ftt', loading ? 'unset-absolute' : '']">
            <!-- <div class="relative">
                <div v-if="loading" class="overlay-loading-dialog"></div>
            </div> -->
            <div>
                <slot name="footer-top"></slot>
                <div class="flex justify-between items-center">
                    <div class="flex gap-2">
                        <slot name="footer-left"></slot>
                    </div>
                    <div class="flex gap-2">
                        <slot name="footer-center"></slot>
                    </div>
                    <div class="flex gap-2">
                        <slot name="footer-right"></slot>
                        
                        <Button class="border-none bg-og-edoor" v-if="!hideButtonClose" @click="close()" :label="titleButtonClose" :disabled="loading" >
                            <img class="btn-si__icon mr-2" :src="BtnCloseIcon"/> {{titleButtonClose}}
                        </Button>
                        <Button class="border-none btn-ok_ss" v-if="!hideButtonOK" @click="onOK()" :label="titleButtonOK" :loading="loading">
                            <span v-if="!loading" class="flex align-items-center">
                                <i class="pi pi-check-circle mr-2" v-if="!loading && !hideIcon && titleButtonOK == 'Ok'"></i>
                                <img class="pi pi-check-circle mr-2" v-else-if="!loading && !hideIcon && titleButtonOK == 'Save'" :src="BtnOkIcon" style="height: 13px;"/>
                                {{titleButtonOK}}
                            </span>
                            <span v-else><i class="pi pi-spin pi-spinner mr-2"></i> {{titleButtonOK}}</span>
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

const emit = defineEmits(['onOK', 'onClose', 'onMaximize'])
const props = defineProps({
    loading: {
        type: Boolean,
        default: false
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
    }
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