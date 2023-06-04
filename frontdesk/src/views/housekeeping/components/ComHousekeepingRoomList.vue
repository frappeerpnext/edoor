<template> 
<div> 
    <DataTable 
        v-model:selection="hk.selectedRooms" 
        dataKey="name" 
        :value="hk.room_list" 
        @row-dblclick="onDblClick" 
        @row-click="onRowSelect"  
        tableStyle="min-width: 50rem"
        paginator :rows="20" :rowsPerPageOptions="[20, 50,100]" 
    >
        <Column selectionMode="multiple" headerStyle="width: 3rem"></Column>
        <Column field="room_number" header="Room #"></Column>
        <Column field="room_type" header="Room Type"></Column>
        <Column field="room_type" header="Room Type"></Column>

        <Column field="housekeeper" header="Housekeeper">
            <template #body="slotProps">
                <Button @click="onAssignHousekeeper($event,slotProps.data)" :label="slotProps.data.housekeeper" link size="small" icon="pi pi-pencil" iconPos="right"></Button>
            </template>
        </Column>
        <Column field="housekeeping_status" header="Status" class="text-left">
            <template #body="slotProps">
                <!-- <Tag :value="slotProps.data.housekeeping_status" :style="{ background: slotProps.data.status_color }"></Tag>  -->
                <ComHousekeepingChangeStatusButton @onSelected="onSelected" :data="slotProps.data"/>
            </template>
        </Column>
    </DataTable>
    <OverlayPanel ref="opHousekeeper">
        <ComOverlayPanelContent :loading="loading"  @onCancel="onAssignHousekeeper($event,{})" @onSave="onSaveAssignHousekeeper">
            <ComSelect class="w-full" isFilter v-model="selected.housekeeper" placeholder="Assign Housekeeper" doctype="Housekeeper"  />
        </ComOverlayPanelContent>
    </OverlayPanel>
</div>
</template>
<script setup>
import { ref,inject,toaster } from '@/plugin';
import ComHousekeepingChangeStatusButton from './ComHousekeepingChangeStatusButton.vue' 
const loading = ref(false)
const selected = ref({
    room: '',
    housekeeper: ''
})
const opHousekeeper = ref()
const hk = inject("$housekeeping")
const frappe = inject("$frappe")
const call = frappe.call()
function onSelected(room,status){
    hk.updateRoomStatus(room,status)
}
function onAssignHousekeeper($event, r){
    selected.value.housekeeper = r.housekeeper || ''
    selected.value.room = r.name || ''
    opHousekeeper.value.toggle($event)
}
function onSaveAssignHousekeeper() {
    loading.value = true; 
    call.post("edoor.api.housekeeping.update_housekeeper", {
        rooms: selected.value.room,
        housekeeper: selected.value.housekeeper
    }).then((result) => {
        toaster('success','Change housekeeping successfully')
        hk.loadData()
        opHousekeeper.value.hide()
        loading.value = false
    }).catch((err) => {
        loading.value = false
    })
}
function onRowSelect(r){
    hk.selectedRow = r.data
}

function onDblClick(r){
    alert("you double click on row: " + r.data.room_number) 
}

</script>