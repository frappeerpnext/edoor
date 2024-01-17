<template>
<DataTable :value="data" paginator  :rows="20" tableStyle="min-width: 50rem" :rowsPerPageOptions="[5, 10, 20, 50]">
    <Column header="No" headerClass="text-center" bodyClass="text-center">
            <template #body="slotProps">
                {{ data.indexOf(slotProps.data) + 1 }}
            </template>
        </Column>
    <Column header="Reservation #">
        <template  #body="slotProps">
            <Button class="p-0 link_line_action1" @click="onViewDetail('view_reservation_detail',slotProps.data.reservation)" link>
            {{ slotProps?.data.reservation  }}
            </Button>
        </template>
    </Column>
    <Column field="name" header="Stay #">
        <template  #body="slotProps">
            <Button class="p-0 link_line_action1" @click="onViewDetail('view_reservation_stay_detail',slotProps.data.name)" link>
            {{ slotProps?.data.name }}
            </Button>
        </template>
    </Column>
    <Column field="reference_number" header="Ref. #"></Column>
    <Column field="name" header="PAX(A/C)">
        <template  #body="slotProps">
            {{slotProps?.data.adult  }} / {{slotProps?.data.child }}
        </template>
    </Column>
    <Column field="reservation_type" header="Type"></Column>
    <Column  header="Res. Date">
        <template  #body="slotProps">
            
            {{ moment(slotProps?.data.reservation_date).format("DD-MM-YYYY") }}
        </template>
       
    </Column>
    <Column field="name" header="Stay Date">
        <template  #body="slotProps">
            {{ moment(slotProps.data.arrival_date).format("DD-MM-YYYY") }} &#8594; {{
                    moment(slotProps.data.departure_date).format("DD-MM-YYYY") }}

        </template>
    </Column>
    <Column field="room_nights" headerClass="text-center" header="Room Nights">
        <template  #body="slotProps">
            <div class="text-center">
  {{ slotProps?.data.room_nights }}
            </div>
          
        </template>
    </Column>
    <Column  header="Room(s)">
    <template #body="slotProps">
        <div> 
                            <span v-tippy ="slotProps?.data.room_type">
                              {{ slotProps?.data.room_type_alias }} 
                            </span>/<span  v-if="slotProps?.data.rooms">
                                 {{slotProps?.data.rooms}}
                            </span>
                            <span @click="onAssignRoom(slotProps?.data)" class="link_line_action w-auto" v-else>
                                <i class="pi pi-pencil"></i>
                                Assign Room
                            </span>
                        </div>
    </template>
    </Column>
    <Column header="Guest">
        <template  #body="slotProps">
            <div>
                <Button class="p-0 link_line_action1" @click="onViewDetail('view_guest_detail',slotProps.data.guest)" link>
                    {{ slotProps?.data.guest }} - {{ slotProps?.data.guest_name }}
                </Button>
            </div>
          
        </template>
    </Column>
    <Column headerClass="text-right" bodyClass="text-right" header="ADR">
        <template  #body="slotProps">
                 <CurrencyFormat :value="slotProps?.data.adr" />
        </template>
    </Column>
    <Column headerClass="text-right" bodyClass="text-right" header="Total Room Rate">
        <template  #body="slotProps">
                 <CurrencyFormat :value="slotProps?.data.total_room_rate" />
        </template>
        
    </Column>
    <Column headerClass="text-center" bodyClass="text-center" header="Status">
        <template  #body="slotProps">
            <span class="px-2 rounded-lg text-white p-1px border-round-3xl" :style="{ backgroundColor: slotProps?.data.status_color }">{{ slotProps?.data.reservation_status}}</span>
        </template>
    </Column>
</DataTable>

</template>
<script setup>
import { inject } from '@/plugin';
const moment = inject("$moment")
const props = defineProps({
    data:Object
})
function onViewDetail(action,name){
    
    window.postMessage(action + "|" + name,"*")
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