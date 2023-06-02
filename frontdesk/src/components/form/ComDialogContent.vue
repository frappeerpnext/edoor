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
                        <Button class="border-none" v-if="!hideButtonOK" @click="onOK()" :label="titleButtonOK"
                            :loading="loading"></Button>
                        <Button class="border-none bg-og-edoor" v-if="!hideButtonClose" @click="onClose()" :label="titleButtonClose"
                            :disabled="loading"  />
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>
<script setup>
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
function onClose() {
    emit('onClose')
}
</script>
<style scoped>
    .bg-og-edoor:hover , .bg-og-edoor:active{
        background-color: var(--bg-og-color);
    }
</style>