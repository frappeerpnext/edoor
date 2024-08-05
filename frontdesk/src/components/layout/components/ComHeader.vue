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
            <Button v-if="isSetting" :class="fillClass ? fillClass : 'content_btn_b'" style="font-size: 1.5rem"  icon="pi pi-ellipsis-v" @click="toggle"></Button>
            <Menu ref="show" :popup="true" style="min-width: 180px;">
                <template #start>
                    <button v-if="isSetting" @click="onSetting()" class="w-full p-link flex align-items-center p-2 pl-4 text-color hover:surface-200 border-noround">
                       <i class="pi pi-cog me-2" ></i>
                        {{ $t('Setting') }}
                    </button>
                </template>
            </Menu>

        </div>
    </div>
</template>
<script setup>
import { ref } from '@/plugin'
const isMobile = ref(window.isMobile) 
const show = ref()
const toggle = (event) => {
    show.value.toggle(event);
};
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
}
function onSetting(){
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