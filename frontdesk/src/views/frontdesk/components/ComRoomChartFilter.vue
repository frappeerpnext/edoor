<template lang="">
    <div class="flex">
        <Button class="border-y-none border-left-none border-noround-right" @click="onView()">
            <img v-if="viewType == 'room_type'" class="icon-set-svg" :src="iconChangeRoom"/>
            <img v-else style="height:19px" :src="iconChangeRoomOrderlist"/>
        </Button>
        <div class="mr-2 relative h-full">
            <Button type="button" class="h-full border-none border-noround-left btn-set__h" icon="pi pi-angle-down" @click="toggle" aria-haspopup="true" aria-controls="peroid_menu" />
            <Menu ref="menu" id="peroid_menu" :popup="true" :model="items">
                <template #item="data">
                    <button
                        :class="active == data.item.key ? 'bg-gray-300' : 'bg-white'"
                        class="w-full p-link flex align-items-center py-2 px-3 text-color hover:surface-200 border-noround">
                        <span class="ml-2">{{data.item.label}} </span>
                    </button>
                </template>
            </Menu>
        </div>
        <Button @click="onPrevNext('prev')" icon="pi pi-angle-double-left" class="border-noround-right border-y-none border-left-none"></Button>
        <Button @click="onToday('today')" class="border-noround border-none"><img class="icon-set-svg" :src="iconTodayCalendar"/></Button>
        <Button @click="onPrevNext('next')" class="border-noround-left border-y-none border-right-none" icon="pi pi-angle-double-right"></Button>
    </div>
</template> 
<script setup>
import { ref } from 'vue'
import iconTodayCalendar from '@/assets/svg/calendar-today-icon.svg'
import iconChangeRoomOrderlist from '@/assets/svg/icon-bed.svg'
import iconChangeRoom from '@/assets/svg/change-room-icon.svg'

const iconChangeRoomStatus = ref({
    img: iconChangeRoom
})
const reservation_chart = ref(JSON.parse(sessionStorage.getItem('reservation_chart')))
const active = ref(reservation_chart.value.peroid)

const emit = defineEmits(['onFilter', 'onPrevNext', 'onToday',])
const props = defineProps({
    viewType: {
        type: String,
        default: '<room_type>'
    }
})
const menu = ref();
const items = ref([
    {
        label: 'Week',
        key: 'week',
        command: () => {
            onSearch('week')
        }
    },
    {
        label: '14 Days',
        key: '14_days',
        command: () => {
            onSearch('14_days')
        }
    },
    {
        label: 'Month',
        key: 'month',
        command: () => {
            onSearch('month')
        }
    }
]);
function onToday() {
    emit('onToday')
}
function onSearch(key) {
    active.value = key
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