<template>
    <!-- {{ hk.reservationStay }} -->
    <div class="pb-20">
        <div class="">
            <hr class="mb-3">
            <div class="py-2 mt-1 border-1  bg-slate-200 font-medium text-center">
                {{ $t('Room') }}
                </div>
            <table>
                <ComStayInfoNoBox label="Room Number" :value="hk.selectedRow?.room_number" />
                <ComStayInfoNoBox label="Status" :value="$t(hk.selectedRow?.housekeeping_status)" />
                <ComStayInfoNoBox label="Housekeeper" :value="hk.selectedRow?.housekeeper" />
            </table>
        </div>
        <div class="grid mt-2">
            <div class="col-6" v-if="!hk.room_block">
                <SplitButton :disabled="hk.selectedRow.room_status == 'Room Block'" class="w-full"
                    :buttonProps="{ style: { backgroundColor: hk.selectedRow?.status_color } }"
                    :label="$t(hk.selectedRow?.housekeeping_status_code)" :model="items" :color="hk.selectedRow?.status_color"
                    :menuButtonProps="{ style: { backgroundColor: hk.selectedRow?.status_color } }"
                    :class="{ 'active-button': true } ">
                </SplitButton>
            </div>
            <div class="col-6">
                <Button class="w-full" :label="$t('Assign Housekeeper')" severity="warning"
                    @click="onAssignHousekeeper($event)"></Button>
                <OverlayPanel ref="opHousekeeper">
                    <ComOverlayPanelContent :loading="loading" @onCancel="onAssignHousekeeper($event, {})"
                        @onSave="onSaveAssignHousekeeper">
                        <ComSelect class="w-full" isFilter v-model="selected.housekeeper" placeholder="Assign Housekeeper"
                            doctype="Housekeeper" />
                    </ComOverlayPanelContent>
                </OverlayPanel>
            </div>
        </div>
        <div v-if="hk && hk.reservationStay && Object.keys(hk.reservationStay).length > 0">
            <div class="py-2 mt-1 border-1  bg-slate-200 font-medium text-center"> {{ $t('Reservation') }} </div>
            <table>
                <ComStayInfoNoBox label="Res No">
                    <Button @click="onViewReservationDetail(hk?.reservationStay?.reservation)"
                        class="-ml-3 link_line_action1" text>{{ hk?.reservationStay?.reservation }}</Button>
                </ComStayInfoNoBox>
                <ComStayInfoNoBox label="Res Stay No">
                    <Button @click="onViewReservationStayDetail(hk?.reservationStay?.name)" class="-ml-3 link_line_action1"
                        text>{{ hk?.reservationStay?.name }}</Button>
                </ComStayInfoNoBox>
                <ComStayInfoNoBox label="Type" :value="hk?.reservationStay?.reservation_type" v-tippy="hk?.reservationStay?.reservation_type !== 'GIT' ? 'Free Independent Traveler'
                    : (hk?.reservationStay?.reservation_type !== 'FIT' ? 'Group Inclusive Tour' : '')" />
                <ComStayInfoNoBox v-if="hk?.reservationStay?.reservation_type != 'FIT'" label="Group">
                    <div class="w-full overflow-hidden white-space-nowrap -ml-3 text-overflow-ellipsis">
                        <div v-tippy="hk?.reservationStay?.group_code" class="inline">
                            {{ hk?.reservationStay?.group_code }}
                        </div>
                        <div v-tippy="hk?.reservationStay?.group_name" class="inline">
                            {{ hk?.reservationStay?.group_name }}
                        </div>
                    </div>
                </ComStayInfoNoBox>
                <ComStayInfoNoBox label="Status">
                    <span class="-ms-3 font-semibold" :style="{ color: hk.reservationStay?.status_color }">{{
                        hk?.reservationStay?.reservation_status }}</span>
                </ComStayInfoNoBox>
                <ComStayInfoNoBox label="Guest Name">
                    <Button @click="onViewCustomerDetail(hk?.reservationStay?.guest)" class="-ml-3 link_line_action1"
                        text>{{ hk?.reservationStay?.guest }} - {{ hk?.reservationStay?.guest_name }}</Button>
                </ComStayInfoNoBox>
                <ComStayInfoNoBox label="Nationality" :value="hk?.reservationStay?.nationality" />
                <ComStayInfoNoBox label="Phone Number" :value="hk?.reservationStay?.guest_phone_number" />
                <ComStayInfoNoBox label="Email" :value="hk?.reservationStay?.guest_email" />
                <ComStayInfoNoBox label="PAX" :value="hk?.reservationStay?.adult + ' / ' + hk?.reservationStay?.child" />
                <ComStayInfoNoBox label="Arrival">
                    <span class="-ms-3 font-semibold">
                        {{ gv.dateFormat(hk?.reservationStay?.arrival_date) }} - {{
                            gv.timeFormat(hk?.reservationStay?.arrival_time) }}
                    </span>
                </ComStayInfoNoBox>
                <ComStayInfoNoBox label="Departure">
                    <span class="-ms-3 font-semibold">
                        {{ gv.dateFormat(hk?.reservationStay?.departure_date) }} - {{
                            gv.timeFormat(hk?.reservationStay?.departure_time) }}
                    </span>
                </ComStayInfoNoBox>
                <ComStayInfoNoBox label="Night(s)" :value="hk?.reservationStay?.room_nights" />
            </table>
            <template>
                <div class="py-2 mt-3 border-1  bg-slate-200 font-medium text-center">Housekeeping Charge Summary</div>
                <table class="w-full" v-if="hk.selectedRow.summary">
                    <ComStayInfoNoBox label="TOTAL DEBIT" :value="gv.currencyFormat(hk.selectedRow.summary.debit)" />
                    <ComStayInfoNoBox label="TOTAL CREDIT" :value="gv.currencyFormat(hk.selectedRow.summary.credit)" />
                    <ComStayInfoNoBox label="BALANCE"
                        :value="gv.currencyFormat(hk.selectedRow.summary.debit - hk.selectedRow.summary.credit)" />
                </table>
            </template>
        </div>
        <div v-if="hk.reservationStay?.owner || hk.reservationStay?.modified_by">
            <div class="py-2 my-3 mb-10 border-1  bg-slate-200 font-medium wrap__sp_not">{{ hk.reservationStay.housekeeping_note }}</div>
            <div class="mb-5 leading-5 text-sm ">
                <div class="mt-auto">
                    <span class="italic">{{ $t('Created by') }} : </span>
                    <span class="text-500 font-italic">
                        {{ hk.reservationStay?.owner.split("@")[0] }}
                        <ComTimeago :date="hk.reservationStay?.creation" />
                    </span>
                </div>
                <div class="mt-auto">
                    <span class="italic">   {{$t('Last Modified')}} : </span>
                    <span class="text-500 font-italic">
                        {{ hk.reservationStay?.modified_by.split("@")[0] }}
                        <ComTimeago :date="hk.reservationStay?.modified" />

                    </span>
                </div>
                <div>
                    <div v-if="hk.reservationStay?.checked_in_by || hk.reservationStay?.checked_out_by">
                        <div v-if="hk.reservationStay?.checked_in_by || hk.reservationStay?.checked_in_date">
                            <span class="italic">{{ $t('Checked-in by') }} : </span>
                            <span class="text-500 font-italic">
                                {{ hk.reservationStay?.checked_in_by.split("@")[0] }}
                                <ComTimeago :date="hk.reservationStay?.checked_in_date" />
                            </span>
                        </div>
                        <div v-if="hk.reservationStay?.checked_out_by || hk.reservationStay?.checked_out_date">
                            <span class="italic"> {{ $t('Checked-out by') }} : </span>
                            <span class="text-500 font-italic">
                                {{ hk.reservationStay?.checked_out_by.split("@")[0] }}
                                <ComTimeago :date="hk.reservationStay?.checked_out_date" />
                            </span>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <div v-if="hk.room_block">
            <div class="py-2 mt-1 border-1  bg-slate-200 font-medium text-center"> {{ $t('Room Block') }} </div>
            <table>
                <ComStayInfoNoBox label="Block Name">
                    <Button @click="onOpenLink(hk.room_block.name)" class="-ml-3 link_line_action1" text>{{
                        hk?.room_block?.name }}</Button>
                </ComStayInfoNoBox>
                <ComStayInfoNoBox label="Room Type" :value="hk?.room_block?.room_type" />
                <ComStayInfoNoBox label="Block Date" :value="gv.dateFormat(hk?.room_block?.block_date)" />
                <ComStayInfoNoBox label="Start Date" :value="gv.dateFormat(hk?.room_block?.start_date)" />
                <ComStayInfoNoBox label="End Date" :value="gv.dateFormat(hk?.room_block?.end_date)" />
                <ComStayInfoNoBox label="Total Night(s)" :value="hk?.room_block?.total_night_count" />
                <ComStayInfoNoBox label="Reason" :value="hk?.room_block?.reason" />
                <ComStayInfoNoBox label="Block by" :value="hk?.room_block?.modified_by?.split('@')[0]" />
            </table>
        </div>

    </div>
</template>
<script setup>
import { inject, ref, useToast, onMounted, onUnmounted } from '@/plugin';
const hk = inject("$housekeeping")
const edoor_setting = JSON.parse(localStorage.getItem('edoor_setting'))
const housekeeping_status_code = ref(edoor_setting.housekeeping_status_code)
const visible = ref(false)
const toast = useToast();
const opHousekeeper = ref()
const selected = ref({})
const submitLoading = ref(false)
const items = ref([])
const show = ref()
const frappe = inject("$frappe")
const db = frappe.db()
const gv = inject('$gv');
import {i18n} from '@/i18n';
const { t: $t } = i18n.global;
if (housekeeping_status_code.value.length > 0) {
    housekeeping_status_code.value.forEach(h => {

        items.value.push({
            label: $t(h.status),
            style:{minWidth:'185px'},
            command: () => {

                onSelected(h)
            }
        })

    });
}

/// change housekeeping status in slidbar
const toggle = (event) => {
    show.value.toggle(event);
};
function onSelected($event) {
    if (!hk.selectedRow) {
        toast.add({ severity: 'warn', summary: "Change housekeeping status", detail: "Please select roow to change housekeeping status", life: 3000 })
    } else {
        db.updateDoc('Room', hk.selectedRow.name, {
            housekeeping_status_code: $event.status
        })
            .then((doc) => {
                hk.selectedRow.housekeeping_status = doc.housekeeping_status
                hk.selectedRow.housekeeping_status_code = $event.status
                hk.selectedRow.status_color = doc.status_color
                toast.add({ severity: 'success', summary: "Change Status", detail: "Change housekeeping status successfully", life: 3000 })
                window.postMessage({"action":"ComHousekeepingStatus"},"*")
                submitLoading.value = false
            })
            .catch((error) => {
                submitLoading.value = false
            });
    }
}
// Change housekeeper in slidbar
function onAssignHousekeeper($event) {
    opHousekeeper.value.toggle($event)
}

function onSaveAssignHousekeeper($event) {
    if (!gv.cashier_shift?.name) {
        gv.toast('error', 'Please Open Cashier Shift.')
        return
    }
    if (!hk.selectedRow) {
    } else {
        db.updateDoc('Room', hk.selectedRow.name, {
            housekeeper: selected.value.housekeeper,
        })
            .then((doc) => {
                hk.selectedRow.housekeeper = doc.housekeeper
                toast.add({ severity: 'success', summary: "Assign housekeeping", detail: "Assign housekeeping status successfully", life: 3000 })
                window.socket.emit("RefreshData", { property: setting.property.name, action: "refresh_hk" })
                submitLoading.value = false
                opHousekeeper.value.hide()
            })
            .catch((error) => {
                submitLoading.value = false
            });
    }
}

onMounted(() => {
    window.socket.on("ComHousekeepingRoomDetailPanel", (arg) => {
        if (arg.property == window.property_name) {
            setTimeout(function () {
                hk.loadData(false)
            }, 3000)
        }
    })
})

function onOpenLink(data) {
    window.postMessage('view_room_block_detail' + "|" + data, '*')
}

function onViewCustomerDetail(name) {
    window.postMessage('view_guest_detail|' + name, '*')
}

function onViewReservationStayDetail(rs) {
    window.postMessage('view_reservation_stay_detail|' + rs, '*')

}

function onViewReservationDetail(rs) {
    window.postMessage('view_reservation_detail|' + rs, '*')
}

onUnmounted(() => {
    window.socket.off("ComHousekeepingRoomDetailPanel")
})
</script>
