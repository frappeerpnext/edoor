<template>
    <Button @click="onClick" v-tippy="'New Group Booking'" label="New Group Booking" class="btn-date__tt btn-inner-set-icon border-none">
        <img class="mr-2" :src="iconEdoorAddGroupBooking">New Group Booking
    </Button>
</template>
<script setup>
import iconEdoorAddGroupBooking from '../../../assets/svg/icon-add-group-booking.svg'
import { useDialog } from 'primevue/usedialog';

import NewGroupBooking from '@/views/reservation/NewGroupBooking.vue';
import ComGroupAssignRoom from "@/views/reservation/components/form/ComGroupAssignRoom.vue"
import ReservationDetail from "@/views/reservation/ReservationDetail.vue"
 
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
                if(data.assign_room==false){
                  
                    onViewReservationDetail(data.reservation.name)
                }else {
                    onOpenGroupAssignRoom(data.reservation)

                }
                
            }
        }
    });
}

function onViewReservationDetail(name) {
    const dialogRef = dialog.open(ReservationDetail, {
        data: {
            name: name,
            delay_load_data:1500//for waiting data update in background process
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
 
function onOpenGroupAssignRoom(reservation) {
    const dialogRef = dialog.open(ComGroupAssignRoom, {
        data: {
            reservation: reservation
        },
        props: {
            header: 'Group Assign Room - ' + reservation.name,
            contentClass: 'ex-pedd',
            style: {
                width: '80vw',
            },
            position:"top",
            modal: true,
            maximizable: true,
            closeOnEscape: false
        },
        onClose: (options)=>{
            if(options.data){
                if(options.data=="open_reservation_detail"){
                    window.postMessage('view_reservation_detail|' + reservation.name , '*')
                }
            }
        }
    });
}


</script>