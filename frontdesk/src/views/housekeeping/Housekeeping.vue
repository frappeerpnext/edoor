<template>
    <div>
        <div class="px-2">
            <ComHeader isRefresh @onRefresh="onRefresh()" v-if="!isLoading">
                <template #start>
                    <div class="flex align-items-center">
                        <i @click="onShowSummary" class="pi pi-bars text-3xl cursor-pointer"></i>
                        <div class="text-2xl ml-4">Housekeeping</div>
                    </div>
                </template>
            </ComHeader>
            <div class="flex justify-between mb-4">
                <div>
                    <div class="flex gap-2 ">
                        <div class="flex w-full gap-2">
                            <ComHousekeepingFilter />
                            <ComHousekeepingActionButton />
                        </div>
                    </div>
                </div>
                <div>
                    <div class="flex justify-center items-center overflow-hidden rounded-lg h-full">
                        <button type="button" @click="hk.view_type = 'table'"
                            :class="(hk.view_type == 'table') ? 'bg-blue-500 p-button h-full p-component text-white conten-btn border-right-none border border-noround-right' : 'p-button h-full p-component conten-btn border-noround-right'">
                                <i :class="(hk.view_type == 'table') ? 'text-white' : ''"
                                class="pi pi-list me-2" />Table
                        </button>
                        <button @click="hk.view_type = 'kanban'"
                            :class="(hk.view_type == 'kanban') ? 'bg-blue-500 p-button h-full p-component text-white conten-btn border-left-none border border-noround-left' : 'p-button h-full p-component conten-btn border-noround-left'">
                                <i :class="(hk.view_type == 'kanban') ? 'text-white' : ''"
                                class="pi pi-th-large me-2" />Kanban
                        </button>
                    </div>
                </div>
            </div>
            <div>
                <div class="grid gap-2">
                    <div v-if="showSummary" class="col-2 p-0 rounded-xl">
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
import { ref, inject, useToast, onMounted } from "@/plugin"
import ComHousekeepingFilter from "./components/ComHousekeepingFilter.vue";
import ComHousekeepingActionButton from "./components/ComHousekeepingActionButton.vue";
import ComHousekeepingStatistic from "./components/ComHousekeepingStatistic.vue";
const edoorShowhousekeepingSummary = localStorage.getItem("edoor_hhowhousekeeping_summary")
import ComHousekeepingRoomList from "./components/ComHousekeepingRoomList.vue";
import ComHousekeepingRoomKanbanView from "./components/ComHousekeepingRoomKanbanView.vue";
const hk = inject("$housekeeping")
const frappe = inject("$frappe")

const showSummary = ref(true)
const db = frappe.db()
const call = frappe.call()
const toast = useToast();
const filter = ref({})
const isLoading = ref(false)

if (edoorShowhousekeepingSummary) {
    showSummary.value = edoorShowhousekeepingSummary == "1";
}
function onShowSummary() {
    showSummary.value = !showSummary.value
    localStorage.setItem("edoor_hhowhousekeeping_summary", showSummary.value ? "1" : "0")
}
function onRefresh() {
    isLoading.value = true
    hk.loadData().then((data) => {
        isLoading.value = false
    }).catch((err) => {
        isLoading.value = false

    })


}
onMounted(() => {

    hk.loadData()
}
)
</script>