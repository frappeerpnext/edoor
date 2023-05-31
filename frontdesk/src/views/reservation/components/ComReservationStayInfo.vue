<template>
    <ComReservationStayPanel title="Stay Information">
        <template #content>
            <div>
                <div class="flex mt-2 gap-2 ">
                    <ComBoxStayInformation tooltip="Reservation Date" title="Res. Date" :value="moment(reservationStay?.reservation_date).format('DD-MM-yyyy')"
                        valueClass="grow"></ComBoxStayInformation>
                </div>
                <div class="flex mt-2 gap-2">
                    <ComBoxStayInformation tooltip="Reference Number" title="Ref. No"
                        :value="reservationStay?.reference_number" valueClass="grow">
                    </ComBoxStayInformation>
                    <ComBoxStayInformation tooltip="Internal Reference Number" title="Int. No"
                        :value="reservationStay?.internal_reference_number" valueClass="grow"
                        titleClass="w-4rem"></ComBoxStayInformation>
                </div>
                <div class="flex mt-2 gap-2">
                    <ComBoxStayInformation tooltip="Booking Number" title="Book. No"
                        :value="reservationStay?.reservation" valueClass="grow">
                    </ComBoxStayInformation>
                </div>
                <div class="flex mt-2 gap-2">
                    <ComBoxStayInformation tooltip="Reservation Number" title="Res. No"
                        :value="reservationStay?.name" valueClass="grow">
                    </ComBoxStayInformation>
                </div>
                <div class="flex mt-2 gap-2">
                    <ComBoxStayInformation title="Rooms" valueClass="grow">
                        <div v-if="reservationStay.rooms && reservationStay.rooms.split(',').length > 3">
                            <span
                                v-for="value_room_stay in reservationStay?.rooms.split(',').slice(0, 3)"
                                :key="value_room_stay" class="rounded-xl px-2 me-1 bg-gray-edoor">
                                {{ value_room_stay }}
                            </span>
                            <span class="rounded-xl px-2 bg-purple-cs link_line_action">
                                {{ reservationStay?.rooms.split(",").length }}
                                more
                            </span>
                        </div>
                        <span class="bg-gray-edoor rounded-xl px-2" v-else>
                            {{ reservationStay?.rooms }}
                        </span>
                    </ComBoxStayInformation>
                </div>
                <div class="flex mt-2 gap-2">
                    <ComBoxStayInformation title="Arraval"
                        :value="moment(reservationStay?.arrival_date).format('DD-MM-yyyy')"
                        valueClass="col-4 " class_action="link_line_action" ></ComBoxStayInformation>
                    <ComBoxStayInformation :value="reservationStay?.arrival_time"
                        valueClass="col " class_action="link_line_action" ></ComBoxStayInformation>
                    <ComBoxStayInformation
                        :value="moment(reservationStay?.arrival_date).format('dddd')"
                        valueClass="col">
                    </ComBoxStayInformation>
                </div>
                <div class="flex mt-2 gap-2">
                    <ComBoxStayInformation title="Departure"
                        :value="moment(reservationStay?.departure_date).format('DD-MM-yyyy')"
                        valueClass="col-4 " class_action="link_line_action" ></ComBoxStayInformation>
                    <ComBoxStayInformation :value="reservationStay?.departure_time"
                        valueClass="col color-purple-edoor" class_action="link_line_action" ></ComBoxStayInformation>
                    <ComBoxStayInformation
                        :value="moment(reservationStay?.departure_date).format('dddd')"
                        valueClass="col">
                    </ComBoxStayInformation>
                </div>
                <div class="flex mt-2 gap-2">
                    <ComBoxStayInformation title="Nights" :value="reservationStay?.room_nights"
                        valueClass="col-2"></ComBoxStayInformation>
                </div>
                <div class="flex mt-2 gap-2">
                    <ComBoxStayInformation title="Adults" :value="reservationStay?.room_nights"
                        valueClass="col-2 color-purple-edoor" class_action="link_line_action"></ComBoxStayInformation>
                    <ComBoxStayInformation title="Children"
                        :value="reservationStay?.room_nights" valueClass="col-2 color-purple-edoor"
                        titleClass="w-5rem" class_action="link_line_action"></ComBoxStayInformation>
                </div>
            </div>
        </template>
    </ComReservationStayPanel>
</template>
<script setup>
import ComReservationStayPanel from './ComReservationStayPanel.vue';
import ComBoxStayInformation from './ComBoxStayInformation.vue';
import {inject} from 'vue'
const moment = inject('$moment')
 const props = defineProps({
    reservationStay: {
        type: Object,
        default: {}
    }
 })
</script>
<style scoped>
    .p-tooltip{
        color: red;
    }
</style>