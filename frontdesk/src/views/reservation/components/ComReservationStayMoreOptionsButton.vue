<template>
    <div>
          <Button class="border-none" icon="pi pi-chevron-down" iconPos="right" type="button" label="Mores" @click="toggle"
            aria-haspopup="true" aria-controls="folio_menu" />
        <Menu ref="folio_menu" id="folio_menu" :popup="true">
            <template #end>
                <button @click="onMarkAsMasterRoom()"
                    v-if="rs.reservationStay.is_master == 0 && (rs.reservationStay.reservation_status == 'Reserved' || rs.reservationStay.reservation_status == 'In-house')"
                    class="w-full p-link flex align-items-center py-2 px-3 text-color hover:surface-200 border-noround">
                    <ComIcon icon="iconCrownBlack" style="height: 12px;" />
                    <span class="ml-2">Mark as Master Room </span>
                </button>
                <button @click="onUndoCheckIn()"
                    v-if="rs.reservationStay.reservation_status == 'In-house' && rs.reservationStay?.arrival_date == working_day?.date_working_day"
                    class="w-full p-link flex align-items-center py-2 px-3 text-color hover:surface-200 border-noround">
                    <i class="pi pi-undo" />
                    <span class="ml-2">Undo Check-In</span>
                </button>
                <button @click="OnUndoCheckOut()"
                    v-if="canUndoCheckOut"
                    class="w-full p-link flex align-items-center py-2 px-3 text-color hover:surface-200 border-noround">
                    <i class="pi pi-undo" />
                    <span class="ml-2">Undo Check Out</span>
                </button>
                
                <button @click="onNoShowReservationStay()"
                    v-if="(rs.reservationStay?.reservation_status=='Confirmed' || rs.reservationStay?.reservation_status=='Reserved') && rs.reservationStay?.arrival_date == working_day?.date_working_day"
                    class="w-full p-link flex align-items-center py-2 px-3 text-color hover:surface-200 border-noround">
                    <i class="pi pi-eye-slash" />
                    <span class="ml-2">No Show</span>
                </button>
              
                <button @click="onReservedRoom()"
                    v-if="rs.reservationStay?.reservation_status=='No Show' && 
                            moment(rs.reservationStay?.departure_date).toDate()> moment(working_day?.date_working_day).toDate() &&
                            rs.reservationStay?.stays?.filter(r => r.show_in_room_chart == 1).length == 0
                            "
                    class="w-full p-link flex align-items-center py-2 px-3 text-color hover:surface-200 border-noround">
                    <i class="pi pi-calendar-plus" />
                    <span class="ml-2">Reserve Room</span>
                </button>
                <button @click="onUnReservedRoom()"
                v-if="rs.reservationStay?.reservation_status=='No Show' && 
                        moment(rs.reservationStay?.departure_date).toDate()> moment(working_day?.date_working_day).toDate() &&
                        rs.reservationStay?.stays?.filter(r => r.show_in_room_chart == 1).length > 0
                        "
                    class="w-full p-link flex align-items-center py-2 px-3 text-color hover:surface-200 border-noround">
                    <i class="pi pi-calendar-times" />
                    <span class="ml-2">Unreserve Room</span>
                </button>
                
                <button @click="onCancelReservationStay()"
                    v-if="rs.reservationStay?.reservation_status=='Confirmed' || rs.reservationStay?.reservation_status=='Reserved'"
                    class="w-full p-link flex align-items-center py-2 px-3 text-color hover:surface-200 border-noround">
                    <i class="pi pi-user-minus" />
                    <span class="ml-2">Cancel Reservation Stay</span>
                </button>
                <button @click="onVoidReservationStay()"
                    v-if="rs.reservationStay?.reservation_status=='Confirmed' || rs.reservationStay?.reservation_status=='Reserved'"
                    class="w-full p-link flex align-items-center py-2 px-3 text-color hover:surface-200 border-noround">
                    <i class="pi pi-file-excel" />
                    <span class="ml-2">Void Reservation Stay </span>
                </button>
                    <button v-if="rs.reservationStay.paid_by_master_room && !rs.reservationStay.is_master" @click="onUnmarkasPaidbyMasterRoom()"
                        class="w-full p-link flex align-items-center py-2 px-3 text-color hover:surface-200 border-noround">
                        <ComIcon  icon="BilltoMasterRoom"  style="height:15px;" ></ComIcon>
                        <span class="ml-2"> Unmark as Paid by Master Room </span>
                    </button>
                    <button @click="onMarkasPaidbyMasterRoom()" v-else-if="!rs.reservationStay.paid_by_master_room && !rs.reservationStay.is_master"
                        class="w-full p-link flex align-items-center py-2 px-3 text-color hover:surface-200 border-noround">
                        <ComIcon  icon="BilltoMasterRoom"  style="height:15px;" ></ComIcon>
                        <span class="ml-2">  Mark as Paid by Master Room </span>
                    </button>
                    <div>
                    <button v-if="rs.reservationStay.allow_post_to_city_ledger" @click="onDisallowPosttoCityLedger()"
                    class="w-full p-link flex align-items-center py-2 px-3 text-color hover:surface-200 border-noround">
                    <ComIcon  icon="IconBillToCompany" class="me-2" style="height:15px;" ></ComIcon>
                    <span> Disallow Post to City Ledger </span>
                    </button>
                    <button v-else @click="onAllowPosttoCityLedger()"
                    class="w-full p-link flex align-items-center py-2 px-3 text-color hover:surface-200 border-noround">
                    <ComIcon  icon="IconBillToCompany" class="me-2" style="height:15px;" ></ComIcon>
                    <span> Allow Post to City Ledger </span>
                    </button>
                    </div>
                <button v-if="rs.reservationStay.reservation_type == 'FIT'" @click="onMarkasGITReservation()"
                    class="w-full p-link flex align-items-center py-2 px-3 text-color hover:surface-200 border-noround">                   
                    <ComIcon icon="userGif" style="height: 15px;" />
                    <span class="ml-2">Mark as GIT Reservation</span>
                </button>

                <button v-else @click="onMarkasFITReservation()"
                    class="w-full p-link flex align-items-center py-2 px-3 text-color hover:surface-200 border-noround">
                    
                    <ComIcon  icon="userProfile"  style="height:15px;" ></ComIcon>
                    <span class="ml-2">Mark as FIT Reservation </span>
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
import { inject, ref, useConfirm, useToast, postApi,useDialog,computed } from "@/plugin";
import ComDialogNote from "@/components/form/ComDialogNote.vue";


const dialog = useDialog();

const moment = inject("$moment")
const confirm = useConfirm()
const toast = useToast();
const emit = defineEmits(['onAuditTrail', "onRefresh"])
const items = ref([])
const folio_menu = ref();
const rs = inject("$reservation_stay")
const working_day = ref(JSON.parse(localStorage.getItem("edoor_working_day")))
const frappe = inject('$frappe');
const db = frappe.db();
const loading = ref(false)


const toggle = (event) => {
    folio_menu.value.toggle(event);
}
 
const canUndoCheckOut = computed(()=>{
    
if (parseInt(window.setting.allow_user_to_add_back_date_transaction)==1){
    return rs.reservationStay.reservation_status == 'Checked Out' 
}else {
    return rs.reservationStay.reservation_status == 'Checked Out' && rs.reservationStay?.departure_date >= working_day.value?.date_working_day 
}
    
})

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
                rs.loading = false
                rs.reservationStay = doc.message
                window.socket.emit("ReservationStayList", { property:window.property_name})
                window.socket.emit("ReservationStayDetail", {reservation_stay:window.reservation_stay})
                window.socket.emit("ReservationDetail", rs.reservationStay.reservation)
                window.socket.emit("Frontdesk", window.property_name)
                window.socket.emit("ComGuestLedger", { property:window.property_name})

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
                reservation_stay: rs.reservationStay.name,
                reservation: rs.reservationStay.reservation,
                property:window.property.name
            },
                "Undo check in successfully"
            ).then((doc) => {
                rs.loading = false
                rs.reservationStay = doc.message
                window.socket.emit("ComHousekeepingStatus", window.property_name)
                window.socket.emit("Dashboard", window.property_name)
                window.socket.emit("ReservationList", { property:window.property_name})
                window.socket.emit("ReservationStayList", { property:window.property_name})
                window.socket.emit("ReservationStayDetail", {reservation_stay:window.reservation_stay})
                window.socket.emit("ReservationDetail", rs.reservationStay.reservation)
                window.socket.emit("Frontdesk", window.property_name)
                window.socket.emit("TodaySummary", window.property_name)
                window.socket.emit("ComGuestLedger", { property:window.property_name})
                window.socket.emit("Reports", window.property_name)
                window.socket.emit("Housekeeping", {property:window.property_name})

                setTimeout(() => {
                    emit('onRefresh')
                }, 1000);


            }).catch((err) => {
                rs.loading = false
            })

        },

    });
}

function OnUndoCheckOut() {
    confirm.require({
        message: 'Are you sure you want to undo check out this reservation?',
        header: 'Confirmation',
        icon: 'pi pi-exclamation-triangle',
        acceptClass: 'border-none crfm-dialog',
        rejectClass: 'hidden',
        acceptIcon: 'pi pi-check-circle',
        acceptLabel: 'Ok',
        accept: () => {
            rs.loading = true
            postApi("reservation.undo_check_out", {
                property: rs.reservationStay.property,
                reservation_stays:[rs.reservationStay.name] 
            }
            ).then((doc) => {
                rs.reservationStay = doc.message
                window.socket.emit("ComHousekeepingStatus", window.property_name)
                window.socket.emit("Dashboard", window.property_name)
                window.socket.emit("ReservationList", { property:window.property_name})
                window.socket.emit("ReservationStayList", { property:window.property_name})
                window.socket.emit("ReservationStayDetail", {reservation_stay:window.reservation_stay})
                window.socket.emit("ReservationDetail", rs.reservationStay.reservation)
                window.socket.emit("Frontdesk", window.property_name)
                window.socket.emit("ComGuestLedger", { property:window.property_name})
                window.socket.emit("Reports", window.property_name)
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

function onCancelReservationStay() {
    onUpdateReservationStatus(
        "Cancel Reservation Stay # " + rs.reservationStay.name,
        {
            api_url: "reservation.update_reservation_status",
            method: "POST",
            confirm_message: "You are about to cancel this reservation.<br/> Once the cancellation is complete, you will no longer be able to make any changes to the reservation. <br/> If you have a cancellation charge, please update the folio transaction first.",
            data: {
                reservation: rs.reservationStay.reservation,
                reserved_room: false,
                status: "Cancelled",
                show_reserved_room:false,
                stays: [{
                    name: rs.reservationStay.name,
                    reservation_status: rs.reservationStay.reservation_status
                }]
            }
        }
    )


}


function onUpdateReservationStatus(header="Confirm Note",data){
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
                rs.getReservationDetail(rs.reservationStay.name)
             }
         }

    });

}


function onVoidReservationStay() {
    onUpdateReservationStatus(
        "Void Reservation Stay # " + rs.reservationStay.name,
        {
            api_url: "reservation.update_reservation_status",
            method: "POST",
            confirm_message: "You are about to void this reservation.<br/> Once the void is complete, you will no longer be able to make any changes to the reservation.",
            data: {
                reservation: rs.reservationStay.reservation,
                reserved_room: false,
                show_reserved_room:false,
                status: "Void",
                stays: [{
                    name: rs.reservationStay.name,
                    reservation_status: rs.reservationStay.reservation_status
                }]
            }
        }
    )

 
}

function onNoShowReservationStay() {
    onUpdateReservationStatus(
        "No Show Reservation Stay # " + rs.reservationStay.name,
        {
            api_url: "reservation.update_reservation_status",
            method: "POST",
            confirm_message:"You are about to mark this reservation as No Show.<br/> If you have a No Show charge, please update the folio transaction first. <br/> If you want to sell this room, please untick on check box <strong>Reserved room for this reservation</strong>",
            data: {
                reservation: rs.reservationStay.reservation,
                reserved_room: true,
                show_reserved_room:true,
                status: "No Show",
                stays: [{
                    name: rs.reservationStay.name,
                    reservation_status: rs.reservationStay.reservation_status
                }]
            }
        }
    )

 
}

 
 
function onReservedRoom() {
 
    confirm.require({
        message: 'Are you sure you want to reserve room for this reservation?',
        header: 'Confirmation',
        icon: 'pi pi-exclamation-triangle',
        acceptClass: 'border-none crfm-dialog',
        rejectClass: 'hidden',
        acceptIcon: 'pi pi-check-circle',
        acceptLabel: 'Ok',
        accept: () => {
            postApi("reservation.reserved_room",{
                property: rs.reservation.property,
                reservation_stay: rs.reservationStay.name
            }).then((resul)=>{
                loading.value = false
                rs.getReservationDetail(rs.reservationStay.name);
                window.socket.emit("ReservationList", { property:window.property_name})
                window.socket.emit("ReservationStayList", { property:window.property_name})
                window.socket.emit("ReservationStayDetail", {reservation_stay:window.reservation_stay})
                window.socket.emit("Frontdesk", window.property_name)
                window.socket.emit("ComGuestLedger", { property:window.property_name})
                window.socket.emit("Reports", window.property_name)
                

            })  
        },

    });

}

function onUnReservedRoom() {
 
    confirm.require({
        message: 'Are you sure you want to unreserve room for this reservation?',
        header: 'Confirmation',
        icon: 'pi pi-exclamation-triangle',
        acceptClass: 'border-none crfm-dialog',
        rejectClass: 'hidden',
        acceptIcon: 'pi pi-check-circle',
        acceptLabel: 'Ok',
        accept: () => {
            postApi("reservation.unreserved_room",{
                property: rs.reservation.property,
                reservation_stay: rs.reservationStay.name
            }).then((resul)=>{
                loading.value = false
                window.socket.emit("ReservationList", { property:window.property_name})
                window.socket.emit("ReservationStayList", { property:window.property_name})
                window.socket.emit("ReservationStayDetail", {reservation_stay:window.reservation_stay})
                window.socket.emit("Frontdesk", window.property_name)
                window.socket.emit("ComGuestLedger", { property:window.property_name})
                window.socket.emit("Reports", window.property_name)
            
            })  
        },

    });

}

function onMarkasPaidbyMasterRoom() {
    if(rs.reservationStay.is_active_reservation){
        confirm.require({
            message: 'Are you sure you want to Mark as Piad by Master Room?',
            header: 'Confirmation',
            icon: 'pi pi-exclamation-triangle',
            acceptClass: 'border-none crfm-dialog',
            rejectClass: 'hidden',
            acceptIcon: 'pi pi-check-circle',
            acceptLabel: 'Ok',
            accept: () => {
                db.updateDoc('Reservation Stay', rs.reservationStay.name, {
                    paid_by_master_room: 1,
                })
                    .then((doc) => {
                        rs.loading = false
                        rs.reservationStay.paid_by_master_room = doc.paid_by_master_room;
                        toast.add({
                            severity: 'success', summary: 'Mark as Piad by Master Room',
                            detail: 'Mark as Piad by Master Room Successfully', life: 3000
                        });
                        window.socket.emit("RefreshReservationDetail", rs.reservation.name)
                        window.socket.emit("ReservationStayList", { property:window.property_name})
                        window.socket.emit("ReservationStayDetail", {reservation_stay:window.reservation_stay})
                        window.socket.emit("ReservationDetail", rs.reservationStay.reservation)

                    })

            },

        });
    }else{
        toast.add({
                severity: 'warn', summary: 'Mark as Paid by Master Room',
                detail: `${rs.reservationStay.reservation_status} reservation can not change information`, life: 3000
            });
    }
}
function onUnmarkasPaidbyMasterRoom() {
    if(rs.reservationStay.is_active_reservation){
        confirm.require({
        message: 'Are you sure you want to Unmark as Paid by Master Room?',
        header: 'Confirmation',
        icon: 'pi pi-exclamation-triangle',
        acceptClass: 'border-none crfm-dialog',
        rejectClass: 'hidden',
        acceptIcon: 'pi pi-check-circle',
        acceptLabel: 'Ok',
        accept: () => {
            db.updateDoc('Reservation Stay', rs.reservationStay.name, {
                paid_by_master_room: 0,
            })
                .then((doc) => {
                    loading.value = false;
                    rs.reservationStay.paid_by_master_room = doc.paid_by_master_room;
                    toast.add({
                        severity: 'success', summary: 'Unmark as Paid by Master Room ',
                        detail: 'Unmark as Paid by Master Room Successfully', life: 3000
                    });
                    window.socket.emit("RefreshReservationDetail", rs.reservation.name)
                    window.socket.emit("ReservationStayList", { property:window.property_name})
                    window.socket.emit("ReservationStayDetail", {reservation_stay:window.reservation_stay})
                    window.socket.emit("ReservationDetail", rs.reservationStay.reservation)

                })
        },

    });
    }
    else{
        toast.add({
                severity: 'warn', summary: 'Unmark as Paid by Master Room',
                detail: `${rs.reservationStay.reservation_status} reservation can not change information`, life: 3000
            });
    }

}
function onDisallowPosttoCityLedger(){
    if(rs.reservationStay.is_active_reservation){
        confirm.require({
            message: 'Are you sure you want to Disallow Post to City Ledger?',
            header: 'Confirmation',
            icon: 'pi pi-exclamation-triangle',
            acceptClass: 'border-none crfm-dialog',
            rejectClass: 'hidden',
            acceptIcon: 'pi pi-check-circle',
            acceptLabel: 'Ok',
            accept: () => {
                db.updateDoc('Reservation Stay', rs.reservationStay.name, {
                    allow_post_to_city_ledger: 0,
                })
                    .then((doc) => {
                        rs.reservationStay.allow_post_to_city_ledger = doc.allow_post_to_city_ledger;
                        toast.add({
                            severity: 'success', summary: 'Disallow Post to City Ledger',
                            detail: 'Disallow Post to City Ledger Successfully', life: 3000
                        });

                        window.socket.emit("ReservationStayDetail", {reservation_stay:window.reservation_stay})
                        window.socket.emit("ReservationDetail", rs.reservationStay.reservation)
                    })
            },

        });
    }else{
        toast.add({
            severity: 'warn', summary: 'Disallow Post to City Ledger',
            detail: `${rs.reservationStay.reservation_status} reservation is not Disallow to change information`, life: 3000
        });
    }
}
function onAllowPosttoCityLedger(){
    if(rs.reservationStay.is_active_reservation){
        confirm.require({
        message: 'Are you sure you want to Allow Post to City Ledger?',
        header: 'Confirmation',
        icon: 'pi pi-exclamation-triangle',
        acceptClass: 'border-none crfm-dialog',
        rejectClass: 'hidden',
        acceptIcon: 'pi pi-check-circle',
        acceptLabel: 'Ok',
        accept: () => {
            db.updateDoc('Reservation Stay', rs.reservationStay.name, {
                allow_post_to_city_ledger: 1,
            })
                .then((doc) => {
                    rs.reservationStay.allow_post_to_city_ledger = doc.allow_post_to_city_ledger;
                    toast.add({
                        severity: 'success', summary: 'Allow Post to City Ledger',
                        detail: 'Allow Post to City Ledger Successfully', life: 3000
                    });

                    window.socket.emit("ReservationStayDetail", {reservation_stay:window.reservation_stay})
                    window.socket.emit("ReservationDetail", rs.reservationStay.reservation)
                })
        },

    });
    }else{
        toast.add({
            severity: 'warn', summary: 'Allow Post to City Ledger',
            detail: `${rs.reservationStay.reservation_status} reservation is not allow to change information`, life: 3000
        });
    }
    
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
                    rs.reservationStay.reservation_type = doc.reservation_type,
                        toast.add({
                            severity: 'success', summary: 'Mark as GIT Reservation',
                            detail: 'Mark as GIT Reservation Successfully', life: 3000
                        });
                        window.socket.emit("ReservationList", { property:window.property_name})
                        window.socket.emit("ReservationStayList", { property:window.property_name})
                        window.socket.emit("Dashboard",window.property_name)

                        window.socket.emit("ReservationStayDetail", {reservation_stay:window.reservation_stay})
                        window.socket.emit("ReservationDetail", rs.reservationStay.reservation)
                        window.socket.emit("Frontdesk", window.property_name)
                        window.socket.emit("Reports", window.property_name)
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
            db.updateDoc('Reservation', rs.reservation?.name, {
                reservation_type: "FIT",
            })
                .then((doc) => {
                    rs.reservationStay.reservation_type = doc.reservation_type,
                        toast.add({
                            severity: 'success', summary: 'Mark as FIT Reservation',
                            detail: 'Mark as FIT Reservation Successfully', life: 3000
                        });
                        window.socket.emit("Dashboard", rs.reservationStay.property);
                        window.socket.emit("ReservationList", { property:window.property_name})
                        window.socket.emit("ReservationStayList", { property:window.property_name})
                        window.socket.emit("Dashboard",window.property_name)

                        window.socket.emit("ReservationStayDetail", {reservation_stay:window.reservation_stay})
                        window.socket.emit("ReservationDetail", rs.reservationStay.reservation)
                        window.socket.emit("Frontdesk", window.property_name)
                        window.socket.emit("Reports", window.property_name)

                })
        },

    });
}

function onAuditTrail() {
    emit('onAuditTrail')
}
 
</script>