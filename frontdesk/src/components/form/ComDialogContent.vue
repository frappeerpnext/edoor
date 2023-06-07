<template>
    <div :class="isDialog ? 'wrap-dialog' : 'bg-white p-2'">
        <div :class="isDialog ? 'wrap-dialog-content overflow-auto' : ''">
            <slot name="default"></slot>
        </div>
        <div v-if="!hideFooter" class="border-t border-gray-200 py-2 px-4">
            <div>
                <div class="flex justify-between items-center">
                    <div class="flex gap-2">
                        <slot name="footer-left"></slot>
                    </div>
                    <div class="flex gap-2">
                        <slot name="footer-center"></slot>
                    </div>
                    <div class="flex gap-2">
                        <slot name="footer-right"></slot>
                        <Button class="border-none" v-if="!hideButtonOK" @click="onOK()" :label="titleButtonOK" :loading="loading">
                            <span v-if="!loading"><img class="mr-2 inline" style="height: 14px;" :src="BtnOkIcon" v-if="!loading"/>Save</span>
                            <span v-else><i class="pi pi-spin pi-spinner mr-2"></i> Save</span>
                        </Button>
                        <Button class="border-none bg-og-edoor" v-if="!hideButtonClose" @click="close()" :label="titleButtonClose" :disabled="loading" >
                            <img class="btn-si__icon mr-2" :src="BtnCloseIcon"/> Close
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

const emit = defineEmits(['onOK', 'onClose'])
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
    }
})
function onOK() {
  
    emit('onOK')
}
function close() {
    emit('onClose')
}
</script>
<style scoped>
    .bg-og-edoor:hover , .bg-og-edoor:active{
        background-color: var(--bg-og-color);
    }
</style>