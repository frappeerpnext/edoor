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
                    <ComIcon icon="checkoutBlack" style="height: 12px;" />
                    <span class="ml-2">Group Check Out</span>
                </button>
                <button @click="onGroupCheckOut(false)"
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
                <button class="w-full p-link flex align-items-center py-2 px-3 text-color hover:surface-200 border-noround">
                    <ComIcon icon="iconGeneralList" style="height: 14px;" />
                    <span class="ml-2">Stay to Other Reservation</span>
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
// function onMarkAsReservationType() {
//     confirm.require({
//         message: `Are you sure you want to mark as ${rs.reservation.reservation_type == 'FIT' ? 'GIT' : 'FIT'} reservation?`,
//         header: 'Confirmation',
//         icon: 'pi pi-exclamation-triangle',
//         acceptClass: 'border-none crfm-dialog',
//         rejectClass: 'hidden',
//         acceptIcon: 'pi pi-check-circle',
//         acceptLabel: 'Ok',
//         accept: () => {
//             db.updateDoc('Reservation', rs.reservation?.name, {
//                 reservation_type: rs.reservation.reservation_type == 'GIT' ? 'FIT' : 'GIT',
//             })
//                 .then((doc) => {
//                     rs.reservation.reservation_type = doc.reservation_type
//                     window.socket.emit("ReservationDetail", reservation.value.name);

//                     toast.add({
//                         severity: 'success', summary: `Mark as ${rs.reservation.reservation_type} reservation`,
//                         detail: `Mark as ${rs.reservation.reservation_type} Reservation Successfully`, life: 3000
//                     });
//                 })
//         },

//     });
// }
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
                    stays: rs.selecteds
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


            if (data) {
                setTimeout(function () {
                    rs.LoadReservation(rs.reservation.name)
                }, 1500)


            }
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
    if (rs.selecteds.length == 0) {
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
                    window.socket.emit("ReservationDetail", rs.reservation.name);
                    window.socket.emit("Dashboard", property.name);
                    window.socket.emit("ReservationList", { property:window.property_name})
                    window.socket.emit("ReservationStayList", { property:window.property_name})
                    window.socket.emit("ComGuestLedger", { property:window.property_name})
                    window.socket.emit("Reports", window.property_name)
                    console.log(rs.selecteds)
                    rs.selecteds.forEach(r => {
                        window.socket.emit("ReservationStayDetail", {reservation_stay:r.name})
                    });
                    
                })
                    .catch((err) => {
                        rs.loading = false
                    })
            }
        }
    })

}


function onGroupUndoCheckIn() {


    if (rs.selecteds.filter(r=>r.reservation_status=='In-house').length ==0) {
        toast.add({ severity: 'warn', summary: "Group Undo Check In", detail: "Please select  In-house reservation stay to undo check in.", life: 3000 })
        return
    } else {
        confirm.require({
            message: `Are you sure you want to undo check in these reservation stay?`,
            header: 'Undo Check In',
            icon: 'pi pi-info-circle',
            acceptClass: 'border-none crfm-dialog',
            rejectClass: 'hidden',
            acceptIcon: 'pi pi-check-circle',
            acceptLabel: 'Ok',
            accept: () => {
                rs.loading = true
                postApi("reservation.undo_check_in", {
                   reservation_stay:rs.selecteds.filter(r=>r.reservation_status=='In-house').map(d=>d.name),
                   reservation:rs.reservation.name,
                   property:window.property_name
                }).then((result) => {
                    if (result) {
                        //wait for equeue process finish
                        rs.LoadReservation()
                        window.socket.emit("ReservationList", { property:window.property_name})
                        window.socket.emit("ReservationStayList", { property:window.property_name})
                        window.socket.emit("ComGuestLedger", { property:window.property_name})
                        window.socket.emit("Reports", window.property_name)
                        window.socket.emit("ReservationDetail", window.reservation)
                        window.socket.emit("ReservationStayDetail", {reservation_stay:window.reservation_stay})
                    }
                }).catch(err=>{
                    rs.loading = false
                })

            }
        });
    }



}


function onGroupCheckOut(is_not_undo = false) {
    const isSelect = validateSelectReservation()
    if (isSelect) {
        confirm.require({
            message: `Are you sure you want to${is_not_undo ? ' undo ' : ' '}check out reservations?`,
            header: 'Check Out',
            icon: 'pi pi-info-circle',
            acceptClass: 'border-none crfm-dialog',
            rejectClass: 'hidden',
            acceptIcon: 'pi pi-check-circle',
            acceptLabel: 'Ok',
            accept: () => {
                const checkList = rs.selecteds.map((r) => r.name).join(',')
                postApi("reservation.check_out", {
                    reservation: rs.reservation.name,
                    reservation_stays: [checkList],
                    is_undo: !is_not_undo
                }).then((result) => {
                    if (result) {
                        window.socket.emit("ReservationList", { property:window.property_name})
                        window.socket.emit("ReservationStayList", { property:window.property_name})
                        window.socket.emit("ComGuestLedger", { property:window.property_name})
                        window.socket.emit("Reports", window.property_name)
                        window.socket.emit("ReservationDetail", window.reservation)
                        window.socket.emit("ReservationStayDetail", {reservation_stay:window.reservation_stay})
                        rs.LoadReservation()
                    }
                }).catch((error) => {
                    //
                })

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
                    window.socket.emit("ReservationDetail", window.reservation)
                    window.socket.emit("ReservationStayDetail", {reservation_stay:window.reservation_stay})
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
                    window.socket.emit("ReservationDetail", window.reservation)
                    window.socket.emit("ReservationStayDetail", {reservation_stay:window.reservation_stay})
                }
            })
                .catch((err) => {
                    submitLoading.value = false
                })
        },

    });

}

function onAllowPostToCityLedger() {
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
            }).then((result) => {
                window.socket.emit("ReservationDetail", window.reservation)
                window.socket.emit("ReservationStayDetail", {reservation_stay:window.reservation_stay})
            })
                .catch((err) => {
                    submitLoading.value = false
                })
        },

    });
}

function onUnAllowPostToCityLedger() {
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
            }).then((result) => {
                window.socket.emit("ReservationDetail", window.reservation)
                window.socket.emit("ReservationStayDetail", {reservation_stay:window.reservation_stay})
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
            docname: rs.reservation.name
        },
        props: {
            header: 'Audit Trail',
            style: {
                width: '75vw',
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
            //
        }
    });
}

function onGroupChangeRate() {
    if (rs.selecteds.filter((r) => r.is_active_reservation == 1 && r.allow_user_to_edit_information == 1).length > 0) {
        const dialogRef = dialog.open(ComGroupChangeRate, {
            data: rs.selecteds,
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
                //
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
                    window.socket.emit("ReservationList", { property:window.property_name})
                    window.socket.emit("ReservationStayList", { property:window.property_name})
                    window.socket.emit("Dashboard", window.property_name)
                    window.socket.emit("Reports", window.property_name)
                    window.socket.emit("ReservationDetail", window.reservation)
                    window.socket.emit("ReservationStayDetail", {reservation_stay:window.reservation_stay})

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
        accept: () => {``
            db.updateDoc('Reservation', rs.reservation?.name, {
                reservation_type: "FIT",
            })
                .then((doc) => {
                    rs.reservation.reservation_type = doc.reservation_type,
                        toast.add({
                            severity: 'success', summary: 'Mark as FIT Reservation',
                            detail: 'Mark as FIT Reservation Successfully', life: 3000
                        });
                    window.socket.emit("ReservationList", { property:window.property_name})
                    window.socket.emit("ReservationStayList", { property:window.property_name})
                    window.socket.emit("Dashboard", window.property_name)
                    window.socket.emit("Reports", window.property_name)
                    window.socket.emit("ReservationDetail", window.reservation)
                    window.socket.emit("ReservationStayDetail", {reservation_stay:window.reservation_stay})

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
                breakpoints: {
                    '960px': '75vw',
                    '640px': '90vw'
                },
                modal: true,
                closeOnEscape: false,
                position: 'top'
            },
            onClose: (options) => {
                console.log(options)
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

</script>