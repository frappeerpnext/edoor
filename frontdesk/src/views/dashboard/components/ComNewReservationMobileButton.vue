<template>
 <SplitButton class="border-split-none w-full" label="Reservation" icon="pi pi-plus-circle" :model="items_add_new" />
</template>
<script setup>
import { ref } from '@/plugin'
import NewReservation from '@/views/reservation/NewReservation.vue';
import NewGroupBooking from '@/views/reservation/NewGroupBooking.vue';
import { useDialog } from 'primevue/usedialog';
const items_add_new = ref([])
const dialog = useDialog();
items_add_new.value.push({
    label: "New FIT Reservation",
    icon: 'pi pi-user',
    command: () => {
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
})


//Confirmattion Voucher
items_add_new.value.push({
    label: "New GIT Reservation",
    icon: 'pi pi-users',
    command: () => {
        dialog.open(NewGroupBooking, {
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
})

</script>