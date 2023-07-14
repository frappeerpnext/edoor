
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
            <ComTagReservation title="ROOMS#:" class="bg-card-info p-1px" v-if="rs.reservationStay">
                <div class="inline" v-if="rs.reservationStay?.stays">
                    <div class="inline" v-for="(i, index)  in rs.reservationStay?.stays?.slice(0, 3)" :key="index">
                        <span v-if="index != 0"> , </span>
                        <span v-tooltip.top="i.room_type">{{ i.room_type_alias }}</span>{{ (i.room_number) ? '/' +
                            i.room_number : '' }}
                    </div>
                    <div v-if="rs.reservationStay?.stays.length > 3"
                        v-tooltip.top="{ value: `<div class='tooltip-room-stay'> ${rs?.reservationStay.stays.slice(3).map(obj => obj.room_type + '/' + obj.room_number).join('\n')}</div>`, escape: true, class: 'max-w-30rem' }"
                        class="bg-gray-400 rounded-xl px-2 cursor-pointer ms-2 inline">
                        {{ rs.reservationStay?.stays.length - 3 }}
                        Mores
                    </div>
                </div>
            </ComTagReservation>
            <div v-tooltip.top="'Master Room'" v-if="rs.reservationStay.is_master"
                class="flex justify-center items-center px-2 rounded-lg me-2 bg-purple-100 p-1px">
                <ComIcon style="height: 14px;" icon="iconCrown" />
            </div>
            <ComReservationStatus v-if="rs.reservationStay && rs.reservationStay?.reservation_status"
                :status-name="rs.reservationStay?.reservation_status" />
            <span v-if="rs.reservationStay?.reservation_type == 'FIT'"
                class="px-2 rounded-lg me-2 text-white p-1px bg-teal-500">
                <i class="pi pi-user" style="font-size: 10px;"></i>
                {{ rs.reservationStay?.reservation_type }}</span>
            <span v-else class="px-2 rounded-lg me-2 text-white p-1px bg-yellow-500">
                <i class="pi pi-users"></i>
                {{ rs.reservationStay?.reservation_type }}</span>

        </div>
    </div>
</template>
<script setup>
import { inject, useRouter } from '@/plugin'
import ComTagReservation from '@/views/reservation/components/ComTagReservation.vue';
const rs = inject('$reservation_stay');
const dialogRef = inject("dialogRef");
const router = useRouter()
const OnViewReservation = () => {
    if (rs.is_page) {

        router.push({ name: 'ReservationDetail', params: { name: rs.reservation.name } })
    } else {
        dialogRef.value.close({ action: "view_reservation_detail", reservation: rs.reservation.name });
    }

}
</script>

  