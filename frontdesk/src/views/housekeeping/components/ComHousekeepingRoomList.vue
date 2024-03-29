<template>
    <div class="hsk-wrapper h-full">
        <ComPlaceholder text="No Data" :loading="hk.loading" :is-not-empty="data.length > 0">
            <DataTable v-model:selection="hk.selectedRooms" class="cursor-pointer max-w-screen" dataKey="name"
                :value="data" stateStorage="local" stateKey="table_house_keeping_room_state" @row-click="onRowSelect"
                tableStyle="min-width: 50rem" showGridlines paginator :rows="20"
                scrollable
                :rowsPerPageOptions="[20, 30, 40, 50, 100, 500]" :page="page">
                <Column selectionMode="multiple" headerStyle="width: 3rem"></Column>
                <Column class="text-center" field="room_number" :header="$t('Room') + '#'"></Column>
                <Column :header="$t('Status')" headerClass="text-center" bodyClass="text-center">
                    <template #body="{ data }">
                        <span v-if="data?.housekeeping_status"
                            class="rounded-pill py-1 px-2 text-white border-round-3xl border-round-3xl white-space-nowrap "
                            :style="{ background: data.status_color }">
                            {{ $t(data.housekeeping_status)  }}
                        </span>
                    </template>
                </Column>
                <Column field="room_type" :header="$t('Room Type') "></Column>
                <Column field="reservation_stay" :header="$t('Reservation Stay')" headerClass="text-center"
                    bodyClass="text-center">
                    <template #body="slotProps">
                        <Button v-if="slotProps.data.reservation_stay"
                            @click="onViewReservationStayDetail(slotProps.data.reservation_stay)"
                            :label="slotProps.data.reservation_stay" link size="small"
                            class="link_line_action1 no-underline"></Button>
                    </template>
                </Column>
                <Column field="guest_name" :header="$t('Guest Name')">
                    <template #body="slotProps">
                        <Button v-if="slotProps.data.guest" class="color-purple-edoor p-0 no-underline"
                            @click="onViewCustomerDetail(slotProps.data.guest)" link>
                            <span class="link_line_action">{{ slotProps.data.guest }} - {{ slotProps.data.guest_name
                            }}</span>
                        </Button>
                    </template>
                </Column>
                <Column field="reservation_status" :header="$t('Reservation Status') " headerClass="text-center"
                    bodyClass="text-center">
                    <template #body="slotProps">

                        <ComHkReservationStatus :statusName="slotProps.data.reservation_status" />
                    </template>
                </Column>
                <Column field="housekeeper" :header="$t('Housekeeper')">
                    <template #body="slotProps">
                        <Button v-if="slotProps.data.housekeeper" @click="onAssignHousekeeper($event, slotProps.data)" link
                            size="small" class="link_line_action1 no-underline">
                            <span v-if="slotProps.data.housekeeper">{{ slotProps.data.housekeeper }}</span>
                        </Button>
                    </template>
                </Column>
            </DataTable>
        </ComPlaceholder>

    </div>
    <OverlayPanel ref="opHousekeeper">
        <ComOverlayPanelContent width="15rem" :loading="loading" @onCancel="onAssignHousekeeper($event, {})"
            @onSave="onSaveAssignHousekeeper">
            <ComSelect class="w-full" isFilter v-model="selected.housekeeper" placeholder="Assign Housekeeper"
                doctype="Housekeeper" />
        </ComOverlayPanelContent>
    </OverlayPanel>
    <Column field="housekeeping_status" header="Status" class="text-left">
        <template #body="slotProps">
            <ComHousekeepingChangeStatusButton @onSelected="onSelected" :data="slotProps.data" />
        </template>
    </Column>
    <div class="hkpanel">
        <Sidebar :overlay-class="'my-overlay-class'" :dismissable="false" class="top-20 slidebar-housekeeping -mt-1 w-full md:w-3"
            v-model:visible="visibleRight" position="right" @hide="SidebarClose">
            <template #header>
                <div class="line-height-1">
                    <div class="text-2xl">{{ $t('Detail OF') }} </div>
                    <div class="text-sm">{{ hk.selectedRow?.room_type }} # {{ hk.selectedRow?.room_number }}</div>
                </div>
            </template>
            <ComHousekeepingRoomDetailPanel></ComHousekeepingRoomDetailPanel>
        </Sidebar>
    </div>
</template>
<script setup>
import { ref, inject, postApi, computed, getDoc, onMounted } from '@/plugin';
import ComHousekeepingChangeStatusButton from './ComHousekeepingChangeStatusButton.vue'
import ComHousekeepingRoomDetailPanel from './ComHousekeepingRoomDetailPanel.vue';
import ComHkReservationStatus from '@/views/housekeeping/components/ComHkReservationStatus.vue'


import { useDialog } from 'primevue/usedialog';
import GuestDetail from "@/views/guest/GuestDetail.vue"
import Paginator from 'primevue/paginator';
import {i18n} from '@/i18n';
const { t: $t } = i18n.global;
const dialog = useDialog();
const loading = ref(false)
const page = ref(0)
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


function pageChange(page) {
    hk.pageState.page = page.page
    hk.pageState.rows = page.rows
    hk.loadData()
}

const data = computed(() => { 
    return hk.room_list
})
function onSelected(room, status) {
    hk.updateRoomStatus(room, status)
}
function onAssignHousekeeper($event, r) {
    if (!gv.cashier_shift?.name) {
        gv.toast('error', 'Please Open Cashier Shift.')
        return
    }
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
    if (hk.selectedRow.reservation_stay) {
        getHKSummary()
        db.getDoc('Reservation Stay', hk.selectedRow.reservation_stay)
            .then((doc) => {
                hk.reservationStay = doc
            })
            .catch((error) => console.error(error));
    }
    else {
        hk.reservationStay = {}
    }
    hk.room_block = undefined

    if (r.data.room_block) {
        getDoc("Room Block", r.data.room_block).then(r => {
            hk.room_block = r

        })
    }
}

onMounted(() => {
    if(window.isMobile){
        let elem = document.querySelectorAll(".p-dialog");
        if (elem){
            elem = elem[elem.length-1]
            elem?.classList.add("p-dialog-maximized"); // adds the maximized class
        }
    }
    let obj = JSON.parse(localStorage.getItem('table_house_keeping_room_state')); 
    if (obj){
        obj.first = 0;
        localStorage.setItem('table_house_keeping_room_state', JSON.stringify(obj));
    }
    hk.loadData()
})

function getHKSummary() {
    postApi('reservation.get_reservation_housekeeping_charge_summary', { reservation_stay: hk.selectedRow.reservation_stay }, '', false)
        .then((doc) => {
            hk.selectedRow.summary = doc.message
        })
        .catch((error) => console.error(error));
}

function onViewCustomerDetail(name) {
    const dialogRef = dialog.open(GuestDetail, {
        data: {
            name: name
        },
        props: {
            header: 'Guest Detail',
            style: {
                width: '80vw',
            },
            modal: true,
            closeOnEscape: false,
            position: 'top',
            maximizable: true,
            breakpoints:{
                '960px': '80vw',
                '640px': '100vw'
            },
        },
        onClose: (options) => {

        }
    });
}
function onViewReservationStayDetail(rs) {
    window.postMessage('view_reservation_stay_detail|' + rs, '*')
}
</script>
<style scoped>
.p-sidebar-mask.p-component-overlay {
    pointer-events: none !important;
}

.p-sidebar-mask {
    background: transparent;
}
</style>
