<template>
    <Button  v-shortkey="['ctrl', 'f']" @shortkey="onClick()"  v-tippy="'Walk-in Reservataion'" @click="onClick" label="Walk-In Guest" class="d-bg-set btn-inner-set-icon border-none">
        <!-- <img class="mr-2" :src="iconEdoorNewReservation"> -->
        <ComIcon icon="iconWalkIn" style="width:30px;" height="20px"></ComIcon>
{{ $t('Walk-In Guest') }}
        
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
        data:{
            is_walk_in:1
        },
        props: {
            header: 'New Walk-In Guest',
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
            header: 'Reservation Detail',
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