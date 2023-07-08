<template>
    <ComReservationStayPanel title="Stay Information">
        <template #btn>
            <div class="flex items-center">
                <span> Res Color </span> 
                <button :style="{background:rs?.reservation?.reservation_color}"  @click="toggle($event, 'Change_color')" class="w-2rem ms-2 h-2rem rounded-lg"></button>   
            </div>
        </template>
        <template #content>
            <div>
                <div class="flex mt-2 gap-2">
                    <ComBoxStayInformation :isAction="true" titleTooltip="Reservation Date" title="Res. Date" :value="gv.dateFormat(rs.reservation?.reservation_date)"
                        valueClass="grow"></ComBoxStayInformation>
                </div>
                <div class="flex mt-2 gap-2">
                    <ComBoxStayInformation :isAction="true" titleTooltip="Reference Number" title="Ref. No"
                        :value="rs.reservation?.reference_number" valueClass="grow">
                    </ComBoxStayInformation>
                    <ComBoxStayInformation :isAction="true" titleTooltip="Internal Reference Number" title="Int. No"
                        :value="rs.reservation?.internal_reference_number" valueClass="grow"
                        titleClass="w-4rem"></ComBoxStayInformation>
                </div>
                <div class="flex mt-2 gap-2">
                    <ComBoxStayInformation title="Group"  valueClass="grow">
                        <span class="link_line_action" v-if="!rs.reservation?.reference_number && !rs.reservation?.internal_reference_number">
                            <i class="pi pi-pencil"></i>
                            ...
                        </span>
                        <div v-else class="flex gap-2">
                            <span v-if="rs.reservation?.reference_number" class="link_line_action grow" >{{ rs.reservation?.reference_number }}</span>
                            <span v-else class="link_line_action grow" >
                                <i class="pi pi-pencil"></i>
                                ...
                            </span>
                            <span>/</span>
                            <span v-if="rs.reservation?.internal_reference_number" class="link_line_action grow" >
                                {{ rs.reservation?.internal_reference_number }}
                            </span>
                            <span v-else class="link_line_action grow" >
                                <i class="pi pi-pencil"></i>
                            ...  
                            </span>
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
                            <div 
                            v-for="(i, index)  in rs?.reservationStays[0]?.room_type_alias?.split(',').slice(0, 3)"
                                :key="index" class="rounded-xl px-2 me-1 bg-gray-edoor inline">
                                <span v-tooltip.top="rs?.reservationStays[0]?.room_types?.split(',')[index]">{{ i }}</span>/{{ rs?.reservationStays[0]?.rooms?.split(',')[index] }}
                            </div>
                            <div v-if="rs?.reservationStays[0]?.room_type_alias?.split(',').length>3"
                                v-tooltip.top="{ value: `<div class='tooltip-room-stay'> ${rs?.reservationStays?.map(stay => {
                                return stay.room_types.split(',').slice(3).map((type, i) => `${type}/${(stay.rooms.split(',').slice(3))[i]}`).join('\n')
                                  })}</div>` , escape: true, class: 'max-w-30rem' }"
                                 class="rounded-xl px-2 bg-purple-cs w-auto inline">
                                    {{ rs?.reservationStays[0]?.room_type_alias?.split(',').length - 3 }}
                                    Mores
                            </div> 
                        </div>
                    </ComBoxStayInformation>
                </div>
                <div class="flex mt-2 gap-2">
                    <ComBoxStayInformation :isAction="true" title="Arrival"                    
                        :value="moment(rs.reservation?.arrival_date).format('DD-MM-yyyy')"
                        valueClass="col-4 " ></ComBoxStayInformation>
                    <ComBoxStayInformation :value="rs.reservation?.arrival_time"
                        valueClass="col " :isAction="true" ></ComBoxStayInformation>
                    <ComBoxStayInformation
                        :value="moment(rs.reservation?.arrival_date).format('dddd')"
                        valueClass="col">
                    </ComBoxStayInformation>
                </div>
                <div class="flex mt-2 gap-2">
                    <ComBoxStayInformation :isAction="true" title="Departure"
                        :value="moment(rs.reservation?.departure_date).format('DD-MM-yyyy')"
                        valueClass="col-4 " class_action="link_line_action" ></ComBoxStayInformation>
                    <ComBoxStayInformation :isAction="true" :value="rs.reservation?.departure_time"
                        valueClass="col" class_action="link_line_action" ></ComBoxStayInformation>
                    <ComBoxStayInformation
                        :value="moment(rs.reservation?.departure_date).format('dddd')"
                        valueClass="col">
                    </ComBoxStayInformation>
                </div>
                <div class="flex mt-2 gap-2">
                    <ComBoxStayInformation title="Nights" :value="rs.reservation?.room_nights"
                        valueClass="col-2"></ComBoxStayInformation>
                </div>
                <div class="flex mt-2 gap-2">
                    <ComBoxStayInformation 
                        @onClick="toggle($event, 'change_pax')"
                        :isAction="true"
                        title="Adult"
                        :value="rs?.reservation?.adult" valueClass="col-2"
                        >
                    </ComBoxStayInformation>
                    <ComBoxStayInformation
                        @onClick="toggle($event, 'change_pax')"
                        :isAction="true"
                        title="Children"
                        :value="rs?.reservation?.child" valueClass="col-2"
                        titleClass="w-5rem"></ComBoxStayInformation>
                </div>
            </div>
        </template>
    </ComReservationStayPanel>
    <OverlayPanel ref="op">
        <ComReservationChangeColorReservation v-if="overLayName=='Change_color'" @onClose="closeOverlay" />
        <ComChangePax v-if="overLayName=='change_pax'" @onClose="closeOverlay" />
    </OverlayPanel>
</template>
<script setup>
import OverlayPanel from 'primevue/overlaypanel';
import {inject} from '@/plugin'
import { ref } from "vue";
import ComReservationStayPanel from './ComReservationStayPanel.vue';
import ComBoxStayInformation from './ComBoxStayInformation.vue';
import ComReservationChangeColorReservation from './ComReservationChangeColorReservation.vue';
import ComChangePax from './ComChangePax.vue';

const moment = inject('$moment')
const rs = inject('$reservation');
const gv = inject('$gv');
const overLayName = ref("")
const op = ref();
const toggle = ($event, name) => {
    overLayName.value = name
    op.value.toggle($event);
}
const closeOverlay = ()=>{
    op.value.hide();
}




</script>
<style scoped>

</style>