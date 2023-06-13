<template>
    <ComReservationStayPanel title="Stay Information">
        <template #content>
            <div>
                <div class="flex mt-2 gap-2">
                    <ComBoxStayInformation tooltip="Reservation Date" title="Res. Date" :value="gv.dateFormat(rs.reservation?.reservation_date)"
                        valueClass="grow"></ComBoxStayInformation>
                </div>
                <div class="flex mt-2 gap-2">
                    <ComBoxStayInformation tooltip="Reference Number" title="Ref. No"
                        :value="rs.reservation?.reference_number" valueClass="grow">
                    </ComBoxStayInformation>
                    <ComBoxStayInformation tooltip="Internal Reference Number" title="Int. No"
                        :value="rs.reservation?.internal_reference_number" valueClass="grow"
                        titleClass="w-4rem"></ComBoxStayInformation>
                </div>
                <div class="flex mt-2 gap-2">
                    <ComBoxStayInformation tooltip="Booking Number" title="Book. No"
                        :value="rs.reservation?.reservation" valueClass="grow">
                    </ComBoxStayInformation>
                </div>
                <div class="flex mt-2 gap-2">
                    <ComBoxStayInformation tooltip="Reservation Number" title="Res. No"
                        :value="rs.reservation?.name" valueClass="grow">
                    </ComBoxStayInformation>
                </div>
                <div class="flex mt-2 gap-2">
                    <ComBoxStayInformation title="Rooms" valueClass="grow">
                        <div v-if="rs && rs?.reservationStays">
                            <span v-for="(i, index) in rs.reservationStays.slice(0, 2)"
                                :key="index" class="rounded-xl px-2 me-1 bg-gray-edoor">
                                    <span>{{ i?.rooms }}</span>
                            </span>
                            <span v-if="rs.reservationStays.length > 2">
                                ... <span class="">more</span>
                            </span>
                        </div>
                    </ComBoxStayInformation>
                </div>
                <div class="flex mt-2 gap-2">
                    <ComBoxStayInformation title="Arraval"                          
                        :value="moment(rs.reservation?.arrival_date).format('DD-MM-yyyy')"
                        valueClass="col-4 " class_action="link_line_action" ></ComBoxStayInformation>
                    <ComBoxStayInformation :value="rs.reservation?.arrival_time"
                        valueClass="col " class_action="link_line_action" ></ComBoxStayInformation>
                    <ComBoxStayInformation
                        :value="moment(rs.reservation?.arrival_date).format('dddd')"
                        valueClass="col">
                    </ComBoxStayInformation>
                </div>
                <div class="flex mt-2 gap-2">
                    <ComBoxStayInformation title="Departure"
                        :value="moment(rs.reservation?.departure_date).format('DD-MM-yyyy')"
                        valueClass="col-4 " class_action="link_line_action" ></ComBoxStayInformation>
                    <ComBoxStayInformation :value="rs.reservation?.departure_time"
                        valueClass="col color-purple-edoor" class_action="link_line_action" ></ComBoxStayInformation>
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
                        title="Adult"
                        :value="rs.reservation?.adult" valueClass="col-2 color-purple-edoor"
                        titleClass="w-6rem" class_action="link_line_action"></ComBoxStayInformation>
                    <ComBoxStayInformation
                        @onClick="toggle($event, 'change_pax')"
                        title="Children"
                        :value="rs.reservation?.child" valueClass="col-2 color-purple-edoor"
                        titleClass="w-5rem" class_action="link_line_action"></ComBoxStayInformation>
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