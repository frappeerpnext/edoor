<template>
    <div>
        <DataTable v-model:selection="hk.selectedRooms" dataKey="name" :value="hk.room_list" @row-dblclick="onDblClick"
            @row-click="onRowSelect" tableStyle="min-width: 50rem" paginator :rows="20" :rowsPerPageOptions="[20, 50, 100]">
            <Column selectionMode="multiple" headerStyle="width: 3rem"></Column>
            <Column field="room_number" header="Room #"></Column>
            <Column header="Status">
                <template #body="{ data }">
                    <span class="py-1 px-3 rounded-xl text-white white-space-nowrap " :style="{ background: data.status_color }">
                        {{ data.housekeeping_status }}
                    </span> 
                </template>
            </Column>
            <Column field="room_type" header="Room Type"></Column>

            <Column field="guest_name" header="Guest Name">
                <template #body="slotProps">
                    <Button class="color-purple-edoor" v-if="slotProps.data.guest" @click="onViewCustomerDetail(slotProps.data.guest)" link>
                        {{ slotProps.data.guest }} - {{ slotProps.data.guest_name }}
                    </Button>
                </template>
            </Column>
            <Column field="room_type" header="Reservation Status"></Column>
            <Column field="housekeeper" header="Housekeeper">
                <template #body="slotProps">
                    <Button @click="onAssignHousekeeper($event, slotProps.data)" :label="slotProps.data.housekeeper" link
                        size="small" icon="pi pi-pencil" iconPos="right"></Button>
                </template>
            </Column>
        </DataTable>
        <OverlayPanel ref="opHousekeeper">
            <ComOverlayPanelContent :loading="loading" @onCancel="onAssignHousekeeper($event, {})"
                @onSave="onSaveAssignHousekeeper">
                <ComSelect class="w-full" isFilter v-model="selected.housekeeper" placeholder="Assign Housekeeper"
                    doctype="Housekeeper" />
            </ComOverlayPanelContent>
        </OverlayPanel>




        <Column field="housekeeping_status" header="Status" class="text-left">

            <template #body="slotProps">
                <!-- <Tag :value="slotProps.data.housekeeping_status" :style="{ background: slotProps.data.status_color }"></Tag>  -->
                <ComHousekeepingChangeStatusButton @onSelected="onSelected" :data="slotProps.data" />
            </template>
        </Column>
        <div class="hkpanel">
        <Sidebar :dismissable="false" v-model:visible="visibleRight" position="right"  :maskStyle="{ pointerEvents: 'none' }">
            <ComHousekeepingRoomDetailPanel></ComHousekeepingRoomDetailPanel>
        </Sidebar>
        </div>
    </div>
</template>

<script setup>

import { ref, inject } from '@/plugin';
import ComHousekeepingChangeStatusButton from './ComHousekeepingChangeStatusButton.vue'
import ComHousekeepingRoomDetailPanel from './ComHousekeepingRoomDetailPanel.vue';
import { useDialog } from 'primevue/usedialog';
import GuestDetail from "@/views/guest/GuestDetail.vue"
const dialog = useDialog();
const loading = ref(false)
const selected = ref({
    room: '',
    housekeeper: ''
})
const opHousekeeper = ref()
const hk = inject("$housekeeping")
const gv = inject("$gv")
const frappe = inject("$frappe")
const call = frappe.call()
const visibleRight = ref(false);
const db = frappe.db()

function onSelected(room, status) {
    hk.updateRoomStatus(room, status)
}
function onAssignHousekeeper($event, r) {
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
        gv.toast('success', 'Change housekeeping successfully')
        hk.loadData()
        opHousekeeper.value.hide()
        loading.value = false
    }).catch((err) => {
        loading.value = false
    })
}
function onRowSelect(r) {   
    console.log(r)
    hk.selectedRow = r.data
    visibleRight.value = true
    if(hk.selectedRow.reservation_stay){
        db.getDoc('Reservation Stay', hk.selectedRow.reservation_stay)
        .then((doc) => {
            hk.reservationStay = doc
        })
        .catch((error) => console.error(error));
    }
    else{
        hk.reservationStay = {} 
    }

}

function onDblClick(r) {
    alert("you double click on row: " + r.data.room_number)
}
function onViewCustomerDetail(name) {
    const dialogRef = dialog.open(GuestDetail, {
        data: {
            name: name
        },
        props: {
            header: 'Guest Detail',
            style: {
                width: '50vw',
            },
            breakpoints: {
                '960px': '75vw',
                '640px': '90vw'
            },
            modal: true
        },
        onClose: (options) => {
            console.log(options)
        }
    });
}
</script>
<style scoped>
.p-sidebar-mask.p-component-overlay{
    pointer-events:none !important;
}

</style>
