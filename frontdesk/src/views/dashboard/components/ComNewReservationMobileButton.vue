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
import {i18n} from '@/i18n';
const { t: $t } = i18n.global; 
const props = defineProps({
    is_walk_in: {
        type: Boolean,
        default: false
    },
})
if (props.is_walk_in) {
    items_add_new.value.push({
    label: $t("New Walk-In Guest"),
    icon: 'pi pi-user',
    command: () => {
        const dialogRef = dialog.open(NewReservation, {
        data:{
            is_walk_in:1
        },
        props: {
            header: $t('New Walk-In Guest'),
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
            position: "top",

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
}
items_add_new.value.push({
    label: $t("New FIT Reservation"),
    icon: 'pi pi-user',
    command: () => {
        const dialogRef = dialog.open(NewReservation, {
        props: {
            header: $t('New FIT Reservation'),
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
            position: "top",
            pt: {
                root: `${window.isMobile ? 'p-dialog-maximized' : ''}`
            }
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
    label: $t("New GIT Reservation"),
    icon: 'pi pi-users',
    command: () => {
        dialog.open(NewGroupBooking, {
        props: {
            header: $t('New Group Booking'),
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