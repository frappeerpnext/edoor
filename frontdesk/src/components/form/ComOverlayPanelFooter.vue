<template lang="">
    <div class="pt-2">
        <div class="border-t border-gray-200 pt-2">
            <div class="flex justify-between items-center">
                <div class="flex gap-2">
                    <Button class="border-none" v-if="!hideButtonOK" @click="onSave()" :label="titleButtonSave"
                        :loading="loading"></Button>
                    <slot name="footer-left"></slot>
                </div>
                <div class="flex gap-2">
                    <slot name="footer-center"></slot>
                </div>
                <div class="flex gap-2">
                    <slot name="footer-right"></slot>
                    
                    <Button class="border-none btn-close" v-if="!hideButtonClose" @click="onClose()" :label="titleButtonCancel"
                        :disabled="loading"  />
                </div>
            </div>
        </div>
    </div>
</template>
<script setup>
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