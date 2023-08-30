<template>
    <div class="">
        <ComPlaceholder text="No Data"  :loading="hk.loading" :is-not-empty="data.length > 0"> 
        <DataTable 
        v-model:selection="hk.selectedRooms" 
        class="cursor-pointer res_list_scroll" 
        dataKey="name" 
        :value="data" 
        stateStorage="local"
        stateKey="table_house_keeping_room_state"
        @row-dblclick="onDblClick"
        @row-click="onRowSelect" 
        tableStyle="min-width: 50rem" 
        paginator 
        showGridlines 
        :rows="20" 
        :rowsPerPageOptions="[20, 30, 40, 50]">
            <Column selectionMode="multiple" headerStyle="width: 3rem"></Column>
            <Column class="text-center" field="room_number" header="Room #"></Column>
            <Column  header="Status" headerClass="text-center" bodyClass="text-center">
                <template #body="{ data }">
                    <span v-if="data?.housekeeping_status" class="rounded-pill py-1 px-2 text-white border-round-3xl border-round-3xl white-space-nowrap " :style="{ background: data.status_color }">
                        {{ data.housekeeping_status }}
                    </span> 
                </template>
            </Column>
            <Column field="room_type" header="Room Type"></Column>
            <Column field="reservation_stay" header="Reservation Stay" headerClass="text-center" bodyClass="text-center">
                <template #body="slotProps">
                    <Button v-if="slotProps.data.reservation_stay" @click="onViewReservationStayDetail(slotProps.data.reservation_stay)" :label="slotProps.data.reservation_stay" link
                        size="small" class="link_line_action1 no-underline"></Button>
                </template>
            </Column>
           
            
            <Column field="guest_name" header="Guest Name">
                <template #body="slotProps">
                    <Button v-if="slotProps.data.guest" class="color-purple-edoor p-0 no-underline" @click="onViewCustomerDetail(slotProps.data.guest)" link>
                        <span class="link_line_action">{{ slotProps.data.guest }} - {{ slotProps.data.guest_name }}</span>
                    </Button>
                </template>
            </Column>
            <Column field="reservation_status" header="Reservation Status" headerClass="text-center" bodyClass="text-center">
                <template #body="slotProps">
                    <ComReservationStatus v-if="slotProps.data.guest" :statusName="slotProps.data.reservation_status"/>
                </template>
            </Column>
            <Column field="housekeeper" header="Housekeeper">
                <template #body="slotProps">
                    <Button v-if="slotProps.data.housekeeper" @click="onAssignHousekeeper($event, slotProps.data)" link size="small" class="link_line_action1 no-underline">
                        <span v-if="slotProps.data.housekeeper">{{slotProps.data.housekeeper}}</span>
                    </Button>
                </template>
            </Column>
            <div class="absolute bottom-6 left-4">
                <strong>Total Records: <span class="ttl-column_re">{{hk.room_list.length}}</span></strong>
            </div>
        </DataTable>
        </ComPlaceholder>
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
        <Sidebar :dismissable="false" class="top-20 -mt-1 w-3" v-model:visible="visibleRight" position="right" @hide="SidebarClose" >
            <ComHousekeepingRoomDetailPanel></ComHousekeepingRoomDetailPanel>
        </Sidebar>
        </div>
    </div>
</template>

<script setup>

import { ref, inject,postApi,computed } from '@/plugin';
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
const data = computed(()=>{
    return gv.search(hk.room_list, hk.filter.keyword, 'room_number,guest,guest_name,room_type,housekeeper,reservation_stay')
})
 
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

function SidebarClose() {
    const elements_row_hk = document.querySelectorAll('.active_row_hk');
    elements_row_hk.forEach(elements_row_hk => {
                elements_row_hk.classList.remove('active_row_hk');
        });
    }
function onRowSelect(r) {
    const elements_row_hk = document.querySelectorAll('.active_row_hk');
    if (r.originalEvent.currentTarget.classList.contains('active_row_hk')) {
        visibleRight.value = false;
        r.originalEvent.currentTarget.classList.remove('active_row_hk');
    } else {
        elements_row_hk.forEach(elements_row_hk => {
            if (elements_row_hk !== r.originalEvent.currentTarget) {
                elements_row_hk.classList.remove('active_row_hk');
            }
        });
        visibleRight.value = true
        r.originalEvent.currentTarget.classList.add('active_row_hk');
    }

    hk.selectedRow = r.data
    if(hk.selectedRow.reservation_stay){
        getHKSummary()
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
function getHKSummary(){ 
    postApi('reservation.get_reservation_housekeeping_charge_summary',{ reservation_stay :hk.selectedRow.reservation_stay},'',false)  
    .then((doc) => {
        hk.selectedRow.summary = doc.message
    })
  .catch((error) => console.error(error));
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
                width: '75vw',
            },
            breakpoints: {
                '960px': '75vw',
                '640px': '90vw'
            },
            modal: true,
            closeOnEscape: false,
            position: 'top',
            maximizable: true
        },
        onClose: (options) => {
            console.log(options)
        }
    });
}
function onViewReservationStayDetail(rs){
    window.postMessage('view_reservation_stay_detail|'+rs, '*')

}
</script>
<style scoped>
.p-sidebar-mask.p-component-overlay{
    pointer-events:none !important;
}
</style>
