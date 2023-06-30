<template>
    <div> 
        <div class="flex items-center justify-end">
            <div class="res_btn_st">
                <Button :class="class" class="h-2rem w-2rem" style="font-size: 1.5rem" text rounded :aria-controls="data.name.replaceAll(' ', '')" icon="pi pi-ellipsis-v" @click="toggle"></Button>
            </div>
            <Menu ref="show" :model="menus" :id="data.name.replaceAll(' ', '')" :popup="true" style="min-width: 180px;">
                <template #end> 
                        <button @click="onClickDetail" class="w-full p-link flex align-items-center p-2 pl-4 text-color hover:surface-200 border-noround">
                            View Reservation Stay
                        </button>
                        <template v-if="data.reservation_status == 'Reserved' || data.reservation_status == 'Confirmed'">
                            <button @click="onChangeStatus('No Show')" v-if="data.reservation_status == 'Reserved'" class="w-full p-link flex align-items-center p-2 pl-4 text-color hover:surface-200 border-noround">
                                No Show
                            </button>
                            <button @click="onChangeStatus('Cancelled')" v-if="data.reservation_status != 'Cancelled'" class="w-full p-link flex align-items-center p-2 pl-4 text-color hover:surface-200 border-noround">
                                Cancel
                            </button>
                            <button @click="onChangeStatus('Void')" v-if="data.reservation_status != 'Void'" class="w-full p-link flex align-items-center p-2 pl-4 text-color hover:surface-200 border-noround">
                                Void
                            </button>
                            <button class="w-full p-link flex align-items-center p-2 pl-4 text-color hover:surface-200 border-noround">
                                Check-In
                            </button>
                        </template>
                        <button v-if="data.reservation_status == 'Checked In' || data.reservation_status == 'In-house'" class="w-full p-link flex align-items-center p-2 pl-4 text-color hover:surface-200 border-noround">
                            Check Out
                        </button>
                        <button class="w-full p-link flex align-items-center p-2 pl-4 text-color hover:surface-200 border-noround">
                            Build To Company
                        </button>
                        <button class="w-full p-link flex align-items-center p-2 pl-4 text-color hover:surface-200 border-noround">
                            Build To Master Group 
                        </button>
                        <button class="w-full p-link flex align-items-center p-2 pl-4 text-color hover:surface-200 border-noround">
                            Build To Guest
                        </button>
                        <button class="w-full p-link flex align-items-center p-2 pl-4 text-color hover:surface-200 border-noround">
                            Build To Room and Tax to Company, Extra to Guest
                        </button>
                </template>
            </Menu>
        </div>
    </div>
    <ComDialogNote :header="note.title" :visible="note.show" :loading="loading" @onOk="onSaveNote" @onClose="onCloseNote"/>
</template>
<script setup>
import {ref, useDialog, updateDoc,inject} from '@/plugin'

const props = defineProps({
    data: Object,
    class: String
})
const emit = defineEmits('onClickDetail')
const rs = inject("$reservation")
const dialog = useDialog()
const show = ref()
const loading = ref(false)
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
    const data = JSON.parse(JSON.stringify(props.data))
    data.reservation_status = note.value.reservation_status
    data.reservation_status_note = text_note
    data.update_room_occupy = true
    data.update_reservation_stay = true
    updateDoc('Reservation Stay', data.name, data).then((r)=>{
        if(r.reservation){
            rs.LoadReservation(r.reservation)
            loading.value = false
            onCloseNote()
        }
            
    }).catch(()=>{
        loading.value = false
    })
}
</script>
<style>
    .res_btn_st button{
        padding: unset !important;
    }
</style>