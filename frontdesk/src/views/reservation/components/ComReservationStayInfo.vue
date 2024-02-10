<template>
    <ComReservationStayPanel title="Stay Information" panelClass="block">
        <template #btn>
            <div class="flex items-center justify-content-end">
                <span>{{ stay?.reservationStay?.reservation_color_code || "Select Reservation Color Code" }}</span> 
                <button :style="{background:stay?.reservationStay?.reservation_color}"  @click="toggle($event, 'Change_color')" class="w-2rem ms-2 h-2rem rounded-lg border-2 border-gray-500"></button>
                <span>
                </span>
            </div>
        </template>
        <template #content>
            <div class=""> 
                <div class="flex mt-2 gap-2">
                    <ComBoxStayInformation  @onClick="toggle($event, 'change_reservation_information')" 
                     titleTooltip="Reservation Date" title="Res. Date" 
                     :value="gv.dateFormat(stay.reservationStay?.reservation_date)"
                        valueClass="grow" :isAction="true" ></ComBoxStayInformation>
                </div>
                <div class="flex mt-2 gap-2">
                    <ComBoxStayInformation  @onClick="toggle($event, 'change_reservation_information')" titleTooltip="Reference Number" valueTooltip="Add Reference Number" title="Ref. No"
                         :isSlot="true" :isAction="true" valueClass="col-4">
                        <span>
                            <i v-if="!stay.reservationStay?.reference_number" class="pi pi-pencil"></i>
                            {{ stay.reservationStay?.reference_number ? stay.reservationStay?.reference_number : '...' }}
                        </span>
                    </ComBoxStayInformation>
                    <ComBoxStayInformation  @onClick="toggle($event, 'change_reservation_information')" titleTooltip="Internal Reference Number" valueTooltip="Add Internal Reference Number" title="Int. No"
                     :isAction="true" valueClass="grow" :isSlot="true"
                        titleClass="w-5rem leading-10">
                        <span>
                            <i v-if="!stay.reservationStay?.internal_reference_number" class="pi pi-pencil"></i>
                            {{ stay.reservationStay?.internal_reference_number ? stay.reservationStay?.internal_reference_number : '...' }}
                        </span>
                    </ComBoxStayInformation>
                </div>
                <div v-if="!(stay.reservationStay.reservation_type == 'FIT')" class="flex mt-2 gap-2">
                    <ComBoxStayInformation  @onClick="toggle($event, 'change_reservation_information')"   titleTooltip="Group Name & Group Code" title="Group"  valueClass="grow">
                        <div class="flex align-items-center">
                        <div v-tippy="'Group Color'" class=" px-3 h-1rem py-2 me-3 border-round-lg inline-block group_color_reservation" :style="{background:stay.reservationStay?.group_color}">
                        </div>
                        <button v-tippy="'Group Name & Group Code'" class="link_line_action text-left" v-if="!stay.reservationStay?.group_name && !stay.reservationStay?.group_code" link>
                            <i class="pi pi-pencil"></i>
                            ...
                        </button>
                        <div v-else class="flex gap-2 w-full">
                            <a v-tippy="'Group Name'" v-if="stay.reservationStay?.group_name" class="link_line_action grow text-left overflow-hidden" >{{ stay.reservationStay?.group_name }}</a>
                            <button v-else class="link_line_action grow text-left" >
                                <i class="pi pi-pencil"></i>
                                ...
                            </button>
                            <span>/</span>
                            <a v-tippy="'Group Code'" v-if="stay.reservationStay?.group_code" class="link_line_action grow text-left overflow-hidden" >
                                {{ stay.reservationStay?.group_code }}
                            </a>
                            <button v-else class="link_line_action grow text-left" >
                                <i class="pi pi-pencil"></i>
                                ...  
                            </button>
                        </div>
                    </div>
                    </ComBoxStayInformation>
                </div>
                <div class="flex mt-2 gap-2">
                    <ComBoxStayInformation titleTooltip="Reservation Number" title="Res. No"
                        :value="stay.reservationStay?.reservation" valueClass="grow">
                    </ComBoxStayInformation>
                </div>
                <div class="flex mt-2 gap-2">
                    <ComBoxStayInformation titleTooltip="Reservation Stay Number" title="Res Stay. No"
                        :value="stay.reservationStay?.name" valueClass="grow">
                    </ComBoxStayInformation>
                </div>
                <div class="flex mt-2 gap-2">
                    <ComBoxStayInformation title="Rooms" valueClass="grow">
                        <div v-if="stay.reservationStay?.stays">
                            <div 
                            v-for="(i, index)  in stay?.reservationStay.stays?.slice(0, 3)"
                                :key="index" class="rounded-xl px-2 me-1 bg-gray-edoor inline">
                                <span  v-tippy="i.room_type">{{ i.room_type_alias }}</span>{{ (i.room_number) ? '/' + i.room_number + ' ' : '' }}                               
                            </div>
                            <div v-if="stay.reservationStay?.stays.length>3"  v-tippy="{ value: `<div class='tooltip-room-stay'> ${stay?.reservationStay.stays.slice(3).map(obj => obj.room_type + '/' + (obj.room_number || '')  ).join('\n')}</div>` , escape: true, class: 'max-w-30rem' }" class="rounded-xl px-2 bg-purple-cs w-auto inline">
                                    {{ stay.reservationStay?.stays.length - 3 }}
                                    Mores
                            </div> 
                        </div>
                    </ComBoxStayInformation>
                </div>
                <div class="flex mt-2 gap-2">
                    <ComBoxStayInformation @onClick="onChangeDate($event)" title="Arrival" :value="gv.dateFormat(stay.reservationStay?.arrival_date)" valueClass="col-4 " :isAction="true" ></ComBoxStayInformation>
                    <ComBoxStayInformation  @onClick="onChangeDate($event)" :value="gv.timeFormat(stay.reservationStay?.arrival_time)" valueClass="col " :isAction="true" ></ComBoxStayInformation>
                    <ComBoxStayInformation :value="moment(stay.reservationStay?.arrival_date).format('dddd')" valueClass="col"></ComBoxStayInformation>
                </div>
                <div class="flex mt-2 gap-2">
                    <ComBoxStayInformation 
                        title="Departure"
                        @onClick="onChangeDate($event)"
                        :value="gv.dateFormat(stay.reservationStay?.departure_date)"
                        valueClass="col-4 " :isAction="true" >
                    </ComBoxStayInformation>
                    <ComBoxStayInformation  @onClick="onChangeDate($event)" :value="gv.timeFormat(stay.reservationStay?.departure_time)"
                        valueClass="col color-purple-edoor" :isAction="true" ></ComBoxStayInformation>
                    <ComBoxStayInformation
                        :value="moment(stay.reservationStay?.departure_date).format('dddd')"
                        valueClass="col">
                    </ComBoxStayInformation>
                </div>
                <div class="flex mt-2 gap-2">
                    <ComBoxStayInformation title-class="col-2" title="Nights" :value="(stay.reservationStay?.room_nights || 0)"
                        valueClass="col-2 pr-0"></ComBoxStayInformation>
                </div>

                <div class="flex mt-2 gap-2">               
                    <ComBoxStayInformation 
                        @onClick="toggle($event, 'change_pax')"
                        title="Adults"
                        :value="(stay.reservationStay?.adult || 0)" valueClass="col-2 color-purple-edoor"
                         :isAction="true"></ComBoxStayInformation>
                    <ComBoxStayInformation
                        @onClick="toggle($event, 'change_pax')"
                        title="Children"
                        :value="(stay.reservationStay?.child || 0)" valueClass="col-2 color-purple-edoor"
                        titleClass="w-5rem leading-10" :isAction="true"></ComBoxStayInformation>
                </div>
            </div>
        </template>
    </ComReservationStayPanel>
    <OverlayPanel ref="op">
            <ComReservationStayChangeColorReservation v-if="overLayName=='Change_color'" @onClose="closeOverlay" />
            <ComChangePax v-else-if="overLayName=='change_pax'" @onClose="closeOverlay" />
            <ComEditReservationInformation doctype="Reservation Stay" v-else-if="overLayName=='change_reservation_information'" @onClose="onCloseRef" />
            <ComReservationStayChangeArrivalDepartureDate v-else-if="overLayName == 'change_date'" @onClose="closeOverlay"/>
    </OverlayPanel>
</template>
<script setup>
import OverlayPanel from 'primevue/overlaypanel';
import {inject} from '@/plugin'
import { ref } from "vue";
// import ColorPicker from 'primevue/colorpicker';
import ComReservationStayPanel from './ComReservationStayPanel.vue';
import ComBoxStayInformation from './ComBoxStayInformation.vue';
import ComChangePax from './ComChangePax.vue';
import ComEditReservationInformation from './ComEditReservationInformation.vue';
import ComReservationStayChangeColorReservation from './ComReservationStayChangeColorReservation.vue';
import ComReservationStayChangeArrivalDepartureDate from './ComReservationStayChangeArrivalDepartureDate.vue';
const moment = inject('$moment')
const stay = inject('$reservation_stay');
const gv = inject('$gv');
const overLayName = ref("")
const op = ref();
// const color = ref()
const toggle = ($event, name) => {
    overLayName.value = name
    op.value.toggle($event);
}
const closeOverlay = ()=>{
    op.value.hide();
}
function onChangeDate($event){

    if(stay.reservationStay.stays.length > 1){
        gv.toast("warn","This reservation stay has multiple rooms. Please change in room stay.")
        return
    }
    toggle($event, 'change_date')
}
function onCloseRef(result){
    if(result){
        stay.reservationStay = result
    } 
    op.value.hide()
}

</script>
<style scoped>
.p-tooltip{
    max-width: 25rem !important;
}
</style>