<template lang="">
    <ComReservationStayPanel title="Room Stay">
        <template #content> 
            <div id="room_stay" class="room-stay-list text-center"> 
            <DataTable class="p-datatable-sm mt-2" :value="rooms"  tableStyle="min-width: 50rem">
                    <Column class="w-15rem" field="start_date" header="Stay Date" >
                        <template #body="{ data }">
                            <span v-tippy ="'Arrival Date'">
                            {{gv.dateFormat(data.start_date) }}
                            </span>
                            &#8594;
                            <span v-tippy="'Departure Date'">
                            {{gv.dateFormat(data.end_date) }}
                            </span> 
                        </template>
                    </Column> 
                    <Column class="text-center w-10rem" field="room_nights" header="Nights"></Column>
                    <Column field="room_type_alias" header="Room">
                        <template #body="{ data }">
                        <div> 
                            <span v-tippy ="data.room_type">
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
                    <Column v-if="can_view_rate" class="text-right res__room-list-right" header="ADR">
                        <template #body="{data}">
                            <span class="text-end">
                                <CurrencyFormat :value="data.adr" /> 
                                 
                            </span>
                        </template>
                    </Column>

                    <Column v-if="can_view_rate"  class="text-right res__room-list-right" header="Discount">
                        <template #body="{data}">
                            <span class="text-end">
                                <CurrencyFormat :value="data.discount_amount" /> 
                            </span>
                        </template>
                    </Column>

                    <Column v-if="can_view_rate"  class="text-right res__room-list-right" header="Tax">
                        <template #body="{data}">
                            <span class="text-end">
                                <CurrencyFormat :value="data.total_tax" /> 
                            </span>
                        </template>
                    </Column>
                    <Column v-if="can_view_rate"  class="text-right res__room-list-right" header="Total Rate">
                        <template #body="{ data }">
                            <span class="text-end">
                            <CurrencyFormat :value="data.total_rate"/> 
                            </span>
                        </template>
                    </Column>
                    <Column header="">
                        <template #body="{ data }">
                            <ComReservationStayRoomListMoreOption :rooms="rooms" class="p-0" @onSelected="onSelected" :data="data"/>
                          
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
import ComReservationStayPanel from '@/views/reservation/components/ComReservationStayPanel.vue';
import ComReservationStayRoomListMoreOption from '@/views/reservation/components/ComReservationStayRoomListMoreOption.vue'
import ComReservationStayUpgradeRoom from '@/views/reservation/components/ComReservationStayUpgradeRoom.vue';
import ComReservationStayAssignRoom from '@/views/reservation/components/ComReservationStayAssignRoom.vue';
import {inject,ref,useDialog,computed   } from '@/plugin'
import Enumerable from 'linq';
const gv = inject('$gv');
const rs = inject("$reservation_stay")
const dialog = useDialog() 

const can_view_rate = ref(window.can_view_rate)

const rooms = computed(()=>{
    return Enumerable.from(rs.reservationStay?.stays).orderBy("$.start_date").toArray()
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
                width: '80vw',
            },
            
            modal: true,
            closeOnEscape: false,
            position: 'top'
        },
        onClose: (options) => { 
            
            if(options.data){
                //we delay time to reload here to wait until equeue job is done in server
                
                setTimeout(() => {
                    rs.getReservationDetail(rs.reservationStay.name)  
                    window.socket.emit("Frontdesk", window.property_name)
                }, 1500);
                
            }
        }
    });
}
    
function onAssignRoom(data){
    let getData = JSON.parse(JSON.stringify(data))

    getData.business_source = rs.reservationStay.business_source
    dialog.open(ComReservationStayAssignRoom, {
        data: {
            stay_room: getData
        },
        props: {
            header: `Assign Room`,
            style: {
                width: '80vw',
            },
            modal: true,
            closeOnEscape: false,
            position: 'top'
        },
        onClose: (options) => {
            if(options.data && options.data.message){
                setTimeout(() => {
                    rs.getReservationDetail(options.data.message.name)
                }, 1500);
            } 
        }
    })
}
</script>
<style scoped>
    .p-datatable > .p-datatable-wrapper {
        border-radius: 0.75rem !important;
    }
</style>