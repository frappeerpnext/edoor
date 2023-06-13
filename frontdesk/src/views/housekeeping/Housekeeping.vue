<template>
    <div>
        <div class="px-2">
    <ComHeader isRefresh @onRefresh="Refresh()">
            <template #start>
                <div class="flex align-items-center">
                        <i @click="onShowSummary" class="pi pi-bars text-3xl cursor-pointer"></i>
                        <div @click="onRefresh()" class="text-2xl ml-4">Housekeeping</div>
                </div>
            </template>
    </ComHeader>
    <div class="flex my-2">
        <Button @click="hk.view_type ='table'">View as Table</Button>
        <Button @click="hk.view_type ='kanban'">View as Kanban</Button>
    </div>
    
    <div class="grid gap-2">
        <div class="col-12">
            <div class="flex justify-between">
                <div class="flex gap-3">
                    <ComHousekeepingFilter/>        
                </div>
                <div class="flex gap-3">
                    <ComHousekeepingActionButton/>
                </div>
            </div>
        </div>
        <div v-if="showSummary" class="col-2 bg-white rounded-xl">
            <ComHousekeepingStatistic/>        
        </div>
        <div class="col bg-white rounded-xl">
            <ComHousekeepingRoomList v-if="hk.view_type=='table'"/>
            <ComHousekeepingRoomKanbanView v-else/>
        </div>
        <!-- <div class="col-2">
            detail
        </div> -->
    </div>
    <table style="width:100%; border: solid 1px #ccc;">
    <!-- <tr>
        <td colspan="2" ><ComHousekeepingFilter/></td>
        <td><ComHousekeepingActionButton/></td>
    </tr> -->
    <!-- <tr>
        <td style="vertical-align: top;"><ComHousekeepingStatistic/></td>
        <td style="vertical-align: top;">
            <ComHousekeepingRoomList v-if="hk.view_type=='table'"/>
            <ComHousekeepingRoomKanbanView v-else/>

        </td>
    </tr> -->
    </table>
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
if (edoorShowhousekeepingSummary) {
    showSummary.value = edoorShowhousekeepingSummary == "1";
}
function onShowSummary() {
    showSummary.value = !showSummary.value
    localStorage.setItem("edoor_hhowhousekeeping_summary", showSummary.value ? "1" : "0")
}
onMounted(() => {
 
   hk.loadData()
}
)
</script>