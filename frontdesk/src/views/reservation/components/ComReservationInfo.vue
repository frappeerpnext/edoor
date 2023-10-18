<template>
    <ComReservationStayPanel title="Stay Information">
        <template #btn>
            <div class="flex items-center">
                <span> Res {{ rs.reservation?.reservation_type }} Color </span> 
                <button :style="{background:rs?.reservation?.reservation_color}"  @click="toggle($event, 'Change_color')" class="w-2rem ms-2 h-2rem rounded-lg border-2 border-gray-500"></button>   
            </div>
        </template>
        <template #content>
            <div>
                <div class="flex mt-2 gap-2">
                    <ComBoxStayInformation  @onClick="toggle($event, 'edit_reservation_information')"  :isAction="true" titleTooltip="Reservation Date" title="Res. Date" :value="gv.dateFormat(rs.reservation?.reservation_date)"
                        valueClass="grow"></ComBoxStayInformation>
                </div>
                <div class="flex mt-2 gap-2">
                    <ComBoxStayInformation @onClick="toggle($event, 'edit_reservation_information')" :isAction="true" titleTooltip="Reference Number" title="Ref. No"
                         :isSlot="true" valueClass="grow">
                        <span>
                            <i v-if="!rs.reservation?.reference_number" class="pi pi-pencil"></i>
                            {{ rs.reservation?.reference_number ? rs.reservation?.reference_number : '...' }}
                        </span>
                    </ComBoxStayInformation>
                    <ComBoxStayInformation @onClick="toggle($event, 'edit_reservation_information')" :isSlot="true" :isAction="true" titleTooltip="Internal Reference Number" title="Int. No"
                         valueClass="grow"
                        titleClass="w-4rem leading-10">
                        <span>
                            <i v-if="!rs.reservation?.internal_reference_number" class="pi pi-pencil"></i>
                            {{ rs.reservation?.internal_reference_number ? rs.reservation?.internal_reference_number : '...' }}
                        </span>
                    </ComBoxStayInformation>
                </div>
                <div class="flex mt-2 gap-2" v-if="!(rs.reservation?.reservation_type == 'FIT')">
                    <ComBoxStayInformation @onClick="toggle($event, 'edit_reservation_information')"   title="Group"  valueClass="grow">
                        <button class="link_line_action text-left overflow-hidden" v-if="!rs.reservation?.group_name && !rs.reservation?.group_code">
                            <i class="pi pi-pencil"></i>
                            ...
                        </button>
                        <div v-else class="flex gap-2">
                            <a v-tippy="'Group Name'" v-if="rs.reservation?.group_name" class="link_line_action grow overflow-hidden w-6" >{{ rs.reservation?.group_name }}</a>
                            <button v-else class="link_line_action grow text-left overflow-hidden" >
                                <i class="pi pi-pencil"></i>
                                ...
                            </button>
                            <span>/</span>
                            <a v-tippy="'Group Code'" v-if="rs.reservation?.group_code" class="link_line_action grow w-6" >
                                {{ rs.reservation?.group_code }}
                            </a>
                            <button v-else class="link_line_action grow text-left overflow-hidden" >
                                <i class="pi pi-pencil"></i>
                            ...  
                            </button>
                        </div>
                    </ComBoxStayInformation>
                </div>
                <div class="flex mt-2 gap-2">
                    <ComBoxStayInformation titleTooltip="Reservation Number" title="Res. No"
                        :value="rs.reservation?.name" valueClass="grow">
                    </ComBoxStayInformation>
                </div>
                <div class="flex mt-2 gap-2">
                    <ComBoxStayInformation title="Rooms" valueClass="grow">
                        <div v-if="rs && rs?.reservationStays">
                            <div> 
                                <span v-for="(i, index) in roomData" :key="index">
                                    <div class="inline" v-if="index < 3">
                                        <div class="rounded-xl px-2 me-1 bg-gray-edoor inline">
                                        <span v-tippy="i.room_type">{{i.room_type_alias}}</span>
                                        <span v-if="i.room_number">/{{ i.room_number }}  
                                        </span>
                                        </div>
                                    </div>
                                </span>
                                <span v-if="roomData.length > 3"
                                    v-tippy="getTooltip()"    
                                    class="inline rounded-xl px-2 bg-purple-cs w-auto ms-1 cursor-pointer">
                                    {{roomData.length - 3}} Mores
                                </span>
                            </div>
                        </div>
                    </ComBoxStayInformation>
                </div>
                <div class="flex mt-2 gap-2">
                    <ComBoxStayInformation @onClick="toggle($event, 'change_date')" :isAction="true" title="Arrival"                    
                        :value="moment(rs.reservation?.arrival_date).format('DD-MM-yyyy')"
                        valueClass="col-4 " ></ComBoxStayInformation>
                    <ComBoxStayInformation  @onClick="toggle($event, 'change_date')" :value="gv.timeFormat(rs.reservation?.arrival_time)"
                        valueClass="col " :isAction="true" ></ComBoxStayInformation>
                    <ComBoxStayInformation
                        :value="moment(rs.reservation?.arrival_date).format('dddd')"
                        valueClass="col">
                    </ComBoxStayInformation>
                </div>
                <div class="flex mt-2 gap-2">
                    <ComBoxStayInformation  @onClick="toggle($event, 'change_date')" :isAction="true" title="Departure"
                        :value="moment(rs.reservation?.departure_date).format('DD-MM-yyyy')"
                        valueClass="col-4 " class_action="link_line_action" ></ComBoxStayInformation>
                    <ComBoxStayInformation  @onClick="toggle($event, 'change_date')" :isAction="true" :value="gv.timeFormat(rs.reservation?.departure_time)"
                        valueClass="col" class_action="link_line_action" ></ComBoxStayInformation>
                    <ComBoxStayInformation
                        :value="moment(rs.reservation?.departure_date).format('dddd')"
                        valueClass="col">
                    </ComBoxStayInformation>
                </div>
                <div class="flex mt-2 gap-2">
                    <ComBoxStayInformation title="Nights" :value="(rs.reservation?.room_nights || 0)"
                        valueClass="col-2"></ComBoxStayInformation>
                </div>
                <div class="flex mt-2 gap-2">
                    <ComBoxStayInformation
                        title="Adults"
                        :value="(rs?.reservation?.adult || 0)" valueClass="col-2"
                        >
                    </ComBoxStayInformation>
                   
                    <ComBoxStayInformation
                        title="Children" valueClass="col-2"
                        titleClass="w-5rem leading-10">
                     {{ (rs?.reservation?.child || 0) }}
                    </ComBoxStayInformation>
                </div>
            </div>
        </template>
    </ComReservationStayPanel>
    <OverlayPanel ref="op">
        <ComReservationChangeColorReservation v-if="overLayName=='Change_color'" @onClose="closeOverlay" />
        <ComEditReservationInformation doctype="Reservation" v-else-if="overLayName=='edit_reservation_information'" @onClose="onCloseRef" />
        <ComPopOverChangeReservationDate doctype="Reservation" v-else-if="overLayName=='change_date'" @onClose="onCloseRef" />
    </OverlayPanel>
</template>
<script setup>
import OverlayPanel from 'primevue/overlaypanel';
import {inject, computed, ref} from '@/plugin'
import ComReservationStayPanel from './ComReservationStayPanel.vue';
import ComBoxStayInformation from './ComBoxStayInformation.vue';
import ComEditReservationInformation from './ComEditReservationInformation.vue';
import ComReservationChangeColorReservation from './ComReservationChangeColorReservation.vue';
import ComPopOverChangeReservationDate from './form/ComPopOverChangeReservationDate.vue';
const moment = inject('$moment')
const rs = inject('$reservation');
const gv = inject('$gv');
const overLayName = ref("")
const op = ref();
const roomData = computed(()=>{
    if(rs.reservation && rs.reservation.rooms_data){
        return JSON.parse(rs.reservation.rooms_data)
    }
    return []
})
function getTooltip(){ 
   var html = ''
   var index = 0
   roomData.value.forEach(e => {
        index = index + 1
        if(index > 3){
            html = html + ` ${e.room_type}/${e.room_number ?  e.room_number : ''}<br/>`
        }
        
   });
    return `<div class='tooltip-room-stay'>${html}</div>`
 
}
const toggle = ($event, name) => {
    overLayName.value = name
    op.value.toggle($event);
}
const closeOverlay = ()=>{
    op.value.hide();
}
function onCloseRef(result){
    if(result){
        rs.reservation = result
    }
    op.value.hide()
}
function onChangeDate($event){
    //alert(123)
}


</script>
<style scoped>

</style>