<template>
    {{ data.name }}
    <Button class="h-2rem w-2rem" style="font-size: 1.5rem" text rounded :aria-controls="data.name.replaceAll(' ', '')" icon="pi pi-ellipsis-v" @click="toggle"></Button>
    <Menu ref="show" :model="menus" :id="data.name.replaceAll(' ', '')" :popup="true" style="min-width: 180px;">
        <template #end> 
            <ComReservationStayMoreOptions @onDupicateReservation="onDupicateReservation" @onAuditTrail="onAuditTrail()" @onRefresh="onRefresh(false)" >
                <!-- <template #default> 
                    <Button v-if="rs.canCheckIn() && rs.reservationStay?.reservation_status != 'In-house'" @click="onCheckIn"
                        class="w-full p-link flex align-items-center py-2 px-3 text-color hover:surface-200 border-0 bg-transparent">
                        <ComIcon icon="checkin-black" style="height: 18px;" class="me-2" />
                        {{ $t('Check In') }}
                    </Button>
                    <Button
                        v-if="rs.reservationStay?.reservation_status === 'In-house' && (moment(working_day.date_working_day) >= moment(rs.reservationStay.departure_date).add(-1, 'day'))"
                        @click="onCheckOut" class="w-full p-link flex align-items-center py-2 px-3 text-color hover:surface-200 border-noround">
                        <ComIcon icon="checkoutBlack" style="height: 18px;" class="me-2" />
                        {{ $t('Check Out') }}
                    </Button>
                </template> -->
            </ComReservationStayMoreOptions>
        </template>
    </Menu>
</template>
<script setup>
import { ref, inject, useDialog } from '@/plugin';
import ComReservationStayMoreOptions from "@/views/reservation/components/ComReservationStayMoreOptions.vue"; 
import ComAuditTrail from "@/components/layout/components/ComAuditTrail.vue"; 
const props = defineProps({
    data:Object
})
const emit = defineEmits(['onMoreAction']) 

import {i18n} from '@/i18n'; 
const { t: $t } = i18n.global;

const dialogRef = inject("dialogRef");
const rs = inject('$reservation_stay');
const dialog = useDialog()


const show = ref()
const toggle = (event) => {
    show.value.toggle(event);
    emit('onMoreAction')
}; 


function onDupicateReservation(){
    dialogRef.value.close()
}

function onAuditTrail() {
    const dialogRef = dialog.open(ComAuditTrail, {
        data: {
            doctype: 'Reservation Stay',
            docname: props.data.name,
            referenceTypes: [
                { doctype: 'Reservation Stay', label: 'Reservation stay' },
                { doctype: 'Reservation Room Rate', label: 'Room Rate' },
                { doctype: 'Customer', label: 'Guest' },
                { doctype: 'Reservation Folio', label: 'Reservation Folio' },
                { doctype: 'Folio Transaction', label: 'Folio Transaction' },
            ],
            filter_key: "custom_reservation_stay"
        },
        props: {
            header: $t('Audit Trail'),
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
    });
} 
</script>