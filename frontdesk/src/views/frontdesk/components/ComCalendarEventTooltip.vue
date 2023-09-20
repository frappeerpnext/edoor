<template>
  
    <div class="p-2 w-full" v-if="event.extendedProps.type =='stay'">
                                        <div class="text-center border-1 p-2 border-round-lg">Reservation</div>
                                        <table class="tip_description_stay_table m-1 pt-3">
                                            <tbody>
                                            <tr class="table-rs-de" ><td>Res. No</td><td class="px-2">:</td><td>{{event.extendedProps?.reservation || ''}}</td></tr>
                                            <tr class="table-rs-de"><td>Res Stay. No</td><td class="px-2">:</td><td>{{event.extendedProps?.reservation_stay || ''}}</td></tr>    
                                            <tr class="table-rs-de"><td>Ref. No</td><td class="px-2">:</td><td>{{event.extendedProps?.reference_number || ''}} </td></tr>
                                            <tr class="table-rs-de"><td>Int. No</td><td class="px-2">:</td><td>{{event.extendedProps?.internal_reference_number ?? ''}}</td></tr>
                                            <tr class="table-rs-de"><td>Ref. type</td><td class="px-2">:</td><td>{{event.extendedProps?.reservation_type || ''}} {{event.extendedProps?.group_code ? '( ' + event.extendedProps?.group_code + ' )' : ''}}</td></tr>    
                                            <tr class="table-rs-de"><td>Guest</td><td class="px-2">:</td><td>{{event.title}}</td></tr>
                                            <tr class="table-rs-de"><td>Arrival</td><td class="px-2">:</td><td>{{ moment(event.extendedProps?.arrival_date).format('YYYY-MM-DD')}} - {{moment(event.extendedProps?.start_time, "HH:mm:ss").format("h:mm A") }}</td></tr>
                                            <tr class="table-rs-de"><td>Departure</td><td class="px-2">:</td><td>{{ moment(event.extendedProps?.departure_date).format('YYYY-MM-DD')}} - {{moment(event.extendedProps?.end_time, "HH:mm:ss").format("h:mm A")}}</td></tr>
                                            <tr class="table-rs-de"><td>Room</td><td class="px-2">:</td><td>{{event.extendedProps?.room_number}}</td></tr>
                                            <tr class="table-rs-de"><td>Pax</td><td class="px-2">:</td><td>{{event.extendedProps?.adult}} / {{event.extendedProps?.child}}</td></tr>
                                            <tr class="table-rs-de"><td>Source</td><td class="px-2">:</td><td>{{event.extendedProps?.business_source || ''}}</td></tr>
                                            <tr class="table-rs-de"><td>ADR</td><td class="px-2">:</td><td>
                                                <CurrencyFormat :value="event.extendedProps?.adr"/> 
                                            </td></tr>
                                            <tr class="table-rs-de"><td>Total Room Rate</td><td class="px-2">:</td><td>
                                                <CurrencyFormat :value="event.extendedProps?.total_room_rate"/> 
                                            </td>
                                            </tr>
                                            <tr class="table-rs-de"><td>Total Debit</td><td class="px-2">:</td><td>
                                                <CurrencyFormat :value="event.extendedProps?.total_debit"/> 
                                            </td>
                                            </tr>
                                            <tr class="table-rs-de"><td>Total Debit</td><td class="px-2">:</td><td>
                                                <CurrencyFormat :value="event.extendedProps?.total_debit"/> 
                                            </td>
                                            </tr>
                                            <tr class="table-rs-de"><td>Balance</td><td class="px-2">:</td><td>
                                                <CurrencyFormat :value="event.extendedProps?.balance"/> 
                                            </td>
                                            </tr>
                                            <tr v-if="event.extendedProps?.note != 'null' && event.extendedProps?.note" ><td><span class="mt-2">Note</span></td></tr>
                                            <tr v-if="event.extendedProps?.note != 'null' && event.extendedProps?.note"><td colspan="3"><div class="border-round-lg p-2 reason-box-style" >{{event.extendedProps?.note.length > 220 ? event.extendedProps?.note.substring(0, 220) + '...' : event.extendedProps?.note}}</div></td></tr>
                                           
                                            </tbody>
                                        </table>
    </div>
    <div v-else-if="event.extendedProps.type == 'room_block'" class="w-full p-2">
                                        <div class="text-center border-1 p-2 border-round-lg"> {{event.title}}</div>
                                        <table class="tip_description_stay_table mx-1 my-2 pt-3 ">
                                            <tbody>
                                            <tr class="table-rs-de" ><td>Block Number</td><td class="px-3">:</td><td> {{event?.publicId || ''}}</td></tr>  
                                            <tr class="table-rs-de"><td>Start Date</td><td class="px-3">:</td><td> {{moment(event?.start).format('YYYY-MM-DD')}}</td></tr>
                                            <tr class="table-rs-de"><td>Release Date</td><td class="px-3">:</td><td> {{moment(event?.end).format('YYYY-MM-DD')}}</td></tr>
                                            <tr class="table-rs-de"><td>Blocked by</td><td class="px-3">:</td><td> {{event.extendedProps?.block_by || ''}}</td></tr>
                                            <tr><td><span class="mt-2">Reason</span></td></tr>
                                            <tr><td colspan="3"><div class="border-round-lg p-2 reason-box-style" > {{event.extendedProps?.reason}}</div></td></tr>
                                            </tbody>
                                        </table>
    </div>
    
    <div v-else-if="event.extendedProps.type == 'room_type_event'" class="w-full p-2">
                                        <div :style="{backgroundColor:event.ui.backgroundColor}" class="text-center border-1 p-2 border-round-lg">Available Room  <span>{{event.title}}</span> </div>
                                        <table class="tip_description_stay_table mx-1 my-2 pt-3 ">
                                            <tbody>
                                            <tr class="table-rs-de" ><td>Arrival</td><td class="px-3">:</td><td> {{event?.extendedProps?.arrival }}</td></tr>  
                                            <tr class="table-rs-de"><td>Departure</td><td class="px-3">:</td><td> {{event?.extendedProps?.departure }}</td></tr>
                                            <tr class="table-rs-de"><td>Adult</td><td class="px-3">:</td><td> {{event?.extendedProps?.adult }}</td></tr>
                                            <tr class="table-rs-de"><td>Child</td><td class="px-3">:</td><td> {{event.extendedProps?.child}}</td></tr>
                                            
                                            </tbody>
                                        </table>
    </div> 
 
</template>
<script setup>
    import CurrencyFormat from "@/components/CurrencyFormat.vue"
    import moment from "@/utils/moment.js";
    const props =defineProps({
        event:Object
    })
</script>
