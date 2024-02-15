<template>
    <div> 
        <div class="flex items-center justify-end">
            <div class="res_btn_st">
                <Button  :class="class" class="h-2rem w-2rem" style="font-size: 1.5rem" text rounded :aria-controls="data.name.replaceAll(' ', '')" icon="pi pi-ellipsis-v" @click="toggle"></Button>
            </div>
            <Menu ref="show" :model="menus" :id="data.name.replaceAll(' ', '')" :popup="true" style="min-width: 180px;">
                <template #end>
                        <button @click="onChangeStay(data)"  class="w-full p-link flex align-items-center p-2 pl-4 text-color hover:surface-200 border-noround">
                            Change Stay
                        </button> 
                        <button  v-if="data?.room_id"  @click="onUnassignRoom(data)" class="w-full p-link flex align-items-center p-2 pl-4 text-color hover:surface-200 border-noround">
                            Unassign room
                        </button>
                        <button @click="onOpenDeleted(data)" class="w-full p-link flex align-items-center p-2 pl-4 text-color hover:surface-200 border-noround">
                            Delete
                        </button>
                        
                </template>
            </Menu>
        </div>
    </div>
    
</template>
<script setup>
import {ref,inject, useDialog, useConfirm, postApi} from '@/plugin'
import ComReservationStayChangeStay from './ComReservationStayChangeStay.vue';
import ComDialogNote from '@/components/form/ComDialogNote.vue';

const rs = inject('$reservation_stay')
const gv = inject('$gv')
const moment = inject('$moment')
const dialogRef = inject('dialogRef')
const dialogConfirm = useConfirm()
const edoor_working_day = JSON.parse(localStorage.getItem('edoor_working_day'))
const props = defineProps({
    data: Object,
    rooms: Array,
    class: String
})
const dialog = useDialog()
const emit = defineEmits('onSelected')
const show = ref()

const loading = ref(false)
const toggle = (event) => {
    show.value.toggle(event);
};
function isNotLast(){
    const names = props.rooms.map(item => item.name);
    const index = names.indexOf(props.data.name)
    if((index + 1) < props.rooms.length ){
        gv.toast('warn',"This room stay is not last stay.")
        return false
    }else{
        return true
    }
}
function isNotLastForDelete(){
    const names = props.rooms.map(item => item.name);
    const index = names.indexOf(props.data.name)
    if((index + 1) < props.rooms.length && index !=0){
        gv.toast('warn',"This room stay is not last stay.")
        return false
    }else{
        return true
    }
}
function onOpenDeleted(data){
    if(moment(data.start_date).isAfter(edoor_working_day.date_working_day) && props?.rooms.length > 1  ){
        if(isNotLastForDelete()){
            
            const dialogRef = dialog.open(ComDialogNote, {
                data: {
                    api_url: "reservation.delete_stay_room",
                    method: "DELETE",
                    confirm_message: "Are you sure you want to delete this stay room?",
                    data: {
                        parent: props.data.parent,
                        name: props.data.name, 
                    }
                },
                props: {
                    header: "Delete Stay Room",
                    style: {
                        width: '50vw',
                    },
                    modal: true,
                    maximizable: true,
                    closeOnEscape: false,
                    position: "top",
                    pt: {
                root: `${window.isMobile ? 'p-dialog-maximized' : ''}`
            }
                },
                onClose: (options) => {
                    const data = options.data;
                    if (data) {
                        rs.getReservationDetail(props.data.parent)
                    }
                }

    });

        }
    }else{
        gv.toast('warn',"This room stay is disallow to delete.")
    }
    
    
}
function onSelected(room,status){
    show.value.hide()
    emit('onSelected',room,status)
}
 

function onChangeStay(data){
 
    
    if((moment(data.end_date).isSame(edoor_working_day.date_working_day) || moment(data.end_date).isAfter(edoor_working_day.date_working_da)) || rs.reservationStay.reservation_status !='Checked Out'){
        if(data.can_change_start_date==1 || data.can_change_end_date==1){
            dialog.open(ComReservationStayChangeStay, {
                data: {
                    item: props.data
                },
                props: {
                    header: `Change Stay`,
                    style: {
                        width: '60vw',
                    },
                    
                    modal: true,
                    closeOnEscape: false,
                    position: 'top'
                },
                onClose: (options) => {
                    //
                }
            })
            
        }else {
            gv.toast('warn',"This room stay is disallow to change stay.")
        }
    }else{
        gv.toast('warn',"This room stay is disallow to change stay.")
    }
    
}
function onUnassignRoom(data){

    
    dialogConfirm.require({
        message: 'Are you sure to unassign room?',
        header: 'Unassign Confirmation',
        icon: 'pi pi-info-circle',
        acceptClass: 'border-none crfm-dialog',
        rejectClass: 'hidden',
        acceptIcon: 'pi pi-check-circle',
        acceptLabel: 'Ok',
        accept: () => {
            loading.value = true
            postApi("reservation.unassign_room",{reservation_stay: rs.reservationStay.name, room_stay: props.data.name}).then((r)=>{
                loading.value = false
                rs.reservationStay = r.message
                window.postMessage({"action":"Dashboard"},"*")
                window.postMessage({action:"ReservationStayList"},"*")
                window.postMessage({action:"ReservationList"},"*")
                window.postMessage({action:"ReservationDetail"},"*")
                window.postMessage({action:"ReservationStayDetail"},"*")      
                window.postMessage({"action":"Frontdesk"},"*")  
                window.postMessage({action:"TodaySummary"},"*")
                window.postMessage({action:"GuestLedger"},"*")
                window.postMessage({action:"GuestLedgerTransaction"},"*")
                window.postMessage({action:"Reports"},"*")

            }).catch(()=>{
                loading.value = false
            })
        }
    })
  
}
</script>
<style>
    .res_btn_st button{
        padding: unset !important;
    }
</style>