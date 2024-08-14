<template>
    <div class="flex" >
    <div class="p-2 w-full col" :class="index != '0' ? 'border-left-1' : ''" v-for="( data , index ) in data" v-if="data">
        <div class="text-center mb-3 border-1 p-2 border-round-lg overflow-hidden text-overflow-ellipsis ">
            <span class="me-2"> {{ data.guest_name }}
            </span>
        </div>
        <div class="flex mb-2 mt-2 gap-2 text-right">
              <div class="col p-2 bg-gray-edoor-10 rounded-lg shadow-charge-total border border-gray-edoor-100">
                  <div class="text-500 uppercase text-sm white-space-nowrap">{{$t('Total Debit')}}</div>
                  <div class="text-xl line-height-2 font-semibold text-color white-space-nowrap" ><CurrencyFormat :value="data?.total_debit"></CurrencyFormat></div>
              </div>
              <div class="col p-2 bg-gray-edoor-10 rounded-lg shadow-charge-total border border-gray-edoor-100">
                  <div class=" text-500 uppercase text-sm white-space-nowrap">{{$t('Total Credit')}}</div>
                  <div class="text-xl line-height-2 font-semibold text-color white-space-nowrap" ><CurrencyFormat :value="data?.total_credit"></CurrencyFormat></div>
              </div>
              <div class="col p-2 bg-green-50 rounded-lg shadow-charge-total border border-green-edoor">
                  <div class="text-500 uppercase text-sm white-space-nowrap">{{$t('Balance')}}</div>
                
                  <div class="text-xl line-height-2 font-semibold text-color white-space-nowrap"><CurrencyFormat :value="( data?.total_debit - data?.total_credit )"></CurrencyFormat></div>
              </div>
          </div>

 

        <table class="tip_description_stay_table m-1 pt-4">
            <tbody>
                <tr class="table-rs-de">
                    <td> {{ $t('Res. No') }} </td>
                    <td class="px-2">:</td>
                    <td>{{ data?.reservation || '' }}</td>
                </tr>
                <!-- <tr class="table-rs-de" v-if="data.reservation_color">
                    <td>{{ $t('Res Special Color') }}</td>
                    <td class="px-2">:</td>
                    <div class="flex mt-1 align-items-center">
                        <div style="height:14px !important;" class="px-4 inline-block border-1 border-white me-2"
                            :style="{ background: event.extendedProps.reservation_color }"></div> <span>
                            {{ event.extendedProps.reservation_color_code }} </span>
                    </div>
                </tr> -->
                <tr class="table-rs-de">
                    <td>{{ $t('Res Stay Status') }}</td>
                    <td class="px-2">:</td>
                    <td>{{ $t(data?.reservation_status || '') }}</td>
                </tr>
                <tr class="table-rs-de">
                    <td>{{ $t('Business Source') }}</td>
                    <td class="px-2">:</td>
                    <td>{{ $t(data?.business_source || '') }}</td>
                </tr>
                <tr class="table-rs-de">
                    <td>{{ $t('Res Stay. No') }}</td>
                    <td class="px-2">:</td>
                    <td>{{ data?.reservation_stay || '' }}</td>
                </tr>
                <tr class="table-rs-de">
                    <td>{{ $t('Ref. No') }}</td>
                    <td class="px-2">:</td>
                    <td>{{ data?.reference_number || '' }} </td>
                </tr>
                <tr class="table-rs-de">
                    <td>{{ $t('Int. No') }}</td>
                    <td class="px-2">:</td>
                    <td>{{ data?.internal_reference_number ?? '' }}</td>
                </tr>
                <tr class="table-rs-de">
                    <td> {{ $t('Res. Type') }}</td>
                    <td class="px-2">:</td>
                    <td>{{ data?.reservation_type || '' }} </td>
                </tr>
                <!-- <tr class="table-rs-de"
                    v-if="data?.group_name || data?.group_code || data?.group_color">
                    <td>{{ $t('Group') }}</td>
                    <td class="px-2">:</td>
                    <td>
                        <div style="height:14px !important;" class="px-4 inline-block border-1 border-white me-2"
                            :style="{ background: data.group_color }"></div><span
                            v-if="data?.group_name">{{ data?.group_name || '' }}</span> <span
                            v-if="data?.group_code"> - {{ data?.group_code || '' }}</span>
                    </td>
                </tr> -->
                <tr class="table-rs-de">
                    <td>{{ $t('Arrival') }}</td>
                    <td class="px-2">:</td>
                    <td>{{ moment(data.arrival_date).format('DD-MM-YYYY') }} 
                    </td>
                </tr>
                <tr class="table-rs-de">
                    <td>{{ $t('Departure') }}</td>
                    <td class="px-2">:</td>
                    <td>{{ moment(data.departure_date).format('DD-MM-YYYY') }} 
                    </td>
                </tr>
                <tr class="table-rs-de">
                    <td>{{ $t('Nights') }}</td>
                    <td class="px-2">:</td>
                    <td>{{ data.room_nights }}
                    </td>
                </tr>
                <tr class="table-rs-de">
                    <td>{{ $t('Room') }}</td>
                    <td class="px-2">:</td>
                    <td>{{ data?.room_number }}</td>
                </tr>
                <tr class="table-rs-de">
                    <td>{{ $t('Pax(A/C)') }}</td>
                    <td class="px-2">:</td>
                    <td>{{ data?.adult }} / {{ data?.child }}</td>
                </tr>
                <!-- <tr class="table-rs-de">
                    <td>{{ $t('Source') }}</td>
                    <td class="px-2">:</td>
                    <td>{{ data?.business_source || '' }}</td>
                </tr> -->
                <!-- <tr v-if="data?.note != 'null' && data?.note">
                    <td colspan="3">
                        <div class="border-round-lg p-2 reason-box-style">{{ data?.note.length > 220 ?
                            data?.note.substring(0, 220) + '...' : data?.note }}</div>
                    </td>
                </tr> -->
            </tbody>
        </table>
         <hr class="my-2">
        <div class="flex gap-2 justify-content-between">
        <Button @click="onViewReservationStay(data.reservation_stay)" class="white-space-nowrap border-none">View Detail</Button>
        <Button v-if="data?.is_arrival && data?.reservation_status == 'Reserved'" @click="onCheckIn"
                class="bg-green-500 border-none white-space-nowrap">
                <ComIcon icon="checkin" style="height: 18px;" class="me-2" />
                {{ $t('Check In') }}
                
        </Button>
        <Button
                v-if="data?.reservation_status === 'In-house' && data?.is_departure"
                @click="onCheckOut" class="bg-red-400 border-none white-space-nowrap">
                <ComIcon icon="checkout" style="height: 18px;" class="me-2" />
                {{ $t('Check Out') }}
        </Button>
        </div>
        
    </div>
</div>
<div class="card flex justify-center">
        <Button label="Dialog Show" @click="visible = true" />
        <Dialog v-model:visible="visible" >
            <div class="flex justify-end gap-2">
                <Button type="button" label="Cancel" severity="secondary" @click="visible = false"></Button>
                <Button type="button" label="Save" @click="visible = false"></Button>
            </div>
        </Dialog>
    </div>
    
</template>
<script setup>
import Dialog from 'primevue/dialog'; 
import CurrencyFormat from "@/components/CurrencyFormat.vue"
import ComIcon from "@/components/ComIcon.vue"
import ComConfirmCheckIn from '@/views/reservation/components/confirm/ComConfirmCheckIn.vue'
import Button from 'primevue/button';
import moment from "@/utils/moment.js";
import {i18n} from '@/i18n';
const { t: $t } = i18n.global;
import { ref , defineEmits } from "vue";
const visible = ref(false);
const props = defineProps({
    data:Object
})
function onViewReservationStay(stay) {
      window.postMessage('view_reservation_stay_detail|' + stay, '*')
}
const emit = defineEmits(['checkin']);
function onCheckIn(){
    emit('checkin')
}
function onCheckOut(){
    alert(231)
}
</script>
