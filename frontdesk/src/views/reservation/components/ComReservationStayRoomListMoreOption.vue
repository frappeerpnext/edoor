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
                        <button @click="onUnassignRoom" v-if="moment(data.start_date).isAfter(edoor_working_day.date_working_day) && data.room_id" class="w-full p-link flex align-items-center p-2 pl-4 text-color hover:surface-200 border-noround">
                            Unassign room
                        </button>
                        <button @click="openNote = true" v-if="moment(data.start_date).isAfter(edoor_working_day.date_working_day)" class="w-full p-link flex align-items-center p-2 pl-4 text-color hover:surface-200 border-noround">
                            Delete
                        </button>
                </template>
            </Menu>
        </div>
    </div>
    <ComDialogNote header="Delete Room Stay" :visible="openNote" :loading="loading" @onOk="onDeleted" @onClose="onCloseNote"/>
</template>
<script setup>
import {ref,inject, useDialog, deleteApi, useConfirm, updateDoc} from '@/plugin'
import ComReservationStayChangeStay from './ComReservationStayChangeStay.vue';
import ComNote from '@/components/form/ComNote.vue';
const rs = inject('$reservation_stay')
const moment = inject('$moment')
const dialogConfirm = useConfirm()
const edoor_working_day = JSON.parse(localStorage.getItem('edoor_working_day'))
const props = defineProps({
    data: Object,
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
            loading.value = false
            openNote.value = false
            rs.getReservationDetail(props.data.parent)
        }
    }).catch((r)=>{
        loading.value = false
    })
}
function onChangeStay(){
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
            closeOnEscape: false
        },
        onClose: (options) => {
            //
        }
    })
}
function onUnassignRoom(){
    dialogConfirm.require({
        message: 'Are you sure to unassign room?',
        header: 'Unassign Confirmation',
        icon: 'pi pi-info-circle',
        acceptClass: 'border-none crfm-dialog',
        accept: () => {
            loading.value = true
            let data = JSON.parse(JSON.stringify(rs.reservationStay))
 
            data.stays.filter(r=>{
                if(r.name == props.data.name){
                    r.room_id = ''
                    r.room_number = ''
                }
                return r
            })
            data.update_reservation_stay = true
            data.update_room_occupy = true
            updateDoc('Reservation Stay',data.name,data).then((r)=>{
                rs.reservationStay = r
                loading.value = false
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