<template>
    <Button @click="onClick" v-tooltip.left="'New Group Booking'" label="New Group Booking" class="btn-date__tt btn-inner-set-icon border-none">
        <img class="mr-2" :src="iconEdoorAddGroupBooking">New Group Booking
    </Button>
</template>
<script setup>
import iconEdoorAddGroupBooking from '../../../assets/svg/icon-add-group-booking.svg'
import { useDialog } from 'primevue/usedialog';

import NewGroupBooking from '@/views/reservation/NewGroupBooking.vue';
import ReservationDetail from '@/views/reservation/ReservationDetail.vue';

const dialog = useDialog();

function onClick() {
    const dialogRef = dialog.open(NewGroupBooking, {
        props: {
            header: 'New Group Booking',
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
            closeOnEscape: false
        },
        onClose: (options) => {
            console.log(options)
        }
    });
}


</script>