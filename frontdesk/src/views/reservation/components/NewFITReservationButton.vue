<template>
    <Button  v-shortkey="['ctrl', 'f']" @shortkey="onClick()"  v-tippy="$t('New Reservation')" @click="onClick" :label="$t('New reservation')" class="d-bg-set btn-inner-set-icon border-none">
        <img class="mr-2" :src="iconEdoorNewReservation">
        {{ $t('New Reservation') }}
        
    </Button>
</template>
<script setup>
import iconEdoorNewReservation from '../../../assets/svg/icon-add-reservation.svg'
import { useDialog } from 'primevue/usedialog';
import NewReservation from '@/views/reservation/NewReservation.vue';
import ReservationDetail from '@/views/reservation/ReservationDetail.vue';
import {i18n} from '@/i18n';
const { t: $t } = i18n.global;
const dialog = useDialog();
function onClick() {
   
    const dialogRef = dialog.open(NewReservation, {
        props: {
            header: $t('New FIT Reservation'),
            style: {
                width: '80vw',
            }, 
            modal: true,
            maximizable: true,
            closeOnEscape: false,
            position: "top",
            breakpoints:{
                '960px': '80vw',
                '640px': '100vw'
            },
        },
        onClose: (options) => {
             
            const data = options.data;
            if (data != undefined) {
                onViewReservationDetail(data.name)
            }
        }
    });
}


function onViewReservationDetail(name) {
    const dialogRef = dialog.open(ReservationDetail, {
        data: {
            name: name,
            delay_load_data:1500
        },
        props: {
            header: $t('Reservation Detail'),
            contentClass: 'ex-pedd',
            style: {
                width: '80vw',
            },
            modal: true,
            maximizable: true,
            closeOnEscape: false,
            position:"top", 
            breakpoints:{
                '960px': '80vw',
                '640px': '100vw'
            },
        },
        onClose: (options) => {

        }
    });

   
}


</script>