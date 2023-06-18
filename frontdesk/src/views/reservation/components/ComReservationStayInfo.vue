<template>
    <ComReservationStayPanel title="Stay Information">
        <template #btn>
            <div class="flex items-center">
                <span> Res Color </span>
               <button @click="" class="w-2rem ms-2 h-2rem bg-blue-500 rounded-lg" link></button> 
            </div>
        </template>
        <template #content>
            <div class="">
                <div class="flex mt-2 gap-2">
                    <ComBoxStayInformation title-class="col-2 pr-0" titleTooltip="Reservation Date" title="Res. Date" :value="gv.dateFormat(stay?.reservation_date)"
                        valueClass="grow"></ComBoxStayInformation>
                </div>
                <div class="flex mt-2 gap-2">
                    <ComBoxStayInformation title-class="col-2 pr-0" titleTooltip="Reference Number" valueTooltip="Add Reference Number" title="Ref. No"
                        :value="stay.reservationStay?.reference_number" :isAction="true" valueClass="col-4">
                    </ComBoxStayInformation>
                    <ComBoxStayInformation titleTooltip="Internal Reference Number" valueTooltip="Add Internal Reference Number" title="Int. No"
                        :value="stay.reservationStay?.internal_reference_number" :isAction="true" valueClass="grow"
                        titleClass="w-5rem">
                    </ComBoxStayInformation>
                </div>
                <div class="flex mt-2 gap-2">
                    <ComBoxStayInformation title-class="col-2 pr-0"  titleTooltip="Group Name & Group Code" title="Group"  valueClass="grow">
                        <span class="link_line_action" v-if="!stay.reservationStay?.reference_number && !stay.reservationStay?.internal_reference_number">
                            <i class="pi pi-pencil"></i>
                            ...
                        </span>
                        <div v-else class="flex gap-2">
                            <span v-if="stay.reservationStay?.reference_number" class="link_line_action grow" >{{ stay.reservationStay?.reference_number }}</span>
                            <span v-else class="link_line_action grow" >
                                <i class="pi pi-pencil"></i>
                                ...
                            </span>
                            <span>/</span>
                            <span v-if="stay.reservationStay?.internal_reference_number" class="link_line_action grow" >
                                {{ stay.reservationStay?.internal_reference_number }}
                            </span>
                            <span v-else class="link_line_action grow" >
                                <i class="pi pi-pencil"></i>
                            ...  
                            </span>
                        </div>
                    </ComBoxStayInformation>
                </div>
                <div class="flex mt-2 gap-2">
                    <ComBoxStayInformation title-class="col-2 pr-0" titleTooltip="Reservation Number" title="Res. No"
                        :value="stay.reservationStay?.reservation" valueClass="grow">
                    </ComBoxStayInformation>
                </div>
                <div class="flex mt-2 gap-2">
                    <ComBoxStayInformation title-class="col-2 pr-0" titleTooltip="Reservation Stay Number" title="Res Stay. No"
                        :value="stay.reservationStay?.name" valueClass="grow">
                    </ComBoxStayInformation>
                </div>
                <div class="flex mt-2 gap-2">
                    <ComBoxStayInformation title-class="col-2 pr-0" title="Rooms" valueClass="grow">
                        <div v-if="stay.reservationStay?.rooms && stay.reservationStay?.rooms.split(',').length > 3">
                            <span
                                v-for="value_room_stay in stay.reservationStay?.rooms.split(',').slice(0, 3)"
                                :key="value_room_stay" class="rounded-xl px-2 me-1 bg-gray-edoor">
                                {{ value_room_stay }}
                            </span>
                            <span class="rounded-xl px-2 bg-purple-cs link_line_action">
                                {{ stay.reservationStay?.rooms.split(",").length }}
                                more
                            </span>
                        </div>
                        <span class="bg-gray-edoor rounded-xl px-2" v-else>
                            {{ stay.reservationStay?.room_type_alias }}{{ (stay.reservationStay?.rooms) ? '/'+stay.reservationStay?.rooms : '' }}
                        </span>
                    </ComBoxStayInformation>
                </div>
                <div class="flex mt-2 gap-2">
                    <ComBoxStayInformation title-class="col-2 pr-0" title="Arrival"                          
                        :value="gv.dateFormat(stay.reservationStay?.arrival_date)"
                        valueClass="col-4 " :isAction="true" ></ComBoxStayInformation>
                    <ComBoxStayInformation :value="stay.reservationStay?.arrival_time"
                        valueClass="col " :isAction="true" ></ComBoxStayInformation>
                    <ComBoxStayInformation
                        :value="moment(stay.reservationStay?.arrival_date).format('dddd')"
                        valueClass="col">
                    </ComBoxStayInformation>
                </div>
                <div class="flex mt-2 gap-2">
                    <ComBoxStayInformation title-class="col-2 pr-0" title="Departure"
                        :value="gv.dateFormat(stay.reservationStay?.departure_date)"
                        valueClass="col-4 " :isAction="true" ></ComBoxStayInformation>
                    <ComBoxStayInformation :value="stay.reservationStay?.departure_time"
                        valueClass="col color-purple-edoor" :isAction="true" ></ComBoxStayInformation>
                    <ComBoxStayInformation
                        :value="moment(stay.reservationStay?.departure_date).format('dddd')"
                        valueClass="col">
                    </ComBoxStayInformation>
                </div>
                <div class="flex mt-2 gap-2">
                    <ComBoxStayInformation title-class="col-2" title="Nights" :value="stay.reservationStay?.room_nights"
                        valueClass="col-2 pr-0"></ComBoxStayInformation>
                </div>

                <div class="flex mt-2 gap-2">               
                    <ComBoxStayInformation 
                        @onClick="toggle($event, 'change_pax')"
                        title="Adult"
                        :value="stay.reservationStay?.adult" valueClass="col-2 color-purple-edoor"
                        titleClass="col-2 pr-0" :isAction="true"></ComBoxStayInformation>
                    <ComBoxStayInformation
                        @onClick="toggle($event, 'change_pax')"
                        title="Children"
                        :value="stay.reservationStay?.child" valueClass="col-2 color-purple-edoor"
                        titleClass="w-5rem" :isAction="true"></ComBoxStayInformation>
                </div>
            </div>
        </template>

     

    </ComReservationStayPanel>
    
    <OverlayPanel ref="op">

            <ComChangePax v-if="overLayName=='change_pax'" @onClose="closeOverlay" />
    </OverlayPanel>
</template>
<script setup>
import OverlayPanel from 'primevue/overlaypanel';
import {inject} from '@/plugin'
import { ref } from "vue";

import ComReservationStayPanel from './ComReservationStayPanel.vue';
import ComBoxStayInformation from './ComBoxStayInformation.vue';
import ComChangePax from './ComChangePax.vue';

const moment = inject('$moment')
const stay = inject('$reservation_stay');
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