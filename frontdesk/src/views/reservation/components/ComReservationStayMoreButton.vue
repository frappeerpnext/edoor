<template>
    <div> 
        <div class="flex items-center justify-end">
            <div class="res_btn_st">
                <Button :class="class" class="h-2rem w-2rem" style="font-size: 1.5rem" text rounded :aria-controls="data.name.replaceAll(' ', '')" icon="pi pi-ellipsis-v" @click="toggle"></Button>
            </div>
            <Menu ref="show" :model="menus" :id="data.name.replaceAll(' ', '')" :popup="true" style="min-width: 180px;">
                <template #end> 
                        <button @click="onMarkAsMasterRoom()"
                        v-if="props.data.is_master == 0 && (props.data.reservation_status == 'Reserved' || props.data.reservation_status == 'In-house' || props.data.reservation_status == 'Confirmed')"
                        class="w-full p-link flex align-items-center p-2  text-color hover:surface-200 border-noround">
                        <ComIcon icon="iconCrownBlack" style="height: 12px;" />
                        <span class="ml-2">Mark as Master Room</span>
                        </button>
                        <button @click="onClickDetail" class="w-full p-link flex align-items-center p-2  text-color hover:surface-200 border-noround">
                            <i class="pi pi-eye me-2" />
                            View Reservation Stay
                        </button>
                        <template v-if="data.reservation_status == 'Reserved' || data.reservation_status == 'Confirmed'">
                            <button @click="onChangeStatus('No Show')" v-if="data.reservation_status == 'Reserved'" class="w-full p-link flex align-items-center p-2  text-color hover:surface-200 border-noround">
                                <i class="pi pi-eye-slash me-2" />
                                No Show
                            </button>
                            <button @click="onChangeStatus('Cancelled')" v-if="data.reservation_status != 'Cancelled'" class="w-full p-link flex align-items-center p-2  text-color hover:surface-200 border-noround">
                                <i class="pi pi-user-minus me-2" />
                                Cancel
                            </button>
                            <button @click="onChangeStatus('Void')" v-if="data.reservation_status != 'Void'" class="w-full p-link flex align-items-center p-2  text-color hover:surface-200 border-noround">
                                <i class="pi pi-file-excel me-2" />
                                Void
                            </button>
                            <button class="w-full p-link flex align-items-center p-2  text-color hover:surface-200 border-noround">
                                <ComIcon icon="checkin-black" class="me-2" style="height: 14px;" />
                                Check-In
                            </button>
                        </template>
                        <button v-if="data.reservation_status == 'Checked In' || data.reservation_status == 'In-house'" class="w-full p-link flex align-items-center p-2  text-color hover:surface-200 border-noround">
                            <ComIcon icon="checkoutBlack" class="me-2" style="height: 12px;" />
                            Check Out
                        </button>
                        <div>
                            <button v-if="props.data.paid_by_master_room && !props.data.is_master" @click="onUnmarkasPaidbyMasterRoom()" class="w-full p-link flex align-items-center p-2  text-color hover:surface-200 border-noround">
                                <ComIcon  icon="BilltoMasterRoom" class="me-2" style="height:15px;" ></ComIcon>
                                Unmark as Paid by Master Room
                            </button>
                            <button v-else-if="!props.data.paid_by_master_room && !props.data.is_master" @click="onMarkasPaidbyMasterRoom()" class="w-full p-link flex align-items-center p-2  text-color hover:surface-200 border-noround">
                                <ComIcon  icon="BilltoMasterRoom" class="me-2" style="height:15px;" ></ComIcon>
                                Mark as Paid by Master Room
                            </button>
                        </div>

                        <div>
                            <button v-if="!props.data.allow_post_to_city_ledger" @click="onAllowPosttoCityLedger()" class="w-full p-link flex align-items-center p-2 text-color hover:surface-200 border-noround">
                                <ComIcon  icon="IconBillToCompany" class="me-2" style="height:15px;" ></ComIcon>
                                Allow Post to City Ledger 
                            </button>
                            <button v-else @click="onUnallowPosttoCityLedger()" class="w-full p-link flex align-items-center p-2 text-color hover:surface-200 border-noround">
                                <ComIcon  icon="IconBillToCompany" class="me-2" style="height:15px;" ></ComIcon>
                                Unallow Post to City Ledger 
                            </button>
                        </div>
                </template>
            </Menu>
        </div>
    </div>
</template>
<script setup>
import {ref, useDialog, postApi,inject,useConfirm,useToast} from '@/plugin'
import ComDialogNote from '@/components/form/ComDialogNote.vue';
const moment = inject("$moment")
const props = defineProps({
    data: Object,
    class: String
})
const emit = defineEmits('onClickDetail')

const rs = inject("$reservation")
const dialog = useDialog()
const show = ref()
const loading = ref(false)
const confirm = useConfirm()
const frappe = inject('$frappe');
const db = frappe.db();
const toast = useToast();

const note = ref({
    title: '',
    show: false,
    reservation_status:'' // No Show // Void // Cancel
})
const toggle = (event) => {
    show.value.toggle(event);
};
function onClickDetail(){
    show.value.hide()
    emit('onClickDetail',props.data.name)

}

function onChangeStatus(reservation_status){
    let confirm_message = ""
    if (reservation_status=="Cancelled"){
        confirm_message = "You are about to cancel reservation(s).<br/> Once the cancellation is complete, you will no longer be able to make any changes to the reservation. <br/> If you have a cancellation charge, please update the folio transaction first."
    }else if(reservation_status=="Void"){
        confirm_message = "You are about to void  reservation(s). Once the void is complete, you will no longer be able to make any changes to the reservation."
    }else {
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
                    show_reserved_room:reservation_status=="No Show"?true:false,
                    stays: [{name:props.data.name,reservation_status: props.data.reservation_status}]
                    
                },

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
              setTimeout(function(){
                rs.LoadReservation(rs.reservation.name)
                window.socket.emit("RefresheDoorDashboard", rs.reservation.property);
              },1500)
                
        
             }
         }

    });

}

function onUnmarkasPaidbyMasterRoom(){
    confirm.require({
        message: 'Are you sure you want to Unmark as Piad by Master Room?',
        header: 'Confirmation',
        icon: 'pi pi-exclamation-triangle',
        acceptClass: 'border-none crfm-dialog',
        rejectClass: 'hidden',
        acceptIcon: 'pi pi-check-circle',
        acceptLabel: 'Ok',
        accept: () => {
            db.updateDoc('Reservation Stay', props.data.name, {
                paid_by_master_room: 0,
            })
                .then((doc) => {

                    props.data.paid_by_master_room = doc.paid_by_master_room;
                    toast.add({
                        severity: 'success', summary: 'Unmark as Piad by Master Room',
                        detail: 'Unmark as Piad by Master Room Successfully', life: 3000
                    });
                })

        },

    });
}
function onMarkasPaidbyMasterRoom(){
    confirm.require({
        message: 'Are you sure you want to Mark as Piad by Master Room?',
        header: 'Confirmation',
        icon: 'pi pi-exclamation-triangle',
        acceptClass: 'border-none crfm-dialog',
        rejectClass: 'hidden',
        acceptIcon: 'pi pi-check-circle',
        acceptLabel: 'Ok',
        accept: () => {
            db.updateDoc('Reservation Stay', props.data.name, {
                paid_by_master_room: 1,
            })
                .then((doc) => {

                    props.data.paid_by_master_room = doc.paid_by_master_room;
                    toast.add({
                        severity: 'success', summary: 'Mark as Piad by Master Room',
                        detail: 'Mark as Piad by Master Room Successfully', life: 3000
                    });
                })

        },

    });
}
function onAllowPosttoCityLedger(){
    confirm.require({
        message: 'Are you sure you want to Allow Post to City Ledger?',
        header: 'Confirmation',
        icon: 'pi pi-exclamation-triangle',
        acceptClass: 'border-none crfm-dialog',
        rejectClass: 'hidden',
        acceptIcon: 'pi pi-check-circle',
        acceptLabel: 'Ok',
        accept: () => {
            db.updateDoc('Reservation Stay', props.data.name, {
                allow_post_to_city_ledger: 1,
            })
                .then((doc) => {
                    props.data.allow_post_to_city_ledger = doc.allow_post_to_city_ledger;
                    toast.add({
                        severity: 'success', summary: 'Allow Post to City Ledger',
                        detail: 'Allow Post to City Ledger Successfully', life: 3000
                    });
                })
        },

    });
}
function onUnallowPosttoCityLedger(){
    confirm.require({
        message: 'Are you sure you want to Unallow Post to City Ledger?',
        header: 'Confirmation',
        icon: 'pi pi-exclamation-triangle',
        acceptClass: 'border-none crfm-dialog',
        rejectClass: 'hidden',
        acceptIcon: 'pi pi-check-circle',
        acceptLabel: 'Ok',
        accept: () => {
            db.updateDoc('Reservation Stay', props.data.name, {
                allow_post_to_city_ledger: 0,
            })
                .then((doc) => {
                    props.data.allow_post_to_city_ledger = doc.allow_post_to_city_ledger;
                    toast.add({
                        severity: 'success', summary: 'Unallow Post to City Ledger',
                        detail: 'Unallow Post to City Ledger Successfully', life: 3000
                    });
                })
        },

    });
}
function onMarkAsMasterRoom (){
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
                reservation_stay: props.data.name,
                
            }).then((doc) => {
                rs.reservationStays.forEach(r => r.is_master = false);
                props.data.is_master = doc.message.is_master
            })
        },
    });
} 

</script>
<style>
    .res_btn_st button{
        padding: unset !important;
    }
</style>