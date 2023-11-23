<template>
    <div :class="wrClass ? wrClass : 'py-3'" class="flex items-center justify-content-between">
        <div >
            <slot name="start"></slot>
        </div>
        <div>
            <slot name="center"></slot>
        </div>
        <div class="flex gap-2">
            <slot name="end"></slot>
            <div class="border-left-1 border-primary-100"></div>
            <Button v-if="isRefresh" @click="onRefresh()" icon="pi pi-refresh" :class="fillClass ? fillClass : 'content_btn_b'"></Button>
        </div>
    </div>
</template>
<script setup>
const props = defineProps({
    isRefresh: {
        type: Boolean,
        default: false
    },
    fillClass: String,
    wrClass: String
})
const emit = defineEmits(['onRefresh'])
function onRefresh(){
    emit('onRefresh')
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