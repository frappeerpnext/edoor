<template>
    <div>

        <!-- <SplitButton class="border-split-none" label="Mores" icon="pi pi-list" :model="items" /> -->
        <Button class="border-none" icon="pi pi-chevron-down" iconPos="right" type="button" label="Mores" @click="toggle"
            aria-haspopup="true" aria-controls="folio_menu" />
        <Menu ref="folio_menu" id="folio_menu" :popup="true">
            <template #end>
                <button @click="onMarkAsMasterRoom()"
                    v-if="rs.reservationStay.is_master == 0 && (rs.reservationStay.reservation_status == 'Reserved' || rs.reservationStay.reservation_status == 'In-house')"
                    class="w-full p-link flex align-items-center py-2 px-3 text-color hover:surface-200 border-noround">
                    <i class="pi pi-file-edit" />
                    <span class="ml-2">Mark as Master Room </span>
                </button>

                <button @click="onUndoCheckIn()"
                    v-if="rs.reservationStay.reservation_status == 'In-house' && rs.reservationStay?.arrival_date == working_day?.date_working_day"
                    class="w-full p-link flex align-items-center py-2 px-3 text-color hover:surface-200 border-noround">
                    <i class="pi pi-file-edit" />
                    <span class="ml-2">Undo Check-In</span>
                </button>

                <button @click="onMarkasPaybyMasterRoom()"
                    v-if="rs.reservationStay.is_master == 0 && (rs.reservationStay.reservation_status == 'Reserved' || rs.reservationStay.reservation_status == 'In-house')"
                    class="w-full p-link flex align-items-center py-2 px-3 text-color hover:surface-200 border-noround">
                    <i class="pi pi-file-edit" />
                    <span class="ml-2">Mark as Pay by Master Room </span>
                </button>

                <button @click="onUnmarkasPaybyMasterRoom()"
                    v-if="rs.reservationStay.reservation_status == 'In-house' && rs.reservationStay?.arrival_date == working_day?.date_working_day"
                    class="w-full p-link flex align-items-center py-2 px-3 text-color hover:surface-200 border-noround">
                    <i class="pi pi-file-edit" />
                    <span class="ml-2"> Unmark as Pay by Master Room </span>
                </button>
                <button @click="onAuditTrail" class="w-full p-link flex align-items-center py-2 px-3 text-color hover:surface-200 border-noround">
                    <i class="pi pi-file-edit" />
                    <span class="ml-2">Audit Trail</span>
                </button>


            </template>
        </Menu>
    </div>
</template>
<script setup>
import { inject, ref, useConfirm, useToast, postApi } from "@/plugin";
import ComAuditTrail from '../../../components/layout/components/ComAuditTrail.vue';
const socket = inject("$socket")
const confirm = useConfirm()
const toast = useToast();
const emit = defineEmits(['onAuditTrail',"onRefresh"])
const items = ref([])
const folio_menu = ref();
const rs = inject("$reservation_stay")
const working_day = ref(JSON.parse(localStorage.getItem("edoor_working_day")))

const toggle = (event) => {
    folio_menu.value.toggle(event);
}
items.value.push({
    label: "Audit Trail",
    icon: 'pi pi-history',
    command: () => {
        emit('onAuditTrail')
    }
})
items.value.push({
    label: "Allow post to City Ledger",
    icon: 'pi pi-history',
    command: () => {
        emit('onAuditTrail')
    }
})
items.value.push({
    label: "Edit Trail",
    icon: 'pi pi-history',
    command: () => {
        emit('onAuditTrail')
    }
})
items.value.push({
    label: "Edit Trail",
    icon: 'pi pi-history',
    command: () => {
        emit('onAuditTrail')
    }
})


function onMarkAsMasterRoom() {
    confirm.require({
        message: 'Are you sure you want to mark this room as master room?',
        header: 'Confirmation',
        icon: 'pi pi-exclamation-triangle',
        acceptClass: 'border-none crfm-dialog',
        rejectClass: 'hidden',
        acceptIcon: 'pi pi-check-circle',
        acceptLabel: 'Ok',
        accept: () => {
            postApi("reservation.mark_as_master_folio", {
                reservation: rs.reservation.name,
                reservation_stay: rs.reservationStay.name
            }).then((doc) => {

                rs.reservationStay = doc.message
                socket.emit("RefreshReservationDetail", rs.reservation.name)

                //toast.add({ severity: 'info', summary: 'Information', detail: 'Update successfully', life: 3000 });
            })

        },

    });
}

function onUndoCheckIn() {
    confirm.require({
        message: 'Are you sure you want to undo check in this reservation?',
        header: 'Confirmation',
        icon: 'pi pi-exclamation-triangle',
        acceptClass: 'border-none crfm-dialog',
        rejectClass: 'hidden',
        acceptIcon: 'pi pi-check-circle',
        acceptLabel: 'Ok',
        accept: () => {
            rs.loading = true
            postApi("reservation.undo_check_in", {
                reservation_stay: rs.reservationStay.name
            },
                "Undo check in successfully"
            ).then((doc) => {
                rs.reservationStay = doc.message
               
                socket.emit("RefreshReservationDetail", rs.reservation.name)
                socket.emit("RefresheDoorDashboard", doc.message.property)
                rs.loading = false
                setTimeout(() => {
                    emit('onRefresh')
                }, 1000);


            }).catch((err) => {
                rs.loading = false
            })

        },

    });
}

function onMarkasPaybyMasterRoom(){
    confirm.require({
        message: 'Are you sure you want to Mark as Pay by Master Room?',
        header: 'Confirmation',
        icon: 'pi pi-exclamation-triangle',
        acceptClass: 'border-none crfm-dialog',
        rejectClass: 'hidden',
        acceptIcon: 'pi pi-check-circle',
        acceptLabel: 'Ok',
        accept: () => {
            
            db.updateDoc('Reservation Stay', rs.reservationStay.name, {
                pay_by_company: 1,
            })
                .then((doc) => {
                    rs.folios.forEach(r => r.is_master = false);
                    rs.reservationStay.pay_by_company = doc.pay_by_company;
                    toast.add({
                        severity: 'success', summary: 'Mark Folio as Master Folio',
                        detail: 'Mark Folio as Master Folio Successfully', life: 3000
                    });
                })
        },

    });
   
}
function onUnmarkasPaybyMasterRoom(){
    confirm.require({
        message: 'Are you sure you want to Unmark as Pay by Master Room?',
        header: 'Confirmation',
        icon: 'pi pi-exclamation-triangle',
        acceptClass: 'border-none crfm-dialog',
        rejectClass: 'hidden',
        acceptIcon: 'pi pi-check-circle',
        acceptLabel: 'Ok',
        accept: () => {
            rs.loading = true
            postApi("reservation.undo_check_in", {
                reservation_stay: rs.reservationStay.name
            },
                "Undo check in successfully"
            ).then((doc) => {
                rs.reservationStay = doc.message
                socket.emit("RefreshReservationDetail", rs.reservation.name)
                socket.emit("RefresheDoorDashboard", doc.message.property)
                rs.loading = false
                setTimeout(() => {
                    emit('onRefresh')
                }, 1000);


            }).catch((err) => {
                rs.loading = false
            })

        },

    });
   
}

function onAuditTrail(){
    emit('onAuditTrail')
}
</script>