<template lang="">
    <ComReservationStayPanel title="Room Stay">
        <template #content>
            <div id="room_stay" class="room-stay-list text-center">
            <DataTable class="p-datatable-sm mt-2" :value="rooms"  tableStyle="min-width: 50rem">
                    <Column field="start_date" header="Stay Date" >
                        <template #body="{ data }">
                            {{ moment(data.start_date).format('DD-MM-yyyy') }} to {{ moment(data.end_date).format('DD-MM-yyyy') }}
                        </template>
                    </Column>
                   
                    <Column field="room_nights" header="Nights"></Column>
                    <Column field="room_type_alias" header="Room">
                        <template #body="{ data }">
                        <div>
                            <span v-tooltip.top="data.room_type">
                              {{ data.room_type_alias }}  
                            </span>/<span  v-if="data.room_number">
                                 {{data.room_number}}
                            </span>
                             <span @click="onAssignRoom(data)" class="link_line_action w-auto" v-else>
                                <i class="pi pi-pencil"></i>
                                Assign Room
                             </span>
                        </div>
                        </template>
                    </Column>
                    <Column class="text-right res__room-list-right" header="ADR">
                        <template #body="{data}">
                            <span class="text-end">
                                <CurrencyFormat :value="data.adr" /> 
                            </span>
                        </template>
                    </Column>
                    <Column class="text-right res__room-list-right" header="Tax">
                        <template #body="{data}">
                            <span class="text-end">
                                <CurrencyFormat :value="data.total_tax" /> 
                            </span>
                        </template>
                    </Column>
                    <Column class="text-right res__room-list-right" header="Total Charge">
                        <template #body="{ data }">
                            <span class="text-end">
                            <CurrencyFormat :value="data.total_amount"/>
                            </span>
                        </template>
                    </Column>
                    <Column header="">
                        <template #body="slotProps">
                            <template v-if="canNotUpgradeRoom">
                                <ComReservationStayRoomListMoreOption class="p-0" @onSelected="onSelected" :data="slotProps.data"/>
                            </template>
                        </template>
                    </Column>
            </DataTable>
            </div>
            <div class="flex justify-end mt-3" v-if="canNotUpgradeRoom">
                <Button class="conten-btn" @click="onUpgradeRoom"><ComIcon icon="iconBedPurple" class="me-2" /> Upgrade Room</Button>
            </div>
        </template>
    </ComReservationStayPanel>
</template>
<script setup>
import ComReservationStayPanel from './ComReservationStayPanel.vue';
import ComReservationStayRoomListMoreOption from '../components/ComReservationStayRoomListMoreOption.vue'
import ComReservationStayUpgradeRoom from './ComReservationStayUpgradeRoom.vue';
import ComReservationStayAssignRoom from './ComReservationStayAssignRoom.vue';
import {inject,ref,useDialog,computed} from '@/plugin'
import Enumerable from 'linq'
const moment = inject('$moment')
const selecteds = ref([])
const rs = inject("$reservation_stay")
const dialog = useDialog()
const rooms = computed(()=>{
    return Enumerable.from(rs.reservationStay?.stays).orderBy("$.creation").toArray()
})
const canNotUpgradeRoom = computed(()=>{
    return !rs.reservationStatusDelete.find(r=>r == rs.reservationStay.reservation_status)
})
function onUpgradeRoom() { 

        dialog.open(ComReservationStayUpgradeRoom, {
        data: {
            rs: rs
        },
        props: {
            header: `Upgrade Room`,
            style: {
                width: '70vw',
            },
            
            breakpoints: {
                '960px': '75vw',
                '640px': '90vw'
            },
            modal: true,
            closeOnEscape: false
        },
        onClose: (options) => {
            //
        }
    });
}
    
function onAssignRoom(data){
    dialog.open(ComReservationStayAssignRoom, {
        data: {
            stay_room: data
        },
        props: {
            header: `Assign Room`,
            style: {
                width: '70vw',
            },
            
            breakpoints: {
                '960px': '75vw',
                '640px': '90vw'
            },
            modal: true,
            closeOnEscape: false
        },
        onClose: (options) => {
            //
        }
    })
}
</script>
<style scoped>
    .p-datatable > .p-datatable-wrapper {
        border-radius: 0.75rem !important;
    }
</style>