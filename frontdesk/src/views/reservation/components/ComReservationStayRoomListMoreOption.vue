<template>
    <div> 
        <div class="flex items-center justify-end">
            <div class="res_btn_st">
                <Button :class="class" class="h-2rem w-2rem" style="font-size: 1.5rem" text rounded :aria-controls="data.name.replaceAll(' ', '')" icon="pi pi-ellipsis-v" @click="toggle"></Button>
            </div>
            <Menu ref="show" :model="menus" :id="data.name.replaceAll(' ', '')" :popup="true" style="min-width: 180px;">
                <template #end>
                        <button @click="onChangeStay" v-if="moment(data.end_date).isSame(edoor_working_day.date_working_day) || moment(data.end_date).isAfter(edoor_working_day.date_working_day)" class="w-full p-link flex align-items-center p-2 pl-4 text-color hover:surface-200 border-noround">
                            Change Stay
                        </button>
                        <button  @click="onUnassignRoom" v-if="(moment(data.start_date).isAfter(edoor_working_day.date_working_day) || moment(data.start_date).isSame(edoor_working_day.date_working_day)) && data.room_id && rs.reservationStay.reservation_status=='Reserved'" class="w-full p-link flex align-items-center p-2 pl-4 text-color hover:surface-200 border-noround">
                            Unassign room
                        </button>
                        <button @click="onOpenDeleted" v-if="moment(data.start_date).isAfter(edoor_working_day.date_working_day) && props?.rooms.length > 1  " class="w-full p-link flex align-items-center p-2 pl-4 text-color hover:surface-200 border-noround">
                            Delete
                        </button>
                </template>
            </Menu>
        </div>
    </div>
    <ComDialogNote header="Delete Room Stay" :visible="openNote" :loading="loading" @onOk="onDeleted" @onClose="onCloseNote"/>
</template>
<script setup>
import {ref,inject, useDialog, deleteApi, useConfirm, postApi} from '@/plugin'
import ComReservationStayChangeStay from './ComReservationStayChangeStay.vue';
import ComNote from '@/components/form/ComNote.vue';
const rs = inject('$reservation_stay')
const socket = inject('$socket')
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
const openNote = ref(false)
const loading = ref(false)
const toggle = (event) => {
    show.value.toggle(event);
};
function isNotLast(){
    const names = props.rooms.map(item => item.name);
    const index = names.indexOf(props.data.name)
    if((index + 1) < props.rooms.length){
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
function onOpenDeleted(){
    if(isNotLastForDelete()){
        openNote.value = true
    }
    
}
function onSelected(room,status){
    show.value.hide()
    emit('onSelected',room,status)
}
function onCloseNote(){
    openNote.value = false
}
function onDeleted(note){
    loading.value = true
    deleteApi('reservation.delete_stay_room', {
        parent: props.data.parent,
        name: props.data.name, 
        note: note
    })
    .then((result) => {
        if(result.message){
            openNote.value = false
            rs.getReservationDetail(props.data.parent)
            loading.value = false

            socket.emit("RefreshReservationDetail", rs.reservationStay.reservation);

            socket.emit("RefreshData", { property: rs.reservationStay.property, action: "refresh_iframe_in_modal" })
            
            socket.emit("RefreshData", {reservation_stay:rs.reservationStay.name,action:"refresh_reservation_stay"})

            socket.emit("RefresheDoorDashboard", rs.reservationStay.property)

        }
    }).catch((r)=>{
        loading.value = false
    })
}
function onChangeStay(){
    if(isNotLast()){
        dialog.open(ComReservationStayChangeStay, {
            data: {
                item: props.data
            },
            props: {
                header: `Change Stay`,
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
                //
            }
        })
    }
}
function onUnassignRoom(){
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

                socket.emit("RefreshReservationDetail", rs.reservationStay.reservation);

                socket.emit("RefresheDoorDashboard", rs.reservationStay.property);

                socket.emit("RefreshData", { property: rs.reservationStay.property, action: "refresh_iframe_in_modal" })

                socket.emit("RefreshData", {reservation_stay:rs.reservationStay.name,action:"refresh_reservation_stay"})
                
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