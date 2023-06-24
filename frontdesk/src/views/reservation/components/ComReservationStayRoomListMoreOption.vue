<template>
    <div> 
        <div class="flex items-center justify-end">
            <div class="res_btn_st">
                <Button :class="class" class="h-2rem w-2rem" style="font-size: 1.5rem" text rounded :aria-controls="data.name.replaceAll(' ', '')" icon="pi pi-ellipsis-v" @click="toggle"></Button>
            </div>
            <Menu ref="show" :model="menus" :id="data.name.replaceAll(' ', '')" :popup="true" style="min-width: 180px;">
                <template #end>
                        <button v-if="moment(data.start_date).isAfter(edoor_working_day.date_working_day)" class="w-full p-link flex align-items-center p-2 pl-4 text-color hover:surface-200 border-noround">
                            Delete
                        </button>
                        <button @click="onChangeStay" v-if="moment(data.end_date).isSame(edoor_working_day.date_working_day) || moment(data.end_date).isAfter(edoor_working_day.date_working_day)" class="w-full p-link flex align-items-center p-2 pl-4 text-color hover:surface-200 border-noround">
                            Change Stay
                        </button>
                        <button class="w-full p-link flex align-items-center p-2 pl-4 text-color hover:surface-200 border-noround">
                            Unassign room
                        </button>
                </template>
            </Menu>
        </div>
    </div>
</template>
<script setup>
import {ref,inject, useDialog} from '@/plugin'
import ComReservationStayChangeStay from './ComReservationStayChangeStay.vue';
const rs = inject('$reservation_stay')
const moment = inject('$moment')
const edoor_working_day = JSON.parse(localStorage.getItem('edoor_working_day'))
const props = defineProps({
    data: Object,
    class: String
})
const dialog = useDialog()
const emit = defineEmits('onSelected')
const show = ref()
const toggle = (event) => {
    show.value.toggle(event);
};
function onSelected(room,status){
    show.value.hide()
    emit('onSelected',room,status)
}
function onChangeStay(){
    dialog.open(ComReservationStayChangeStay, {
        data: {
            item: props.data
        },
        props: {
            header: `Change Stay`,
            style: {
                width: '70vw',
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
</script>
<style>
    .res_btn_st button{
        padding: unset !important;
    }
</style>