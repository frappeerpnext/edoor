<template lang="">
    <div class="flex">
        <Button class="border-none mr-1" @click="onView()">{{viewType == 'room_type' ? 'Room Type' : 'Room'}}</Button>
        <div class="mr-2 relative">
            <Button type="button" class="h-full border-none" icon="pi pi-eye" @click="toggle" aria-haspopup="true" aria-controls="peroid_menu" />
            <Menu ref="menu" id="peroid_menu" :model="items" :popup="true" />
        </div>
        <Button @click="onPrevNext('prev')" icon="pi pi-angle-double-left" class="border-noround-right border-none"></Button>
        <Button @click="onToday('today')" class="border-noround border-none">Today</Button>
        <Button @click="onPrevNext('next')" class="border-noround-left border-none" icon="pi pi-angle-double-right"></Button>
    </div>
</template>
<script setup>
import { ref } from 'vue'
const emit = defineEmits(['onFilter', 'onPrevNext', 'onToday'])
const props = defineProps({
    viewType: {
        type: String,
        default: 'room_type'
    }
})
const menu = ref();
const items = ref([
    {
        label: 'Week',
        command: () => {
            emit('onFilter', 'week')
        }
    },
    {
        label: '14 Days',
        command: () => {
            emit('onFilter', '14_days')
        }
    },
    {
        label: 'Month',
        command: () => {
            emit('onFilter', 'month')
        }
    }
]);
function onToday() {
    emit('onToday')
}
function onFilter(key) {
    emit('onFilter', key)
}
function onPrevNext(key) {
    emit('onPrevNext', key)
}
const toggle = (event) => {
    menu.value.toggle(event);
};
function onView() {
    emit('onView')
}
</script>
<style lang="">
    
</style>