<template>
<DataTable :value="data" paginator  :rows="20" tableStyle="min-width: 50rem">
    <Column :header="$t('No')" headerClass="text-center" bodyClass="text-center">
            <template #body="slotProps">
                {{ data.indexOf(slotProps.data) + 1 }}
            </template>
        </Column>
    <Column :header="$t('Reservation') + ' #' ">
        <template  #body="slotProps">
            <Button class="p-0 link_line_action1" @click="onViewDetail('view_reservation_detail',slotProps.data.reservation)" link>
            {{ slotProps?.data.reservation  }}
            </Button>
        </template>
    </Column>
    <Column field="name" :header="$t('Stay') + ' #' ">
        <template  #body="slotProps">
            <Button class="p-0 link_line_action1" @click="onViewDetail('view_reservation_stay_detail',slotProps.data.name)" link>
            {{ slotProps?.data.name }}
            </Button>
        </template>
    </Column>
    <Column field="reference_number" :header="$t('Ref.') + ' #' "></Column>
    <Column field="name" :header="$t('PAX(A/C)')" headerClass="text-center" bodyClass="text-center">
        <template  #body="slotProps">
            {{slotProps?.data.adult  }} / {{slotProps?.data.child }}
        </template>
    </Column>
    <Column field="reservation_type" :header="$t('Type')" headerClass="text-center" bodyClass="text-center"></Column>
    <Column  :header="$t('Res. Date')" headerClass="text-center" bodyClass="text-center">
        <template  #body="slotProps">
            
            {{ moment(slotProps?.data.reservation_date).format("DD-MM-YYYY") }}
        </template>
       
    </Column>
    <Column field="name" :header="$t('Stay Date')" headerClass="text-center" bodyClass="text-center">
        <template  #body="slotProps">
            {{ moment(slotProps.data.arrival_date).format("DD-MM-YYYY") }} &#8594; {{
                    moment(slotProps.data.departure_date).format("DD-MM-YYYY") }}

        </template>
    </Column>
    <Column field="room_nights" headerClass="text-center" :header="$t('Room Nights')">
        <template  #body="slotProps">
            <div class="text-center">
  {{ slotProps?.data.room_nights }}
            </div>
          
        </template>
    </Column>
    <Column :header="$t('Rooms')">
            <template #body="slotProps">
                {{ slotProps.data.room_type_alias }} 
                <span v-if="slotProps.data.rooms">/ {{ slotProps.data.rooms }}</span>
            </template>

        </Column>
    <Column :header="$t('Guest')">
        <template  #body="slotProps">
            <div>
                <Button class="p-0 link_line_action1" @click="onViewDetail('view_guest_detail',slotProps.data.guest)" link>
                    {{ slotProps?.data.guest }} - {{ slotProps?.data.guest_name }}
                </Button>
            </div>
          
        </template>
    </Column>
    <Column headerClass="text-right" bodyClass="text-right" :header="$t('ADR')">
        <template  #body="slotProps">
           
                 <CurrencyFormat :value="slotProps?.data.adr" />
           
        </template>
        
    </Column>
       <Column headerClass="text-right" bodyClass="text-right"   :header="$t('Total Rate')">
        <template  #body="slotProps">
         
                 <CurrencyFormat :value="slotProps?.data.total_room_rate" />
         
        </template>
        
    </Column>
    <Column field="status_color" :header="$t('Status')" headerClass="text-center" bodyClass="text-center">
        <template  #body="slotProps">
            <span class="px-2 rounded-lg text-white p-1px border-round-3xl" :style="{ backgroundColor: slotProps?.data.status_color }">{{ slotProps?.data.reservation_status}}</span>
        </template>
    </Column>
    
    <Column field="cancelled_date" :header="$t('Date')" headerClass="text-center" bodyClass="text-center">
        <template  #body="slotProps">
            {{ moment(slotProps.data.cancelled_date).format("DD-MM-YYYY") }} 
        </template>
    </Column>
    
    <Column field="cancelled_by" :header="$t('By')">
        <template  #body="slotProps">
          {{ slotProps?.data.cancelled_by.split("@")[0]}}
        </template>
    </Column>
    <Column field="cancelled_note" :header="$t('Note')"/>
</DataTable>

</template>
<script setup>
import { inject } from '@/plugin';
const moment = inject("$moment")
import {i18n} from '@/i18n';
const { t: $t } = i18n.global;
const props = defineProps({
    data:Object
})
function onViewDetail(action,name){
    
    window.postMessage(action + "|" + name,"*")
}    
</script>