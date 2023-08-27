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
                        
                        <button class="w-full p-link flex align-items-center p-2  text-color hover:surface-200 border-noround">
                            <ComIcon  icon="IconBillToGuest" class="me-2" style="height:15px;" ></ComIcon>
                            Bill To Guest
                        </button>
                        <button class="w-full p-link flex align-items-center p-2  text-color hover:surface-200 border-noround">
                            <i class="pi pi-money-bill me-2" />
                            Bill To Room and Tax to Company, Extra to Guest
                        </button>
                </template>
            </Menu>
        </div>
    </div>
    <ComDialogNote :header="note.title" :visible="note.show" :loading="loading" @onOk="onSaveNote" @onClose="onCloseNote"/>
</template>
<script setup>
import {ref, useDialog, postApi,inject,useConfirm,useToast} from '@/plugin'
const moment = inject("$moment")
const props = defineProps({
    data: Object,
    class: String
})
const emit = defineEmits('onClickDetail')

const rs = inject("$reservation")
const socket = inject("$socket")
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
function onChangeStatus(status){
    note.value.title = `${status} : ${props.data.name}`
    note.value.show = true
    note.value.reservation_status = status
}
function onCloseNote(){
    note.value.title = ''
    note.value.show = false
    note.value.reservation_status = ''
}
function onSaveNote(text_note){
    loading.value = true
    // const data = JSON.parse(JSON.stringify(props.data))
    // data.reservation_status = note.value.reservation_status
    // data.reservation_status_note = text_note
 
    const data = {
        reservation: rs.reservation.name,
        stays: [props.data],
        status:note.value.reservation_status,
        note:text_note
    } 
    postApi('reservation.update_reservation_status',data).then((r)=>{
        rs.LoadReservation(r.reservation)
        socket.emit("RefreshReservationDetail", r.reservation);
        loading.value = false
        onCloseNote()
        rs.LoadReservation(rs.reservation.name)
    }).catch(()=>{
        loading.value = false
    })
    // data.update_room_occupy = true
    // data.update_reservation = true
    // updateDoc('Reservation Stay', data.name, data).then((r)=>{
    //     if(r.reservation){
    //         rs.LoadReservation(r.reservation)
    //         socket.emit("RefreshReservationDetail", r.reservation);
    //         loading.value = false
    //         onCloseNote()
    //     }
            
    
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