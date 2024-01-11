<template>
    <div>
        <Button class="border-none" icon="pi pi-chevron-down" iconPos="right" type="button" label="Mores" @click="toggle"
            aria-haspopup="true" aria-controls="menu" />

        <Menu ref="menu" id="menu" :popup="true">
            <template #end>
                <button @click="onGroupAssignRoom"
                    class="w-full p-link flex align-items-center py-2 px-3 text-color hover:surface-200 border-noround">
                    <i class="pi pi-file-edit" />
                    <span class="ml-2">Group Assign Room</span>
                </button>
                <button @click="onGroupChangeRate"
                    class="w-full p-link flex align-items-center py-2 px-3 text-color hover:surface-200 border-noround">
                    <ComIcon icon="roomRate" style="height: 14px;" />
                    <span class="ml-2">Group Change Rate</span>
                </button>

                <button @click="onGroupChangeStayDate"
                    class="w-full p-link flex align-items-center py-2 px-3 text-color hover:surface-200 border-noround">
                    <ComIcon icon="iconChangeStay" style="height: 14px;" />
                    <span class="ml-2">Group Change Stay Date</span>
                </button>
                <button @click="onChangeStatus('No Show')"
                    class="w-full p-link flex align-items-center py-2 px-3 text-color hover:surface-200 border-noround">
                    <i class="pi pi-eye-slash" />
                    <span class="ml-2">Group No Show</span>
                </button>

                <button @click="onChangeStatus('Cancelled')"
                    class="w-full p-link flex align-items-center py-2 px-3 text-color hover:surface-200 border-noround">
                    <i class="pi pi-user-minus" />
                    <span class="ml-2">Group Cancel</span>
                </button>
                <button @click=" onChangeStatus('Void')"
                    class="w-full p-link flex align-items-center py-2 px-3 text-color hover:surface-200 border-noround">
                    <i class="pi pi-file-excel" />
                    <span class="ml-2">Group Void</span>
                </button>
                <button @click=" onGroupCheckIn(true)"
                    class="w-full p-link flex align-items-center py-2 px-3 text-color hover:surface-200 border-noround">
                    <ComIcon icon="checkin-black" style="height: 14px;" />
                    <span class="ml-2">Group Check-In</span>
                </button>
                <button @click="onGroupUndoCheckIn()"
                    class="w-full p-link flex align-items-center py-2 px-3 text-color hover:surface-200 border-noround">
                    <i class="pi pi-undo" />
                    <span class="ml-2">Group Undo Check-In</span>
                </button>
                <button @click=" onGroupCheckOut(true)"
                    class="w-full p-link flex align-items-center py-2 px-3 text-color hover:surface-200 border-noround">
                    <ComIcon icon="checkoutBlack" style="height: 14px;" />
                    <span class="ml-2">Group Check Out</span>
                </button>
                <button @click="onGroupUndoCheckOut"
                    class="w-full p-link flex align-items-center py-2 px-3 text-color hover:surface-200 border-noround">
                    <i class="pi pi-undo" />
                    <span class="ml-2">Group Undo Check Out</span>
                </button>
                <span>

                    <button @click="onMarkAsPaidbyMasterroom()"
                        class="w-full p-link flex align-items-center py-2 px-3 text-color hover:surface-200 border-noround">
                        <ComIcon icon="BilltoMasterRoom" style="height:13px;"></ComIcon>
                        <span class="ml-2">Mark as Paid by Master Room {{ }}</span>
                    </button>

                    <button @click="onUnMarkAsPaidbyMasterroom()"
                        class="w-full p-link flex align-items-center py-2 px-3 text-color hover:surface-200 border-noround">
                        <ComIcon icon="BilltoMasterRoom" style="height:13px;"></ComIcon>
                        <span class="ml-2">Unmark as Paid by Master Room </span>
                    </button>
                </span>


                <button @click="onAllowPostToCityLedger"
                    class="w-full p-link flex align-items-center py-2 px-3 text-color hover:surface-200 border-noround">
                    <ComIcon icon="IconBillToCompany" style="height:15px;"></ComIcon>
                    <span class="ml-2">Allow Post to City Ledger</span>
                </button>
                <button @click="onUnAllowPostToCityLedger"
                    class="w-full p-link flex align-items-center py-2 px-3 text-color hover:surface-200 border-noround">
                    <ComIcon icon="IconBillToCompany" style="height:15px;"></ComIcon>
                    <span class="ml-2">Disallow Post to City Ledger</span>
                </button>
                <button class="w-full p-link flex align-items-center py-2 px-3 text-color hover:surface-200 border-noround"
                    @click="onTransferStay">
                    <ComIcon icon="iconMoveStay" style="height: 14px;" />
                    <span class="ml-2">Transfer Stay to Other Reservation</span>
                </button>
                <button v-if="rs.reservation.reservation_type == 'FIT'" @click="onMarkasGITReservation()"
                    class="w-full p-link flex align-items-center py-2 px-3 text-color hover:surface-200 border-noround">
                    <ComIcon icon="userGif" style="height: 15px;" />
                    <span class="ml-2">Mark as GIT Reservation</span>
                </button>
                <button v-else @click="onMarkasFITReservation()"
                    class="w-full p-link flex align-items-center py-2 px-3 text-color hover:surface-200 border-noround">

                    <ComIcon icon="userProfile" style="height:15px;"></ComIcon>
                    <span class="ml-2">Mark as FIT Reservation </span>
                </button>
                <button v-if="rs.selecteds == 1" @click="click_me"
                    class="w-full p-link flex align-items-center py-2 px-3 text-color hover:surface-200 border-noround">
                    <i class="pi pi-car" />
                    <span class="ml-2">click_me</span>
                </button>
                <button v-else @click="onPickDrop"
                    class="w-full p-link flex align-items-center py-2 px-3 text-color hover:surface-200 border-noround">
                    <i class="pi pi-car" />
                    <span class="ml-2">Pickup / Drop Off</span>
                </button>
                <button @click="onAuditTrail"
                    class="w-full p-link flex align-items-center py-2 px-3 text-color hover:surface-200 border-noround">
                    <i class="pi pi-history" />
                    <span class="ml-2">Audit Trail</span>
                </button>

            </template>
        </Menu>

    </div>
</template>
<script setup>
import { useDialog, inject, ref, useConfirm, useToast, postApi } from "@/plugin";
import ComAuditTrail from '@/components/layout/components/ComAuditTrail.vue';
import ComGroupAssignRoom from "@/views/reservation/components/form/ComGroupAssignRoom.vue";
import ComGroupChangeRate from "@/views/reservation/components/form/ComGroupChangeRate.vue";
import ComGroupChangeStayDate from "@/views/reservation/components/form/ComGroupChangeStayDate.vue";
import ComFormSetupArrivalAndDeparture from '@/views/reservation/components/ComFormSetupArrivalAndDeparture.vue';
import ComDialogNote from '@/components/form/ComDialogNote.vue';
import ComConfirmCheckIn from '@/views/reservation/components/confirm/ComConfirmCheckIn.vue'
import ComConfirmTransferStay from '@/views/reservation/components/ComConfirmTransferStay.vue'

const dialog = useDialog();


const confirm = useConfirm()
const toast = useToast();
const emit = defineEmits(['onAuditTrail', "onRefresh"])
const menu = ref();

const gv = inject("$gv")
const rs = inject("$reservation")
const frappe = inject('$frappe');
const db = frappe.db();
const reservation = ref({})

const toggle = (event) => {
    menu.value.toggle(event);
}

function onChangeStatus(reservation_status) {

    if (validateSelectReservation()) {
        let confirm_message = ""
        if (reservation_status == "Cancelled") {
            confirm_message = "You are about to cancel reservation(s).<br/> Once the cancellation is complete, you will no longer be able to make any changes to the reservation. <br/> If you have a cancellation charge, please update the folio transaction first."
        } else if (reservation_status == "Void") {
            confirm_message = "You are about to void  reservation(s). Once the void is complete, you will no longer be able to make any changes to the reservation."
        } else {
            confirm_message = `You are about to mark   reservation(s) as No Show.
                    If you have a No Show charge, please update the folio transaction first.
                    If you want to sell this room, please untick on check box Reserved Room`
        }

        const stays = rs.selecteds.filter(r => r.is_active_reservation == 1 && r.allow_user_to_edit_information == 1)

        if (stays.length == 0) {
            toast.add({ severity: 'warn', detail: "Please select active reservation stay to " + reservation_status, life: 3000 })
            return
        }

        onUpdateReservationStatus(
            "Confirm " + reservation_status + " Note",
            {
                api_url: "reservation.update_reservation_status",
                method: "POST",
                confirm_message: confirm_message,
                data: {
                    reservation: rs.reservation.name,
                    reserved_room: false,
                    status: reservation_status,
                    show_reserved_room: reservation_status == "No Show" ? true : false,
                    stays: rs.selecteds.filter(r => r.is_active_reservation == 1 && r.allow_user_to_edit_information == 1)
                },

            }
        )

    }
}


function onUpdateReservationStatus(header = "Confirm Note", data) {
    const dialogRef = dialog.open(ComDialogNote, {
        data: data,
        props: {
            header: header,
            style: {
                width: '50vw',
            },
            modal: true,
            maximizable: true,
            closeOnEscape: false,
            position: "top"
        },
        onClose: (options) => {
            const data = options.data;
        }

    });

}


function validateSelectReservation() {
    if (rs.selecteds && rs.selecteds.length > 0) {
        return true
    }
    else {
        gv.toast('warn', 'Please select reservation stay.')
        return false
    }
}



function onGroupCheckIn() {
    const stays = rs.selecteds.filter(r => r.is_active_reservation == 1 && r.allow_user_to_edit_information == 1)

    if (stays.length == 0) {
        toast.add({ severity: 'warn', detail: "Please select active reservation stay to Check In", life: 3000 })
        return
    }
    if (rs.selecteds.filter(r => r.reservation_status != 'In-house').length == 0) {
        toast.add({ severity: 'warn', summary: "Group Check In", detail: "Please select Reserved reservation stay to check in.", life: 3000 })
        return
    } else {
        const stays = rs.selecteds.filter(r => r.is_active_reservation == 1 && r.allow_user_to_edit_information == 1).map((r) => r.name)
        if (stays.length == 0) {
            if (rs.reservationStays.length > 1) {
                toast.add({ severity: 'warn', summary: "Group Check In", detail: "Please select reservation stay to check in.", life: 3000 })
                return
            } else {
                rs.selecteds = rs.reservationStays
            }

        }
        const dialogRef = dialog.open(ComConfirmCheckIn, {
            data: {
                stays: rs.selecteds
            },
            props: {
                header: 'Confirm Check In',
                style: {
                    width: '450px',
                },
                modal: true,
                closeOnEscape: false
            },
            onClose: (options) => {
                const result = options.data;

                if (result) {
                    rs.loading = true

                    postApi("reservation.check_in", {
                        reservation: rs.reservation.name,
                        reservation_stays: rs.selecteds.map(d => d["name"])
                    }).then((result) => {
                        rs.loading = false
                        window.socket.emit("ReservationDetail", window.reservation);
                        window.socket.emit("Dashboard", window.property_name);
                        window.socket.emit("Frontdesk", window.property_name);
                        window.socket.emit("ReservationList", { property: window.property_name })
                        window.socket.emit("ReservationStayList", { property: window.property_name })
                        window.socket.emit("ComGuestLedger", { property: window.property_name })
                        window.socket.emit("Reports", window.property_name)
                        window.socket.emit("FolioTransactionList", window.property_name)

                        rs.selecteds.forEach(r => {
                            window.socket.emit("ReservationStayDetail", { reservation_stay: r.name })
                        });


                    })
                        .catch((err) => {
                            rs.loading = false
                        })
                }
            }
        })
    }


}


function onGroupUndoCheckIn() {
    if (rs.selecteds.filter(r => r.reservation_status == 'In-house').length == 0) {
        toast.add({ severity: 'warn', summary: "Group Undo Check In", detail: "Please select  In-house reservation stay to undo check in.", life: 3000 })
        return
    } else {
        const dialogRef = dialog.open(ComDialogNote, {
            data: {
                api_url: "reservation.undo_check_in",
                method: "POST",
                confirm_message: "Are you sure you want to undo check in this reservation?",
                data: {
                    reservation_stay: rs.selecteds.filter(r => r.reservation_status == 'In-house').map(d => d.name),
                    reservation: rs.reservation.name,
                    property: window.property_name
                }
            },
            props: {
                header: "Undo Checked In",
                style: {
                    width: '50vw',
                },
                modal: true,
                maximizable: true,
                closeOnEscape: false,
                position: "top"
            },
            onClose: (options) => {
                const result = options.data;
                if (result) {
                    rs.loading = false
                    //wait for equeue process finish
                    // rs.LoadReservation(window.reservation, false)
                    window.socket.emit("ReservationList", { property: window.property_name })
                    window.socket.emit("ReservationStayList", { property: window.property_name })
                    window.socket.emit("ComGuestLedger", { property: window.property_name })
                    window.socket.emit("Reports", window.property_name)
                    window.socket.emit("ReservationStayDetail", { reservation_stay: window.reservation_stay })
                    window.socket.emit("ReservationDetail", window.reservation)
                    window.socket.emit("Frontdesk", window.property_name)
                    window.socket.emit("FolioTransactionList", window.property_name)

                    setTimeout(() => {
                        emit('onRefresh')
                    }, 1000);
                }

            }
        });
    }
}


function onGroupCheckOut(is_not_undo = false) {
    const isSelect = validateSelectReservation()
    if (isSelect) {
        const stays = rs.selecteds.filter(r => r.is_active_reservation == 1 && r.allow_user_to_edit_information == 1).map((r) => r.name)
        if (stays.length == 0) {

            toast.add({ severity: 'warn', detail: "Please select active reservation stay to check out", life: 3000 })
            return
        }
        else if (rs.selecteds.some(r => r.reservation_status !== 'In-house')) {
            toast.add({ severity: 'warn', detail: "Reservation has not been checked in yet", life: 3000 });
            return;
        }
        rs.loading = true
        confirm.require({
            message: `Are you sure you want to${is_not_undo ? ' undo ' : ' '}check out reservations?`,
            header: 'Group Check Out',
            icon: 'pi pi-info-circle',
            acceptClass: 'border-none crfm-dialog',
            rejectClass: 'hidden',
            acceptIcon: 'pi pi-check-circle',
            acceptLabel: 'Ok',
            accept: () => {

                postApi("reservation.check_out", {
                    reservation: rs.reservation.name,
                    reservation_stays: stays,
                    is_undo: !is_not_undo
                }).then((result) => {
                    if (result) {
                        rs.loading = false
                        window.socket.emit("Frontdesk", window.property_name);
                        window.socket.emit("Dashboard", window.property_name);
                        window.socket.emit("ReservationList", { property: window.property_name })
                        window.socket.emit("ReservationStayList", { property: window.property_name })
                        window.socket.emit("ComGuestLedger", { property: window.property_name })
                        window.socket.emit("Reports", window.property_name)
                        window.socket.emit("ReservationStayDetail", { reservation_stay: window.reservation_stay })
                        window.socket.emit("FolioTransactionList", window.property_name)

                        // rs.LoadReservation()
                    }
                }).catch((error) => {
                    rs.loading = false
                })

            }
        });
    }
}

function onGroupUndoCheckOut() {
    const isSelect = validateSelectReservation()
    if (isSelect) {
        const stays = rs.selecteds.filter(r => r.is_active_reservation == 1 && r.allow_user_to_edit_information == 0).map((r) => r.name)
        if (stays.length == 0) {
            toast.add({ severity: 'warn', detail: "Please select check out reservation to performance undo check out", life: 3000 })
            return
        } else if (rs.selecteds.some(r => r.reservation_status === 'In-house')) {
            toast.add({ severity: 'warn', detail: "Reservation has not been checked out yet", life: 3000 });
            return;
        }
        const dialogRef = dialog.open(ComDialogNote, {
            data: {
                api_url: "reservation.undo_check_out",
                method: "POST",
                confirm_message: "Are you sure you want to undo check out this reservation?",
                data: {
                    property: rs.reservation.property,
                    reservation_stays: stays
                }
            },
            props: {
                header: "Undo Checked Out",
                style: {
                    width: '50vw',
                },
                modal: true,
                maximizable: true,
                closeOnEscape: false,
                position: "top"
            },
            onClose: (options) => {
                const data = options.data
                if (options.data) {
                    rs.reservationStay = data.data.message
                    window.socket.emit("Frontdesk", window.property_name);
                    window.socket.emit("Dashboard", window.property_name);
                    window.socket.emit("ReservationList", { property: window.property_name })
                    window.socket.emit("ReservationStayList", { property: window.property_name })
                    window.socket.emit("ComGuestLedger", { property: window.property_name })
                    window.socket.emit("Reports", window.property_name)
                    window.socket.emit("ReservationStayDetail", { reservation_stay: window.reservation_stay })
                    window.socket.emit("FolioTransactionList", window.property_name)

                    rs.LoadReservation()
                }

            }

        });
    }
}

function onGroupAssignRoom() {
    const dialogRef = dialog.open(ComGroupAssignRoom, {
        data: {
            reservation: rs.reservation
        },
        props: {
            header: 'Group Assign Room - ' + rs.reservation.name,
            contentClass: 'ex-pedd',
            style: {
                width: '80vw',
            },
            position: "top",
            modal: true,
            maximizable: true,
            closeOnEscape: false
        }
    });
}

function onMarkAsPaidbyMasterroom() {
    if (rs.selecteds.filter((r) => r.is_master == 0 && r.is_active_reservation == 1).length == 0) {
        if (rs.reservationStays.length >= 1) {
            toast.add({ severity: 'warn', summary: " Mark As Paid by Master room", detail: "Please select reservation stay for Mark As Paid by Master room.", life: 3000 })
            return
        } else {
            rs.selecteds = rs.reservationStays
        }
    }
    confirm.require({
        message: 'Are you sure you want to Mark As Paid by Master room?',
        header: 'Confirmation',
        icon: 'pi pi-exclamation-triangle',
        acceptClass: 'border-none crfm-dialog',
        rejectClass: 'hidden',
        acceptIcon: 'pi pi-check-circle',
        acceptLabel: 'Ok',
        accept: () => {
            postApi("reservation.update_mark_as_paid_by_master_room", {
                stays: rs.selecteds.map(x => x.name),
                paid_by_master_room: 1
            }).then((result) => {
                if (result) {
                    rs.LoadReservation()
                    window.socket.emit("ReservationStayDetail", { reservation_stay: window.reservation_stay })
                }
            })
                .catch((err) => {
                    submitLoading.value = false
                })
        },

    });

}

function onUnMarkAsPaidbyMasterroom() {
    if (rs.selecteds.filter((r) => r.is_master == 0 && r.is_active_reservation == 1).length == 0) {
        if (rs.reservationStays.length >= 1) {
            toast.add({ severity: 'warn', summary: " Unmark As Paid by Master room", detail: "Please select reservation stay for Unmark As Paid by Master room.", life: 3000 })
            return
        } else {
            rs.selecteds = rs.reservationStays
        }
    }
    confirm.require({
        message: 'Are you sure you want to Unmark As Paid by Master room?',
        header: 'Confirmation',
        icon: 'pi pi-exclamation-triangle',
        acceptClass: 'border-none crfm-dialog',
        rejectClass: 'hidden',
        acceptIcon: 'pi pi-check-circle',
        acceptLabel: 'Ok',
        accept: () => {
            postApi("reservation.update_mark_as_paid_by_master_room", {
                stays: rs.selecteds.map(x => x.name),
                paid_by_master_room: 0
            }).then((result) => {
                if (result) {
                    rs.LoadReservation()
                    window.socket.emit("ReservationStayDetail", { reservation_stay: window.reservation_stay })
                }
            })
                .catch((err) => {
                    submitLoading.value = false
                })
        },

    });

}

function onAllowPostToCityLedger() {
    if (rs.selecteds.length == 0) {
        toast.add({ severity: 'warn', summary: "", detail: "Please select reservation stay.", life: 3000 })
        return
    }


    confirm.require({
        message: 'Are you sure you want to allow post to city ledger?',
        header: 'Confirmation',
        icon: 'pi pi-exclamation-triangle',
        acceptClass: 'border-none crfm-dialog',
        rejectClass: 'hidden',
        acceptIcon: 'pi pi-check-circle',
        acceptLabel: 'Ok',
        accept: () => {
            postApi("reservation.update_allow_post_to_city_ledger", {
                stays: rs.selecteds.map(x => x.name),
                allow_post_to_city_ledger: 1
            }, "").then((result) => {
                rs.LoadReservation()
                window.socket.emit("ReservationStayDetail", { reservation_stay: window.reservation_stay })
            })
                .catch((err) => {
                    submitLoading.value = false
                })
        },

    });
}

function onUnAllowPostToCityLedger() {
    if (rs.selecteds.length == 0) {
        toast.add({ severity: 'warn', summary: "", detail: "Please select reservation stay.", life: 3000 })
        return
    }

    confirm.require({
        message: 'Are you sure you want to un allow post to city ledger?',
        header: 'Confirmation',
        icon: 'pi pi-exclamation-triangle',
        acceptClass: 'border-none crfm-dialog',
        rejectClass: 'hidden',
        acceptIcon: 'pi pi-check-circle',
        acceptLabel: 'Ok',
        accept: () => {
            postApi("reservation.update_allow_post_to_city_ledger", {
                stays: rs.selecteds.map(x => x.name),
                allow_post_to_city_ledger: 0
            }, "").then((result) => {
                rs.LoadReservation()
                window.socket.emit("ReservationStayDetail", { reservation_stay: window.reservation_stay })
            })
                .catch((err) => {
                    submitLoading.value = false
                })
        },

    });
}

function onAuditTrail() {
    const dialogRef = dialog.open(ComAuditTrail, {
        data: {
            doctype: 'Reservation',
            docname: rs.reservation.name,
            referenceTypes: [
                { doctype: 'Reservation', label: 'Reservation' },
                { doctype: 'Reservation Stay', label: 'Reservation stay' },
                { doctype: 'Reservation Room Rate', label: 'Room Rate' },
                { doctype: 'Customer', label: 'Guest' },
                { doctype: 'Reservation Folio', label: 'Reservation Folio' },
                { doctype: 'Folio Transaction', label: 'Folio Transaction' },

            ],
            filter_key: "custom_reservation"

        },
        props: {
            header: 'Audit Trail',
            style: {
                width: '80vw',
            },
            modal: true,
            maximizable: true,
            closeOnEscape: false,
            position: "top"
        },
        onClose: (options) => {
            //
        }
    });
}

function onGroupChangeRate() {
    if (rs.selecteds.filter((r) => r.is_active_reservation == 1 && r.allow_user_to_edit_information == 1).length > 0) {
        const dialogRef = dialog.open(ComGroupChangeRate, {
            data: { stays: rs.selecteds, reservation: rs.reservation.name },
            props: {
                header: 'Group Change Rate',
                style: {
                    width: '50vw',
                },
                breakpoints: {
                    '960px': '100vw',
                    '640px': '100vw'
                },
                modal: true,
                maximizable: true,
                closeOnEscape: false,
                position: "top"
            },
            onClose: (options) => {
                if (options.data) {
                    rs.LoadReservation(rs.reservation.name, true)

                }
            }
        });
    } else {
        toast.add({
            severity: 'warn', summary: 'Group Change Rate',
            detail: 'Please select reservation stay for group Change Rate', life: 3000
        });
    }
}

function onGroupChangeStayDate() {
    if (rs.selecteds.filter((r) => r.is_active_reservation == 1 && r.allow_user_to_edit_information == 1).length == 0) {
        if (rs.reservationStays.length > 1) {
            toast.add({ severity: 'warn', summary: "Group Change Stay", detail: "Please select reservation stay for group Change stay date.", life: 3000 })
            return
        } else {
            rs.selecteds = rs.reservationStays
        }
    }
    const dialogRef = dialog.open(ComGroupChangeStayDate, {
        data: rs.selecteds.map(obj => {
            return {
                name: obj.name,
                arrival_date: obj.arrival_date,
                departure_date: obj.departure_date
            };
        }),
        props: {
            header: 'Group Change Stay Date',
            style: {
                width: '60vw',
            },
            breakpoints: {
                '960px': '100vw',
                '640px': '100vw'
            },
            modal: true,
            maximizable: true,
            closeOnEscape: false,
            position: "top"
        },
        onClose: (options) => {

        }
    })
}

function onMarkasGITReservation() {
    confirm.require({
        message: 'Are you sure you want to Mark as GIT Reservation',
        header: 'Confirmation',
        icon: 'pi pi-exclamation-triangle',
        acceptClass: 'border-none crfm-dialog',
        rejectClass: 'hidden',
        acceptIcon: 'pi pi-check-circle',
        acceptLabel: 'Ok',
        accept: () => {
            db.updateDoc('Reservation', rs.reservation?.name, {
                reservation_type: "GIT",
            })
                .then((doc) => {
                    rs.reservation.reservation_type = doc.reservation_type,
                        toast.add({
                            severity: 'success', summary: 'Mark as GIT Reservation',
                            detail: 'Mark as GIT Reservation Successfully', life: 3000
                        });
                    // window.socket.emit("RefreshData", { property: rs.reservation.property, action: "refresh_res_list" })
                    window.socket.emit("ReservationList", { property: window.property_name })
                    window.socket.emit("ReservationStayList", { property: window.property_name })
                    window.socket.emit("Dashboard", window.property_name)
                    window.socket.emit("Reports", window.property_name)
                    window.socket.emit("ReservationDetail", window.reservation)
                    window.socket.emit("ReservationStayDetail", { reservation_stay: window.reservation_stay })

                })
        },

    });

}
function onMarkasFITReservation() {
    confirm.require({
        message: 'Are you sure you want to Mark as FIT Reservation',
        header: 'Confirmation',
        icon: 'pi pi-exclamation-triangle',
        acceptClass: 'border-none crfm-dialog',
        rejectClass: 'hidden',
        acceptIcon: 'pi pi-check-circle',
        acceptLabel: 'Ok',
        accept: () => {
            ``
            db.updateDoc('Reservation', rs.reservation?.name, {
                reservation_type: "FIT",
            })
                .then((doc) => {
                    rs.reservation.reservation_type = doc.reservation_type,
                        toast.add({
                            severity: 'success', summary: 'Mark as FIT Reservation',
                            detail: 'Mark as FIT Reservation Successfully', life: 3000
                        });
                    window.socket.emit("ReservationList", { property: window.property_name })
                    window.socket.emit("ReservationStayList", { property: window.property_name })
                    window.socket.emit("Dashboard", window.property_name)
                    window.socket.emit("Reports", window.property_name)
                    window.socket.emit("ReservationDetail", window.reservation)
                    window.socket.emit("ReservationStayDetail", { reservation_stay: window.reservation_stay })

                })
        },

    });
}

function onPickDrop() {
    if (rs.selecteds.filter((r) => r.is_active_reservation == 1 && r.allow_user_to_edit_information == 1).length > 0) {

        dialog.open(ComFormSetupArrivalAndDeparture, {
            data: {
                stays: rs.selecteds.filter((r) => r.is_active_reservation == 1 && r.allow_user_to_edit_information == 1).map(x => x.name)
            },
            props: {
                header: 'Setup Arrival & Departure Mode',
                style: {
                    width: '60vw',
                },
                modal: true,
                closeOnEscape: false,
                position: 'top'
            },
            onClose: (options) => {

                if (options.data) {
                    rs.selecteds = []
                }
            }
        });
    } else {
        gv.toast('warn', 'Please select reservation stay for Pickup and Drop Off.')
        return false
    }
}

function onTransferStay() {
    const stays = rs.selecteds.filter(r => r.is_active_reservation == 1 && r.allow_user_to_edit_information == 1)

    if (stays.length == 0) {
        toast.add({ severity: 'warn', summary: "", detail: "Please select active reservation stay to transfer to other reservation.", life: 3000 })
        return
    }

    const dialogRef = dialog.open(ComConfirmTransferStay, {
        data: {
            source_reservation: rs.reservation.name,
            stays: stays.map(r => r.name),
            keep_rate: 1
        },
        props: {
            header: "Transfer Stay",
            style: {
                width: '50vw',
            },
            modal: true,
            maximizable: true,
            closeOnEscape: true,
            position: "top"
        },
        onClose: (options) => {
            const data = options.data;
            if (data) {
                rs.LoadReservation();
            }
        }

    });


}

</script>