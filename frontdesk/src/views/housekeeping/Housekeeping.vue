<template>
    <h1>Housekeeping</h1>
    <Button @click="hk.view_type ='table'">View as Table</Button>
    <Button @click="hk.view_type ='kanban'">View as Kanban</Button>
    <table style="width:100%; border: solid 1px #ccc;">
    <tr>
        <td colspan="2" ><ComHousekeepingFilter/></td>
        <td><ComHousekeepingActionButton/></td>
    </tr>
    <tr>
        <td style="vertical-align: top;"><ComHousekeepingStatistic/></td>
        <td style="vertical-align: top;">
            <ComHousekeepingRoomList v-if="hk.view_type=='table'"/>
            <ComHousekeepingRoomKanbanView v-else/>

        </td>
        <td style="vertical-align: top;"><ComHousekeepingRoomDetailPanel/></td>
    </tr>
    </table>
</template>

<script setup>
import { ref, inject, useToast, onMounted } from "@/plugin"
import ComHousekeepingFilter from "./components/ComHousekeepingFilter.vue";
import ComHousekeepingActionButton from "./components/ComHousekeepingActionButton.vue";
import ComHousekeepingStatistic from "./components/ComHousekeepingStatistic.vue";
import ComHousekeepingRoomList from "./components/ComHousekeepingRoomList.vue";
import ComHousekeepingRoomDetailPanel from "./components/ComHousekeepingRoomDetailPanel.vue";
import ComHousekeepingRoomKanbanView from "./components/ComHousekeepingRoomKanbanView.vue";
const hk = inject("$housekeeping")
const frappe = inject("$frappe")
const db = frappe.db()
const call = frappe.call()
const toast = useToast();
const filter = ref({})
onMounted(() => {
 
   hk.loadData()
}
)
</script>