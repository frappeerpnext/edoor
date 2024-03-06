
<template>
    <div class="flex items-center">
        <div class="flex">
            <span @click="OnViewReservation">
                <ComTagReservation :title="$t('RES') + '#:' " :value="rs?.reservation?.name" class="link_line_action w-auto hidden lg:inline-block">
                    <span class="number_action_line inline-block">
                        {{ rs?.reservationStayNames.length }} </span>
                </ComTagReservation>
            </span>
            <ComTagReservation :title="$t('RES STAY') + '#:'" :value="rs.reservationStay?.name" class="bg-card-info p-1px hidden lg:inline-block">
            </ComTagReservation>
            <ComTagReservation :title="$t('ROOMS') + '#:'" class="bg-card-info p-1px hidden lg:inline-block" v-if="rs.reservationStay">
                <div class="inline" v-if="rs.reservationStay?.stays">
                    
                    <div class="inline" v-for="(i, index)  in rs.reservationStay?.stays?.slice(0, 3)" :key="index">
                        <span v-if="index != 0"> , </span>
                        <span v-tippy ="i.room_type">{{ i.room_type_alias }}</span>{{ (i.room_number) ? '/' +
                            i.room_number : '' }}
                    </div>
                    <div v-if="rs.reservationStay?.stays.length > 3"
                        v-tippy="{ value: `<div class='tooltip-room-stay'> ${rs?.reservationStay.stays.slice(3).map(obj => obj.room_type + '/' + obj.room_number).join('\n')}</div>`, escape: true, class: 'max-w-30rem' }"
                        class="bg-gray-400 rounded-xl px-2 cursor-pointer ms-2 inline">
                        {{ rs.reservationStay?.stays.length - 3 }}
                        {{ $t('Mores') }}
                    </div>
                </div>
            </ComTagReservation>
            <div  v-tippy="$t('Allow Post To City Ledger')" v-if="rs.reservationStay && rs.reservationStay?.allow_post_to_city_ledger"
                class="flex justify-center items-center px-2 rounded-lg me-2 bg-card-info p-1px">
                <ComIcon  icon="IconBillToCompany" style="height:15px;width:15px;" ></ComIcon>
            </div>
            <div  v-tippy="$t('Paid By Master Room')" v-if="!(rs?.reservationStay?.is_master) && rs?.reservationStay?.paid_by_master_room"
                class="flex justify-center items-center px-2 rounded-lg me-2 bg-card-info p-1px">
                <ComIcon  icon="BilltoMasterRoom" style="height:15px;" ></ComIcon>
            </div>
            <div  v-tippy="$t('Split Room')" class="flex justify-center items-center px-2 rounded-lg me-2 bg-card-info p-1px" v-if="rs.reservationStay?.stays?.length >= 2" >
                <ComIcon  icon="iconSplit" style="height:15px;" ></ComIcon>
                
            </div>
            <div  v-tippy="$t('Master Room')" v-if="rs.reservationStay && rs.reservationStay.is_master"
                class="flex justify-center items-center px-2 rounded-lg me-2 bg-purple-100 p-1px">
                <ComIcon style="height: 14px;" icon="iconCrown" />
            </div>
        <div v-if="rs.reservationStay?.reservation_type == 'FIT'" v-tippy="rs.reservationStay?.reservation_type !== 'FIT' ? $t('Free Independent Traveler') : $t('Free Independent Traveler')"
            class="px-2 rounded-lg me-2 text-white p-1px bg-teal-500 flex items-center justify-center">
            <span>
            <ComIcon style="height: 15px;" class="m-auto" icon="userFitWhite" />
            </span>
        </div>
        <div v-else="rs.reservationStay?.reservation_type == 'GIT'" v-tippy="rs.reservationStay?.reservation_type !== 'GIT' ? $t('Group Inclusive Tour') : $t('Group Inclusive Tour')"
        class="px-2 rounded-lg me-2 text-white p-1px bg-yellow-500 flex items-center justify-center">
            <span>
            <ComIcon style="height: 15px;" class="m-auto" icon="userGroupWhite" />
            </span>
        </div>
            <span class="px-2 rounded-lg me-2 text-white p-1px" :style="{ background: rs.reservationStay?.status_color }" v-if="rs.reservationStay && rs.reservationStay?.reservation_status">
                {{$t(rs.reservationStay?.reservation_status)  }}
                
            </span>

        </div>
    </div>
  
</template>
<script setup>
import { inject, useRouter,useDialog } from '@/plugin'
import ComTagReservation from '@/views/reservation/components/ComTagReservation.vue';
import ReservationDetail from "@/views/reservation/ReservationDetail.vue"
const rs = inject('$reservation_stay');
const dialogRef = inject("dialogRef");
const router = useRouter()
const dialog = useDialog()
import {i18n} from '@/i18n';
const { t: $t } = i18n.global;
const OnViewReservation = () => {
    if (rs.is_page) {
        router.push({ name: 'ReservationDetail', params: { name: rs.reservation.name } })
    } else {
    
        showReservationDetail(rs.reservation.name)
    }
}
function showReservationDetail(name) {
    if (!window.has_reservation_detail_opened){ 
    
    const open = dialog.open(ReservationDetail, {
        data: {
            name: name
        },
        props: {
            header: 'Reservation Detail',
            contentClass: 'ex-pedd',
            style: {
                width: '80vw',
            },
            maximizable: true,
            modal: true,
            closeOnEscape: false,
            position:"top",
            breakpoints:{
                '960px': '80vw',
                '640px': '100vw'
            },
        }
    });
    }
    dialogRef.value.close()
}
</script>

  