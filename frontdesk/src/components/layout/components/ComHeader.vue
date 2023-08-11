<template>
    <div class="flex items-center justify-content-between py-3">
        <div >
            <slot name="start"></slot>
        </div>
        <div>
            <slot name="center"></slot>
        </div>
        <div class="flex gap-2">
            <slot name="end"></slot>
            <div class="flex gap-2 ms-2 border-left-1 border-primary-100">
                <slot name="hlp_menu"></slot>
                <Button v-if="isRefresh" @click="onRefresh()" icon="pi pi-refresh" class="d-bg-set btn-inner-set-icon border-none refresh-btn"></Button>
            </div>
        </div>
    </div>
</template>
<script setup>
import { ref } from 'vue';
const show = ref()
const toggle = (event) => {
    show.value.toggle(event);
};

const props = defineProps({
    isRefresh: {
        type: Boolean,
        default: false
    }
})
 const emit = defineEmits(['onRefresh'])
 function onRefresh(){
    emit('onRefresh')
 }
 

 function onResetTable(){
    localStorage.removeItem("page_state_reservation")
    localStorage.removeItem("table_reservation_list_state")
   
   window.location.reload()
}
</script>
<style scoped>
    .refresh-btn{
        background: #e3efff !important;
        color: #6366F1;
        border-radius: 50%;
        border: 1px solid #b9d6ff !important;
    }
</style>