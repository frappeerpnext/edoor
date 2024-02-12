<template lang="">
    <div class="flex">
        <template v-if="route.name != 'RoomInventory'">
            <Button class="border-y-none border-left-none border-noround-right"  v-tippy = " v-tippy == 'room_type' ? 'Room List View' : 'Room Type View'" @click="onView()">
                <img v-if="viewType == 'room_type'" class="icon-set-svg" :src="iconChangeRoom"/>
                <img v-else style="height:19px" :src="iconChangeRoomOrderlist"/>
            </Button>
            <div class="mr-2 relative h-full">
                <Button type="button" class="h-full border-none border-noround-left btn-set__h" icon="pi pi-angle-down"  @click="toggle" aria-haspopup="true" aria-controls="peroid_menu" />
                <Menu ref="menu" id="peroid_menu" :popup="true" :model="items">
                    <template #item="data">
                        <button
                            :class="active == data.item.key ? 'bg-gray-300' : 'bg-white'"
                            class="w-full p-link flex align-items-center py-2 px-3 text-color hover:surface-200 border-noround">
                            <div class="flex items-center gap-2"> <ComIcon :icon="data.item.icon" style="height: 16px;" /> {{data.item.label}} </div>
                        </button>
                    </template>
                </Menu>
            </div>
        </template>
        <template v-else>
            <Button class="border-y-none border-left-none border-noround-right white-space-nowrap">
               {{selectedPeriod}}
            </Button>
            <div class="mr-2 relative h-full">
                <Button type="button" class="h-full border-none border-noround-left btn-set__h" icon="pi pi-angle-down"  @click="toggle" aria-haspopup="true" aria-controls="peroid_menu" />
                <Menu ref="menu" id="peroid_menu" :popup="true" :model="items">
                    <template #item="data">
                        <button
                            :class="active == data.item.key ? 'bg-gray-300' : 'bg-white'"
                            class="w-full p-link flex align-items-center py-2 px-3 text-color hover:surface-200 border-noround">
                            <div class="flex items-center gap-2"> <ComIcon :icon="data.item.icon" style="height: 16px;" /> {{data.item.label}} </div>
                        </button>
                    </template>
                </Menu>
            </div>
        </template>
        
        <Button  @click="onPrevNext('prev')" icon="pi pi-angle-double-left" v-tippy="'View Previous Day'" class="border-noround-right border-y-none border-left-none"></Button>
        <Button @click="onToday('today')"  v-tippy ="'View Today'"  class="border-noround border-none"><img class="icon-set-svg" :src="iconTodayCalendar"/></Button>
        <Button @click="onPrevNext('next')"  v-tippy ="'View Next Day'" class="border-noround-left border-y-none border-right-none" icon="pi pi-angle-double-right"></Button>

        <div class="border-left-1 border-primary-100 m-2"></div>
        <Button v-if="!hideRefresh" @click="onRefresh()" icon="pi pi-refresh" class="content_btn_b adjBtnRefresh"></Button>

    </div>
</template> 
<script setup>
import { ref, useRoute,computed } from '@/plugin'
import iconChangeRoom from '@/assets/svg/change-room-icon.svg'
import iconTodayCalendar from '@/assets/svg/calendar-today-icon.svg'
import iconChangeRoomOrderlist from '@/assets/svg/icon-bed.svg'

const route = useRoute()

const reservation_chart = ref(JSON.parse(sessionStorage.getItem('reservation_chart')))
const active = ref(reservation_chart.value?.period || "15_days")
const emit = defineEmits(['onFilter', 'onPrevNext', 'onToday','onChangePeriod','onRefresh'])
const menu = ref();

const props = defineProps({
    viewType: {
        type: String,
        default: '<room_type>'
    },
    hideRefresh: Boolean
})

const selectedPeriod = computed(()=>{
    if(reservation_chart.value?.period=="week"){
        return "Week"
    }else if(reservation_chart.value?.period=="month"){
        return "Month"
    }else {
        return "15 Days"
    }
})

const items = ref([
    {
        label: 'Week',
        key: 'week',
        icon:'iconWeekCalendar',
        command: () => {
            onChangePeriod('week')
        }
    },
    {
        label: '15 Days',
        key: '15_days',
        icon:'icon14Day',
        command: () => {
            onChangePeriod('15_days')
        }
    },
    {
        label: 'Month',
        key: 'month',
        icon:'iconMonth',
        command: () => {
            onChangePeriod('month')
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

function onChangePeriod(key) {
    active.value = key
    emit('onChangePeriod', key)
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

function onRefresh(){
    emit('onRefresh')
}
</script>

<style scoped>
    .adjBtnRefresh{
        padding-top: 0.4rem !important;
        padding-bottom: 0.5rem !important;
    }
</style>