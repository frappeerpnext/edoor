<template lang="">
    <ComReservationStayPanel title="Reservation Room List">
        <template #content>
            {{Object.entries(rs.reservation).length === 0}}
            <ComPlaceholder :loading="rs.loading" :isNotEmpty="true">
                <div class="flex justify-end">
                    <div>
                        <ComBoxStayInformation valueClass="border-1">
                            <span class="bg-gray-edoor rounded-xl px-2 mr-1">No Show</span> 
                            <span class="bg-gray-edoor rounded-xl px-2 mr-1">In house</span>
                            <span class="bg-gray-edoor rounded-xl px-2">Canceled</span>
                        </ComBoxStayInformation>
                    </div>
                </div>
                <div v-for="(item, index) in rs.reservationStays" :key="index">
                </div>
                <div class="room-stay-list ress__list text-center mt-4">
                    <DataTable class="p-datatable-sm" v-model:selection="selecteds" :value="rs.reservationStays" tableStyle="min-width: 50rem">
                        <Column selectionMode="multiple" headerStyle="width: 3rem"></Column>
                        <Column field="arrival_date" header="Arrival"></Column>
                        <Column field="departure_date" header="Departure"></Column>
                        <Column field="room_types" header="Room Type"></Column>
                        <Column field="rooms" header="Room"></Column>
                        <Column header="Guest Name">
                            <template #body="slotProps">
                                <div v-tooltip.top="slotProps.data.guest_name" v-if="slotProps.data.guest_name.length > 15" class="overflow-hidden text-overflow-ellipsis whitespace-nowrap w-12rem">{{slotProps.data.guest_name}}</div>
                                <div v-else>{{slotProps.data.guest_name}}</div>
                            </template>
                        </Column>
                        <Column field="pax" header="Pax"></Column>
                        <Column field="total_charge" header="Total Charge"></Column>
                        <Column field="total_payment" header="Paid"></Column>
                        <Column field="balance" header="Balance"></Column>
                        <Column field="reservation_status" header="Status">
                            <template #body="slotProps">
                                <ComReservationStatus class="border-round-3xl" :status-name="slotProps.data.reservation_status"/>
                            </template>
                        </Column>
                        <Column header="">
                            <template #body="slotProps">
                                <ComReservationStayMoreButton class="p-0 my-1" @onSelected="onSelected" :data="slotProps.data"/>
                            </template>
                        </Column>
                    </DataTable>
                </div>
                <!-- {{rs.reservation}} -->
                <div class="grid mt-3">
                    <div class="col-8">
                        <div class="">
                            <ComReservationStayListStatusBadge v-if="!(Object.entries(rs.reservation).length === 0)"/>
                        </div>
                    </div>
                    <div class="col-4 py-0">
                        <div class="flex gap-2">
                            <ComBoxStayInformation isCurrency tooltip="" title="Total Amount" titleClass="grow white-space-nowrap w-16rem" valueClass="w-full text-right"></ComBoxStayInformation>
                        </div>
                        <div class="flex mt-2 gap-2">
                            <ComBoxStayInformation isCurrency tooltip="" title="Paid" titleClass="grow w-16rem" valueClass="w-full text-right"></ComBoxStayInformation>
                        </div>
                        <div class="flex mt-2 gap-2">
                            <ComBoxStayInformation isCurrency title="Balance" valueClass="text-right bg-gray-edoor-10 font-semibold w-full" titleClass="grow w-16rem font-semibold" ></ComBoxStayInformation>
                        </div>
                    </div>
                </div>
            </ComPlaceholder>
        </template>
    </ComReservationStayPanel>
</template>
<script setup>
import {inject,ref} from '@/plugin'
import ComReservationStayPanel from '@/views/reservation/components/ComReservationStayPanel.vue';
import ComBoxStayInformation from '@/views/reservation/components/ComBoxStayInformation.vue';
import ComReservationStayMoreButton from '../components/ComReservationStayMoreButton.vue'
import ComReservationStayListStatusBadge from '@/views/reservation/components/ComReservationStayListStatusBadge.vue'


const moment = inject('$moment')
const rs = inject("$reservation")
const selecteds = ref([])
 
</script>
<style scoped>
    .p-datatable > .p-datatable-wrapper {
        border-radius: 0.75rem !important;
    }
</style>