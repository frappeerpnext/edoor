<template lang="">
    <ComReservationStayPanel title="Reservation Room List">
        <template #content> 
            <ComPlaceholder :loading="rs.loading" :isNotEmpty="true">
                <div class="flex justify-end">
                    <div>
                        <div class="card flex justify-content-center">
                            <div class="filtr-rmm-list">
                                <ComSelect placeholder="filter by status" v-model="selectStatus" isMultipleSelect optionLabel="reservation_status" optionValue="name" :options="status" @onSelected="onFilterSelectStatus"></ComSelect>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="room-stay-list ress__list text-center mt-3">
                    <DataTable class="p-datatable-sm" v-model:selection="selecteds" :value="roomList" tableStyle="min-width: 50rem">
                        <Column selectionMode="multiple" headerStyle="width: 3rem"></Column>
                        <Column field="arrival_date" header="Arrival"></Column>
                        <Column field="departure_date" header="Departure"></Column>
                        <Column header="Room Type">
                            <template #body="slotProps">
                                <div v-tooltip.top="slotProps.data.room_types">{{slotProps.data.room_type_alias}}</div>
                            </template>
                        </Column>
                        <Column field="rooms" header="Room"></Column>
                        <Column header="Guest Name">
                            <template #body="slotProps">
                                <div v-tooltip.top="slotProps.data.guest_name" v-if="slotProps.data.guest_name.length > 15" class="overflow-hidden text-overflow-ellipsis whitespace-nowrap w-12rem">{{slotProps.data.guest_name}}</div>
                                <div v-else>{{slotProps.data.guest_name}}</div>
                            </template>
                        </Column>
                        <Column header="Pax">
                            <template #body="slotProps">
                                <span v-tooltip.top="'Adults'">{{slotProps.data.adult}}</span>/<span v-tooltip.top="'Children'">{{slotProps.data.child}}</span>
                            </template>
                        </Column>
                        <Column class="text-right res__room-list-right" header="Total Charge">
                            <template #body="slotProps">
                                <CurrencyFormat :value="slotProps.data.total_charge"/>
                            </template>
                        </Column>
                        <Column class="text-right res__room-list-right" header="Paid">
                            <template #body="slotProps">
                                <CurrencyFormat :value="slotProps.data.total_payment"/>
                            </template>
                        </Column>
                        <Column class="text-right res__room-list-right" header="Balance">
                            <template #body="slotProps">
                                <CurrencyFormat :value="slotProps.data.balance"/>
                            </template>
                        </Column>
                        <Column field="reservation_status" class="res__state__center text-center" header="Status">
                            <template #body="slotProps">
                                <ComReservationStatus class="border-round-3xl" :status-name="slotProps.data.reservation_status"/>
                            </template>
                        </Column>
                        <Column header="">
                            <template #body="slotProps">
                                <ComReservationStayMoreButton class="p-0" @onSelected="onSelected" :data="slotProps.data"/>
                            </template>
                        </Column>
                    </DataTable>
                </div>
                <div class="grid mt-3">
                    <div class="col-8 pl-2 py-0">
                        <div class="flex flex-column justify-between h-full">
                            <ComReservationStayListStatusBadge v-if="!(Object.entries(rs.reservation).length === 0)"/>
                        </div>
                    </div>
                    <div class="col py-0">
                        <div class="flex gap-2">
                            <ComBoxStayInformation title="Total Amount" titleClass="grow white-space-nowrap w-16rem" valueClass="w-full text-right">
                                <CurrencyFormat :value="rs.reservation.total_amount"/>
                            </ComBoxStayInformation>
                        </div>
                        <div class="flex mt-2 gap-2">
                            <ComBoxStayInformation title="Paid" titleClass="grow w-16rem" valueClass="w-full text-right">
                                <CurrencyFormat :value="rs.reservation.payment"/>
                            </ComBoxStayInformation>
                        </div>
                        <div class="flex mt-2 gap-2">
                            <ComBoxStayInformation title="Balance" valueClass="text-right bg-gray-edoor-10 font-semibold w-full" titleClass="grow w-16rem font-semibold" >
                                <CurrencyFormat :value="rs.reservation.balance"/>
                            </ComBoxStayInformation>
                        </div>
                    </div>
                </div>
                <hr class="mt-3"/>
                <div class="pt-3">
                    <div class="flex justify-end gap-2"> 
                        <SplitButton class="split__btn_none_icon" label="More Options" @click="moreOptions" :model="items" />
                        <Button class="border-none">
                            <img class="btn-add_comNote__icon me-2" :src="AddRoomIcon"/> Add More Room
                        </Button>
                        <Button class="border-none" label="Edit Booking" icon="pi pi-file-edit" />
                    </div>
                </div>  
            </ComPlaceholder>
        </template>
    </ComReservationStayPanel>
</template>
<script setup>
import {inject,ref,onMounted} from '@/plugin'
import ComReservationStayPanel from '@/views/reservation/components/ComReservationStayPanel.vue';
import ComBoxStayInformation from '@/views/reservation/components/ComBoxStayInformation.vue';
import ComReservationStayMoreButton from '../components/ComReservationStayMoreButton.vue'
import ComReservationStayListStatusBadge from '@/views/reservation/components/ComReservationStayListStatusBadge.vue'
import AddRoomIcon from '@/assets/svg/icon-add-plus-sign.svg'


const moment = inject('$moment')
const rs = inject("$reservation")
const selecteds = ref([])
const roomList = ref(JSON.parse(JSON.stringify(rs.reservationStays)))
console.log(roomList.value)
const selectStatus = ref()

const status = ref(JSON.parse(localStorage.getItem('edoor_setting')).reservation_status)

const items = [
    {
        label: 'Update',
        icon: 'pi pi-refresh',
        command: () => {
            toast.add({ severity: 'success', summary: 'Updated', detail: 'Data Updated', life: 3000 });
        }
    },
    {
        label: 'Delete',
        icon: 'pi pi-times',
        command: () => {
            toast.add({ severity: 'warn', summary: 'Delete', detail: 'Data Deleted', life: 3000 });
        }
    },
];

function onFilterSelectStatus(r){
    getRoomList(r)
}

function getRoomList(filter){
    if(filter && filter.length > 0){
        var list = []
        filter.forEach(f => {
            const data = rs.reservationStays.filter(r=>r.reservation_status == f.name)
            if(data.length > 0){
                data.forEach((d)=>{
                    list.push(d)
                })
            }
            
        });
        roomList.value = list;
    }else{
        roomList.value = rs.reservationStays
    }
}
 
</script>
<style scoped>
    .p-datatable > .p-datatable-wrapper {
        border-radius: 0.75rem !important;
    }
</style>