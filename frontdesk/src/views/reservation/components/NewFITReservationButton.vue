<template>
    <Button v-tooltip.left="'New Reservataion'" @click="onClick" label="New reservation" class="d-bg-set btn-inner-set-icon border-none">
        <img class="mr-2" :src="iconEdoorNewReservation">New Reservation
    </Button>
</template>
<script setup>
import iconEdoorNewReservation from '../../../assets/svg/icon-add-reservation.svg'
import { useDialog } from 'primevue/usedialog';
import NewReservation from '@/views/reservation/NewReservation.vue';
import ReservationDetail from '@/views/reservation/ReservationDetail.vue';

const dialog = useDialog();


function onClick() {
   
    const dialogRef = dialog.open(NewReservation, {
        props: {
            header: 'New FIT Reservation',
            style: {
                width: '80vw',
            },
            breakpoints: {
                '960px': '100vw',
                '640px': '100vw'
            },
            modal: true,
            maximizable: true,
            closeOnEscape: false,
            position: "top"
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
            name: name
        },
        props: {
            header: 'Reservation Detail',
            contentClass: 'ex-pedd',
            style: {
                width: '80vw',
            },
            breakpoints: {
                '960px': '75vw',
                '640px': '90vw'
            },
            modal: true,
            maximizable: true,
            closeOnEscape: false,
            position:"top"
        },
        onClose: (options) => {
            console.log(options)
        }
    });
}


</script>