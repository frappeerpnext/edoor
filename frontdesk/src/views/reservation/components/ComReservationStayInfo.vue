<template>
    <ComReservationStayPanel title="Stay Information">
        <template #content>
          
            <div>
                <div class="flex mt-2 gap-2">
                    <ComBoxStayInformation tooltip="Reservation Date" title="Res. Date" :value="gv.dateFormat(stay.reservationStay?.reservation_date)"
                        valueClass="grow"></ComBoxStayInformation>
                </div>
                <div class="flex mt-2 gap-2">
                    <ComBoxStayInformation tooltip="Reference Number" title="Ref. No"
                        :value="stay.reservationStay?.reference_number" valueClass="grow">
                    </ComBoxStayInformation>
                    <ComBoxStayInformation tooltip="Internal Reference Number" title="Int. No"
                        :value="stay.reservationStay?.internal_reference_number" valueClass="grow"
                        titleClass="w-4rem"></ComBoxStayInformation>
                </div>
                <div class="flex mt-2 gap-2">
                    <ComBoxStayInformation tooltip="Booking Number" title="Book. No"
                        :value="stay.reservationStay?.reservation" valueClass="grow">
                    </ComBoxStayInformation>
                </div>
                <div class="flex mt-2 gap-2">
                    <ComBoxStayInformation tooltip="Reservation Number" title="Res. No"
                        :value="stay.reservationStay?.name" valueClass="grow">
                    </ComBoxStayInformation>
                </div>
                <div class="flex mt-2 gap-2">
                    <ComBoxStayInformation title="Rooms" valueClass="grow">
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
                            {{ stay.reservationStay?.rooms }}
                        </span>
                    </ComBoxStayInformation>
                </div>
                <div class="flex mt-2 gap-2">
                    <ComBoxStayInformation title="Arraval"
                        :value="moment(stay.reservationStay?.arrival_date).format('DD-MM-yyyy')"
                        valueClass="col-4 " class_action="link_line_action" ></ComBoxStayInformation>
                    <ComBoxStayInformation :value="stay.reservationStay?.arrival_time"
                        valueClass="col " class_action="link_line_action" ></ComBoxStayInformation>
                    <ComBoxStayInformation
                        :value="moment(stay.reservationStay?.arrival_date).format('dddd')"
                        valueClass="col">
                    </ComBoxStayInformation>
                </div>
                <div class="flex mt-2 gap-2">
                    <ComBoxStayInformation title="Departure"
                        :value="moment(stay.reservationStay?.departure_date).format('DD-MM-yyyy')"
                        valueClass="col-4 " class_action="link_line_action" ></ComBoxStayInformation>
                    <ComBoxStayInformation :value="stay.reservationStay?.departure_time"
                        valueClass="col color-purple-edoor" class_action="link_line_action" ></ComBoxStayInformation>
                    <ComBoxStayInformation
                        :value="moment(stay.reservationStay?.departure_date).format('dddd')"
                        valueClass="col">
                    </ComBoxStayInformation>
                </div>
                <div class="flex mt-2 gap-2">
                    <ComBoxStayInformation title="Nights" :value="stay.reservationStay?.room_nights"
                        valueClass="col-2"></ComBoxStayInformation>
                </div>

                <div class="flex mt-2 gap-2">
                   
                    <ComChangePax/>
                    <ComBoxStayInformation title="Children"
                        :value="stay.reservationStay?.child" valueClass="col-2 color-purple-edoor"
                        titleClass="w-5rem" class_action="link_line_action"></ComBoxStayInformation>
                </div>
            </div>
        </template>

     

    </ComReservationStayPanel>
 
   
</template>
<script setup>
import OverlayPanel from 'primevue/overlaypanel';
import {inject} from '@/plugin'
import { ref } from "vue";


import ComReservationStayPanel from './ComReservationStayPanel.vue';
import ComBoxStayInformation from './ComBoxStayInformation.vue';
import ComChangePax from './ComChangePax.vue';

const moment = inject('$moment')
const stay = inject('$reservation');
const gv = inject('$gv');



</script>
<style scoped>

</style>