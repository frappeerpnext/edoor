<template>
    <div>
        <!-- <SplitButton class="border-split-none" label="Mores" icon="pi pi-list" :model="items" /> -->
        <Button class="border-none" icon="pi pi-chevron-down" iconPos="right" type="button" label="Mores" @click="toggle"
            aria-haspopup="true" aria-controls="menu" />
        <Menu ref="menu" id="menu" :popup="true">
            <template #end>
                
                <button @click="onGroupAssignRoom" 
                    class="w-full p-link flex align-items-center py-2 px-3 text-color hover:surface-200 border-noround">
                    <i class="pi pi-file-edit" />
                    <span class="ml-2">Group Assign Room</span>
                </button>
                
                <button @click="onChangeStatus('No Show')" 
                    class="w-full p-link flex align-items-center py-2 px-3 text-color hover:surface-200 border-noround">
                    <i class="pi pi-eye-slash" />
                    <span class="ml-2">Group No Show</span>
                </button>
                
                <button @click="onChangeStatus('Group Cancel')" 
                    class="w-full p-link flex align-items-center py-2 px-3 text-color hover:surface-200 border-noround">
                    <i class="pi pi-user-minus" />
                    <span class="ml-2">Group Cancel</span>
                </button>
                <button @click=" onChangeStatus('void')" 
                    class="w-full p-link flex align-items-center py-2 px-3 text-color hover:surface-200 border-noround">
                    <i class="pi pi-file-excel" />
                    <span class="ml-2">Group Void</span>
                </button>
                <button @click=" onGroupCheckIn(true)" 
                    class="w-full p-link flex align-items-center py-2 px-3 text-color hover:surface-200 border-noround">
                    <ComIcon icon="checkin-black" style="height: 14px;" />
                    <span class="ml-2">Group Check-In</span>
                </button>
                <button @click="onGroupCheckIn(false)" 
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

                <button @click="onGroupBuildToCompany" 
                    class="w-full p-link flex align-items-center py-2 px-3 text-color hover:surface-200 border-noround">
                    <ComIcon  icon="IconBillToCompany" style="height:15px;" ></ComIcon>
                    <span class="ml-2">Group Bill To Company</span>
                </button>
                
                <button @click="onGroupBuildToMasterGroup " 
                    class="w-full p-link flex align-items-center py-2 px-3 text-color hover:surface-200 border-noround">
                    <ComIcon  icon="BilltoMasterRoom" style="height:13px;" ></ComIcon>
                    <span class="ml-2">Group Bill To Master Group </span>
                </button>

                <button @click="onGroupBuildToGuest " 
                    class="w-full p-link flex align-items-center py-2 px-3 text-color hover:surface-200 border-noround">
                    <ComIcon  icon="IconBillToGuest" class="me-2" style="height:15px;" ></ComIcon>
                    <span class="ml-2">Group Bill To Guest</span>
                </button>
                <button @click="onGroupBuildToRoomandTaxtoCompany " 
                    class="w-full p-link flex align-items-center py-2 px-3 text-color hover:surface-200 border-noround">
                    <ComIcon icon="iconGeneralList" style="height: 14px;" />
                    <span class="ml-2">Group Bill To Room and Tax to Company, Extra to Guest</span>
                </button>
         
                <button @click="onGroupChangeRate" 
                    class="w-full p-link flex align-items-center py-2 px-3 text-color hover:surface-200 border-noround">
                    <ComIcon icon="iconGeneralList" style="height: 14px;" />
                    <span class="ml-2">Group Change Rate</span>
                </button>
                <button @click="onGroupChangeStayDate" 
                    class="w-full p-link flex align-items-center py-2 px-3 text-color hover:surface-200 border-noround">
                    <ComIcon icon="iconGeneralList" style="height: 14px;" />
                    <span class="ml-2">Group Change Stay Date</span>
                </button>
                <button @click="onGroupChangeStayDate" 
                    class="w-full p-link flex align-items-center py-2 px-3 text-color hover:surface-200 border-noround">
                    <ComIcon icon="iconGeneralList" style="height: 14px;" />
                    <span class="ml-2">Stay To Other Reservation</span>
                </button>
                <button  v-if="rs.reservation.reservation_type == 'FIT'" @click="onMarkasGITReservation()"
                    class="w-full p-link flex align-items-center py-2 px-3 text-color hover:surface-200 border-noround">                   
                    <ComIcon icon="userGif" style="height: 15px;" />
                    <span class="ml-2">Mark as GIT Reservation</span>
                </button>

                <button v-else  @click="onMarkasFITReservation()"
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
        <ComDialogNote :header="note.title" :visible="note.show" :loading="loading" @onOk="onSaveGroupStatus" @onClose="onCloseNote"/>
    </div>
</template>
<script setup>
import {useDialog, inject, ref, useConfirm, useToast, postApi } from "@/plugin";
import ComAuditTrail from '../../../components/layout/components/ComAuditTrail.vue';
import ComGroupAssignRoom from "./form/ComGroupAssignRoom.vue";
 
const dialog = useDialog();


const socket = inject("$socket")
const moment = inject("$moment")
const confirm = useConfirm()
const toast = useToast();
const emit = defineEmits(['onAuditTrail', "onRefresh"])
const menu = ref();
const loading = ref(false);
const gv = inject("$gv")
const rs = inject("$reservation")
const frappe = inject('$frappe');
const db = frappe.db();
const note = ref({
    title: '',
    show: false,
    reservation_status:'' // No Show // Void // Cancel
})
 
const toggle = (event) => {
    menu.value.toggle(event);
}
function onMarkAsReservationType() {
    confirm.require({
        message: `Are you sure you want to mark as ${rs.reservation.reservation_type == 'FIT' ? 'GIT' : 'FIT'} reservation?`,
        header: 'Confirmation',
        icon: 'pi pi-exclamation-triangle',
        acceptClass: 'border-none crfm-dialog',
        rejectClass: 'hidden',
        acceptIcon: 'pi pi-check-circle',
        acceptLabel: 'Ok',
        accept: () => {
            db.updateDoc('Reservation', rs.reservation?.name, {
                reservation_type: rs.reservation.reservation_type == 'GIT' ? 'FIT' : 'GIT',
            })
                .then((doc) => {
                    rs.reservation.reservation_type = doc.reservation_type
                    toast.add({
                        severity: 'success', summary: `Mark as ${rs.reservation.reservation_type } reservation`,
                        detail: `Mark as ${rs.reservation.reservation_type} Reservation Successfully`, life: 3000  
                    });
                })
        },

    });
}
function onChangeStatus(reservation_status){
    if(validateSelectReservation()){
        note.value.title = `${reservation_status}`
        note.value.show = true
        note.value.reservation_status = reservation_status
    }
}
function validateSelectReservation(){
    if(rs.selecteds && rs.selecteds.length > 0){
        return true
    }
    else{
        gv.toast('warn','Please select reservation stay.')
        return false
    }
}
function onSaveGroupStatus(r){ 
    const data = {
        reservation: rs.reservation.name,
        stays:rs.selecteds,
        status:note.value.reservation_status,
        note:r.note,
        reserved_room: r.reserved_room
    } 
    postApi('reservation.update_reservation_status',data).then((r)=>{
        onCloseNote()
        rs.LoadReservation(rs.reservation.name)
    })
}
function onCloseNote(){
    note.value.title = ''
    note.value.show = false
    note.value.reservation_status = ''
}

function onGroupCheckIn (){
    alert('hello-world')
}
function onGroupCheckOut(is_not_undo = false){
    const isSelect = validateSelectReservation()
    if(isSelect){
        confirm.require({
        message: `Are you sure you want to${is_not_undo ? ' undo ' :' '}check out reservations?`,
        header: 'Check Out',
        icon: 'pi pi-info-circle',
        acceptClass: 'border-none crfm-dialog',
        rejectClass: 'hidden',
        acceptIcon: 'pi pi-check-circle',
        acceptLabel: 'Ok',
        accept: () => {
            const checkList = rs.selecteds.map((r)=>r.name).join(',')
            postApi("reservation.check_out",{
                reservation: rs.reservation.name,
                reservation_stays: checkList,
                is_undo: !is_not_undo
            }).then((result) => {
                if(result){
                    rs.LoadReservation()
                }
            }).catch((error) => {
                //
            })

        }
    });
    }
}

function onGroupAssignRoom(){
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
            position:"top",
            modal: true,
            maximizable: true,
            closeOnEscape: false
        }
    });
}

function onGroupBuildToCompany (){
    alert()
}

function onGroupBuildToMasterGroup (){
    alert()
}

function onGroupBuildToGuest (){
    alert()
}

function onGroupBuildToRoomandTaxtoCompany (){
    alert()
}

function onAuditTrail() {
    const dialogRef = dialog.open(ComAuditTrail, {
        data: {
            doctype: 'Reservation',
            docname: name.value
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

function onGroupChangeRate(){
    alert()
}

function onGroupChangeStayDate(){
    alert()
}
function onStayToOtherReservation(){
   
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
                    rs.reservation.reservation_type = doc.reservation_type,
                        toast.add({
                            severity: 'success', summary: 'Mark as FIT Reservation',
                            detail: 'Mark as FIT Reservation Successfully', life: 3000
                        });
                })
        },

    });
}
</script>