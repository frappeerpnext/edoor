
<template>
    <div class="flex items-center">
        <div class="flex">
            <span @click="OnViewReservation">
                <ComTagReservation title="RES#:" :value="rs?.reservation?.name" class="link_line_action w-auto">
                    <span class="number_action_line inline-block">
                        {{ rs?.reservationStayNames.length }} </span>
                </ComTagReservation>
            </span>
            <ComTagReservation title="RES STAY#:" :value="rs.reservationStay?.name" class="bg-card-info p-1px">
            </ComTagReservation>
            <ComTagReservation title="ROOMS#:" class="bg-card-info p-1px"
                v-if="rs.reservationStay">
                {{ rs.reservationStay?.length }}
                <span v-if="rs.reservationStay.rooms && rs.reservationStay?.length > 2">
                    <span v-for="(i, index)  in rs.reservationStay?.rooms.slice(0, 2)"
                    :key="index">
                        {{ rs.reservationStay?.room_type_alias }}{{ (i) ? '/' + i : '' }}
                    </span>
                    <span>
                        {{ rs.reservationStay?.rooms.length }}More
                    </span>
                </span>
                <span v-else>
                    {{ rs.reservationStay?.room_type_alias }}{{ ( rs.reservationStay?.rooms) ? '/' +  rs.reservationStay?.rooms : '' }}
                </span>
            </ComTagReservation>
            <div v-tooltip.top="'Master Room'" v-if="rs.reservationStay.is_master" class="flex justify-center items-center px-2 rounded-lg me-2 bg-purple-100 p-1px"> 
                <ComIcon style="height: 14px;" icon="iconCrown"/>
            </div>
            <ComReservationStatus v-if="rs.reservationStay && rs.reservationStay?.reservation_status"
                :status-name="rs.reservationStay?.reservation_status" />
            <span class="px-2 rounded-lg me-2 text-white p-1px" :style="{ background: rs.reservationStay?.status_color }">{{
                rs.reservationStay?.reservation_type }}</span>
            
        </div>
    </div>
</template>
<script setup>
import { inject } from '@/plugin'
import ComTagReservation from '@/views/reservation/components/ComTagReservation.vue';
const rs = inject('$reservation_stay');
const dialogRef = inject("dialogRef");
const OnViewReservation = () => {
    dialogRef.value.close({ action: "view_reservation_detail", reservation: rs.reservation.name });
}
</script>

  