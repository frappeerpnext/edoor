<template>
    <div :class="wrClass ? wrClass : 'py-3'" class="grid items-center justify-content-between">
        <div v-if="$slots.start" :class="colClass ? colClass : 'col-12'" class=" md:col-6 lg:col-3 " >
            <slot name="start"></slot>
        </div>
        <div v-if="$slots.center" :class="colClass ? colClass : 'col-12'" class=" md:col-6 lg:col flex justify-content-center">
            <slot name="center"></slot>
        </div>
        <div :class="colClass ? colClass : 'col-12'" class=" md:col-6 lg:col flex gap-2 justify-content-end">
            <slot name="end"></slot>
            <div v-if="isRefresh" class="border-left-1 border-primary-100"></div>
            <Button v-if="isRefresh && !isMobile" @click="onRefresh()" icon="pi pi-refresh" :class="fillClass ? fillClass : 'content_btn_b'"></Button>
            <Button v-if="isSetting && !isMobile" @click="onSetting()" icon="pi pi-cog" :class="fillClass ? fillClass : 'content_btn_b'"></Button>
        </div>
    </div>
</template>
<script setup>
import { ref } from '@/plugin'
const isMobile = ref(window.isMobile) 
const props = defineProps({
    isRefresh: {
        type: Boolean,
        default: false
    },
    isSetting: {
        type: Boolean,
        default: false
    },
    fillClass: String,
    wrClass: String,
    colClass:String,
})
const emit = defineEmits(['onRefresh','onSetting'])
function onRefresh(){
    emit('onRefresh')
    emit('onSetting')
}


</script>
<style scoped>
    .refresh-btn{
        background: #e3efff !important;
        color: #6366F1;
        border-radius: 50%;
        border: 1px solid #b9d6ff !important;
    }
    .refresh-btn:hover{
        color: #6366F1;
    }
</style>