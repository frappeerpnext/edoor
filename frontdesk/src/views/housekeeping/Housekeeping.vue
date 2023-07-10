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
            <!-- <div class="flex my-2">
        <Button @click="hk.view_type ='table'"><i class="pi pi-list me-2" />Table</Button>
        <Button @click="hk.view_type ='kanban'"><i class="pi pi-th-large me-2"/>Kanban</Button>
    </div> -->
            <div class="grid">
                <div class="col-12">
                    <div class="flex justify-between">
                        <div class="flex gap-3">
                            <ComHousekeepingFilter />
                        </div>
                        <!-- <div class="flex gap-3">
                    <ComHousekeepingActionButton/>
                </div> -->
                    </div>
                </div>
                <div class="col-12 m-0 p-0">
                    <div class="flex justify-end">
                        <div class="col-10">
                            <div class="w-full flex justify-between my-2">
                                <div class="flex gap-2">
                                    <ComHousekeepingActionButton />
                                </div>
                                <div
                                    class=" flex  justify-center items-center bg-gray-100 shadow-lg overflow-hidden rounded-lg">
                                    <button type="button" @click="hk.view_type = 'table'"
                                        :class="(hk.view_type == 'table') ? 'bg-blue-500  text-white ' : 'bg-white'"
                                        class="border-blue-100 border-2 border-round-left-lg py-2 px-3 "><i
                                            :class="(hk.view_type == 'table') ? 'text-white' : ''"
                                            class="pi pi-list me-2" />Table</button>
                                    <button @click="hk.view_type = 'kanban'"
                                        :class="(hk.view_type == 'kanban') ? 'bg-blue-500   text-white ' : 'bg-white'"
                                        class="border-blue-100 border-2 border-round-right-lg py-2 px-3"><i
                                            :class="(hk.view_type == 'kanban') ? 'text-white' : ''"
                                            class="pi pi-th-large me-2" />Kanban</button>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="col-12">
                    <div class="grid gap-3">
                        <div v-if="showSummary" class="col-2 p-0 rounded-xl">
                            <ComHousekeepingStatistic />
                        </div>
                        <div class="col bg-white rounded-xl">

                            <ComHousekeepingRoomList v-if="hk.view_type == 'table'" />
                            <ComHousekeepingRoomKanbanView v-else />
                        </div>
                    </div>
                </div>
                <!-- <div class="col-2">
            detail
        </div> -->
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
function onRefresh(){
    isLoading.value = true
    hk.loadData().then((data)=>{
        isLoading.value = false
    }).catch((err)=>{
        isLoading.value = false

    })

   
}
onMounted(() => {

    hk.loadData()
}
)
</script>