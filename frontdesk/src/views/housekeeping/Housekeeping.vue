<template> 
    <div>
        <div class="px-2">
            <ComHeader isRefresh @onRefresh="onRefresh()">
                <template #start>
                    <div class="flex align-items-center">
                        <i @click="onShowSummary" class="pi pi-bars text-3xl cursor-pointer"></i>
                        <div class="text-2xl ml-4">Housekeeping</div>
                    </div>
                </template>
                <template #end>
                    <ComHousekeepingActionButton />
                </template>
            </ComHeader>
            <div class="flex justify-between mb-4 overflow-auto ">
                <div>
                    <div class="flex gap-2 me-2">
                        <div class="flex w-full gap-2">
                            <ComHousekeepingFilter />
                        </div>
                    </div>
                </div>
                <div class="flex gap-2">
                    <div class="flex justify-center items-center overflow-hidden rounded-lg h-full">
                        <button type="button" @click="hk.view_type = 'table'"
                            :class="(hk.view_type == 'table') ? 'bg-blue-500 p-button h-full p-component text-white conten-btn border-right-none border border-noround-right' : 'p-button h-full p-component conten-btn border-noround-right'">
                            <i :class="(hk.view_type == 'table') ? 'text-white' : ''" class="pi pi-list me-2" />Table
                        </button>
                        <button @click="hk.view_type = 'kanban'"
                            :class="(hk.view_type == 'kanban') ? 'bg-blue-500 p-button h-full p-component text-white conten-btn border-left-none border border-noround-left' : 'p-button h-full p-component conten-btn border-noround-left'">
                            <i :class="(hk.view_type == 'kanban') ? 'text-white' : ''" class="pi pi-th-large me-2" />Kanban
                        </button>
                    </div>
                    <div>
                        <Button @click="onPrevNext('prev')" icon="pi pi-angle-double-left" v-tippy="'Back day'"
                            class="border-noround-right border-y-none border-left-none h-full"></Button>
                        <Button @click="onToday()" v-tippy="'Today'" class="border-noround border-none h-full"><img
                                class="icon-set-svg" :src="iconTodayCalendar" /></Button>
                        <Button @click="onPrevNext('next')" v-tippy="'Next day'"
                            class="border-noround-left border-y-none border-right-none h-full"
                            icon="pi pi-angle-double-right"></Button>
                    </div>
                </div>
            </div>
            <div>
                <div class="grid gap-2">
                    <div v-if="showSummary" class="col-2 p-0 rounded-xl" style="width:280px">
                        <ComHousekeepingStatistic />
                    </div>
                    <div class="col rounded-xl p-0">
                        <ComHousekeepingRoomList v-if="hk.view_type == 'table'" />
                        <ComHousekeepingRoomKanbanView v-else />
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>
<script setup>
import { ref, inject, onMounted, onUnmounted, reactive } from "@/plugin"
import ComHousekeepingFilter from "./components/ComHousekeepingFilter.vue";
import ComHousekeepingActionButton from "./components/ComHousekeepingActionButton.vue";
import ComHousekeepingStatistic from "./components/ComHousekeepingStatistic.vue";
const edoorShowhousekeepingSummary = localStorage.getItem("edoor_hhowhousekeeping_summary")
import ComHousekeepingRoomList from "./components/ComHousekeepingRoomList.vue";
import ComHousekeepingRoomKanbanView from "./components/ComHousekeepingRoomKanbanView.vue";
import iconTodayCalendar from '@/assets/svg/calendar-today-icon.svg'
import { hydrate } from "vue";
const hk = inject("$housekeeping")
const moment = inject("$moment")
const showSummary = ref(true)
const working_date = JSON.parse(localStorage.getItem("edoor_working_day"))

if (edoorShowhousekeepingSummary) {
    showSummary.value = edoorShowhousekeepingSummary == "1";
}
function onShowSummary() {
    showSummary.value = !showSummary.value
    localStorage.setItem("edoor_hhowhousekeeping_summary", showSummary.value ? "1" : "0")
}

const onRefresh = debouncer(() => {
    hk.pageState.page = 0
    hk.loadData()
}, 500);
function debouncer(fn, delay) {
    var timeoutID = null;
    return function () {
        clearTimeout(timeoutID);
        var args = arguments;
        var that = this;
        timeoutID = setTimeout(function () {
            fn.apply(that, args);
        }, delay);
    };
}
onMounted(() => {
    window.socket.on("Housekeeping", (arg) => {
        if (arg.property == window.property_name) {
            setTimeout(function () {
                hk.loadData(false)
            }, 3000)
        }
    })

    hk.loadData()
})

const dateOptions = reactive({
    dateIncrement: { days: 1 }
})

const onPrevNext = (key) => {
    if (key == 'prev') {
        hk.filter.selected_date = moment(hk.filter.selected_date).add(dateOptions.dateIncrement.days * -1, 'days').toDate()
    }
    else {
        hk.filter.selected_date = moment(hk.filter.selected_date).add(dateOptions.dateIncrement.days, 'days').toDate()
    }
    hk.loadData()
}

const onToday = () => {
    hk.filter.selected_date = moment(working_date.date_working_day).toDate()
    hk.loadData()
}

onUnmounted(() => {
    window.socket.off("Housekeeping")
})

</script>