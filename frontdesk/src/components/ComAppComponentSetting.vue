<template>

    <DynamicDialog v-if="isMobile"  :pt="{
        root: { class: 'p-dialog-maximized' }
    }"/>
    <DynamicDialog v-else/>

    <Toast position="top-center">
        <template #message="slotProps">
            <div class="flex flex-column" style="flex: 1">
                <strong class="mb-1" v-if="slotProps.message.summary" v-html="slotProps.message.summary"></strong>
                <p v-if="slotProps.message.detail" v-html="slotProps.message.detail"></p>
            </div>
        </template>
    </Toast>
    
    <Toast position="top-center">
        <template #message="slotProps">
            <div class="flex flex-column" style="flex: 1">
                <strong class="mb-1" v-if="slotProps.message.summary" v-html="slotProps.message.summary"></strong>
                <p v-if="slotProps.message.detail" v-html="slotProps.message.detail"></p>
            </div>
        </template>
    </Toast>
   <!-- toast top right -->
    <Toast position="top-right" group="tr">
        <template #message="slotProps">
            <div class="flex flex-column" style="flex: 1">
              
                <strong class="mb-1" v-if="slotProps.message.summary" v-html="slotProps.message.summary"></strong>
                <p class="p-toast-detail" v-if="slotProps.message.detail" v-html="slotProps.message.detail" ></p>

                <Button v-if="slotProps.message.action_title" @click="onActionClick(slotProps.message.action)" :label="slotProps.message.action_title" severity="secondary"/>              
               

                
            </div>
           
        </template>
    </Toast>

    <ConfirmDialog></ConfirmDialog>
     <ConfirmDialog group="headless">
        <template #container="{ message, acceptCallback, rejectCallback }">
            <div class="flex flex-column align-items-center p-5 surface-overlay border-round">
                
                <span class="font-bold text-2xl block mb-2 mt-4">{{ message.header }}</span>
                <p class="mb-0" v-html="message.message"></p>
                <div class="flex align-items-center gap-2 mt-4">
                    <Button :label="$t('Close')" @click="rejectCallback" severity="secondary"></Button>
                     
                </div>
            </div>
        </template>
    </ConfirmDialog>
</template>
<script setup>
import {ref} from "vue"
import {i18n} from '@/i18n';
const { t: $t } = i18n.global;

const isMobile = ref(window.isMobile)

function onActionClick(action){
    window.postMessage(action,"*")
}
</script>