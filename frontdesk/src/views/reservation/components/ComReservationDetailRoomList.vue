<template lang="">
    <ComReservationStayPanel title="Reservation Room List">
        <template #content>
            <ComPlaceholder :isNotEmpty="true">
                <div class="flex justify-end sm:overflow-hidden">
                    <div>
                        <div class="card flex justify-content-center">
                            <div class="filtr-rmm-list">
                                <ComSelect :maxSelectedLabels="10" mClass="max-w-35rem" maxWidth="35rem" placeholder="Filter by Status" v-model="rs.filterStatusRooms" isMultipleSelect optionLabel="reservation_status" optionValue="name" :options="status" @onSelected="onFilterSelectStatus">
                                </ComSelect>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="room-stay-list ress__list text-center mt-3 isMaster-guest"> 
                    <DataTable :rowClass="rowClass" class="p-datatable-sm" v-model:selection="rs.selecteds" sortField="name" :sortOrder="1" :value="rs.roomList" @row-dblclick="showReservationStayDetail" tableStyle="min-width: 50rem">
                        <Column selectionMode="multiple" headerStyle="width: 3rem"></Column>
                        <Column field="name" :header="$t('RES STAY #')">
                        <template #body="slotProps">
                            <button @click="showReservationStayDetail(slotProps.data.name)" class="link_line_action w-auto">
                                {{slotProps.data.name}}
                            </button>
                        </template>
                        </column>
                        <Column :header="$t('Stay Date')" headerClass="text-center" bodyClass="text-center">
                            <template #body="slotProps">
                                <div>
                                    <span v-tippy="$t('Arrival Date')">{{gv.dateFormat(slotProps.data.arrival_date)}}</span>
                                    &#8594;
                                    <span v-tippy="$t('Departure Date')">{{gv.dateFormat(slotProps.data.departure_date)}}</span>
                                </div>                               
                            </template>
                        </Column>
                        <Column :header="$t('Nights')" headerClass="text-center" bodyClass="text-center">
                        <template #body="slotProps">
                            <div>
                                <span>
                                    {{ slotProps.data.room_nights || 0 }}
                                </span>
                            </div>
                        </template></Column>
                        <Column :header="$t('Room')">
                            <template #body="slotProps">
                                <div> 
                                    <span v-for="(i, index) in JSON.parse(slotProps.data.rooms_data)" :key="index">
                                        <span v-if="index < 3">
                                            {{(index != 0) ? ',' : ''}}
                                            <span v-tippy="i.room_type">{{i.room_type_alias}}</span>/
                                            <span v-if="i.room_number">
                                                {{ i.room_number }}  
                                            </span>
                                            <button v-tippy="$t('Assign Room')" @click="onAssignRoom(i.name,slotProps.data.name)" class="link_line_action w-auto" v-else>
                                                <!-- <i class="pi pi-pencil"></i> -->
                                                <span>
                                                   {{$t('Assign')}}  {{i.reservation_stay}}
                                                </span> 
                                            </button>
                                        </span>
                                    </span>
                                    <span v-if="JSON.parse(slotProps.data.rooms_data).length > 3"
                                        v-tippy="{ value: getTooltip(slotProps.data) , escape: true, class: 'max-w-30rem' }"
                                        class="inline rounded-xl px-2 bg-purple-cs w-auto ms-1 cursor-pointer">
                                        {{JSON.parse(slotProps.data.rooms_data).length - 3}} {{$t('Mores')}} 
                                    </span>
                                </div>
                            </template>
                        </Column>
                        <Column :header="$t('Guest Name')" class="white-space-nowrap">
                            <template #body="slotProps">
                                <Button  class="p-0 link_line_action1 overflow-hidden text-overflow-ellipsis whitespace-nowrap max-w-12rem"  @click="onViewCustomerDetail(slotProps.data.guest)" link>
                                   {{slotProps.data.guest_name}}
                                </Button>
                            </template>
                        </Column>
                        <Column :header="$t('Pax(A/C)')">
                            <template #body="slotProps">
                                <span v-tippy="$t('Adults')">{{slotProps.data.adult}}</span>/<span v-tippy ="$t('Children')">{{slotProps.data.child}}</span>
                            </template>
                        </Column>
                        <Column v-if="can_view_rate" class="text-right res__room-list-right" :header="$t('ADR')">
                            <template #body="slotProps">
                                <CurrencyFormat :value="slotProps.data.adr"/>
                            </template>
                        </Column>
                        <Column v-if="can_view_rate"  class="text-right res__room-list-right white-space-nowrap" :header="$t('Total Rate')">
                            <template #body="slotProps">
                                <CurrencyFormat :value="slotProps.data.total_room_rate"/>
                            </template>
                        </Column>
                        <Column v-if="can_view_rate" class="text-right res__room-list-right" :header="$t('Debit')">
                            <template #body="slotProps">
                                <CurrencyFormat :value="slotProps.data.total_debit"/>
                            </template>
                        </Column>
                        <Column v-if="can_view_rate"   class="text-right res__room-list-right" :header="$t('Credit')">
                            <template #body="slotProps">
                                <CurrencyFormat :value="slotProps.data.total_credit"/>
                            </template>
                        </Column>
                        <Column v-if="can_view_rate"  class="text-right res__room-list-right" :header="$t('Balance')">
                            <template #body="slotProps">
                                <CurrencyFormat :value="slotProps.data.total_debit - slotProps.data.total_credit "/>
                            </template>
                        </Column>
                        <Column field="reservation_status" class="res__state__center text-center" :header="$t('Status')">
                            <template #body="slotProps">
                                <ComReservationStatus :class="`data-${slotProps.data.reservation_status}`" class="border-round-3xl " :status-name="slotProps.data.reservation_status">
                                    <div v-tippy="$t('Paid by Master Room')" v-if="slotProps.data.paid_by_master_room && slotProps.data.is_active_reservation && !(slotProps.data.is_master)" class="px-1 border-circle bg-tran-black  inline">
                                        <ComIcon class="inline" icon="BilltoMasterRoomWhite" style="height:12px;" ></ComIcon>
                                    </div>
                                    <div v-tippy="$t('Allow Post To City Ledger')" v-if="slotProps.data.allow_post_to_city_ledger && slotProps.data.is_active_reservation" style="width:19.31px;" class="px-1 border-circle bg-tran-black ms-1 inline-block">
                                        <ComIcon class="inline" icon="IconBillToCompanywhite" style="height:12px;" ></ComIcon>
                                    </div>
                                    <div v-tippy="( slotProps.data.require_drop_off ? $t('Require Drop Off') : '' ) + (slotProps.data.require_pickup ? $t(' Require Pickup ') : '' )" v-if="(slotProps.data.require_drop_off || slotProps.data.require_pickup) && slotProps.data.is_active_reservation" style="width:19.31px;" class="px-1 border-circle bg-tran-black ms-1 inline-block">
                                        <i class="pi pi-car text-white" style="font-size: 10px;" />
                                    </div>
                                </ComReservationStatus>
                            </template>
                        </Column>
                        <Column header="">
                            <template #body="slotProps">
                                <ComReservationStayMoreButton class="p-0" @onSelected="onSelected" @onClickDetail="showReservationStayDetail" :data="slotProps.data"/>
                            </template>
                        </Column>
                        <template #empty>
                            <div class="p-4 text-center">
                                <div><img :src="iconNoData" style="width: 80px; margin: 0 auto;"></div>
                                <div class="mt-2 text-sm italic text-gray-400">{{$t('Data Empty')}}</div>
                            </div>
                        </template>
                    </DataTable>
                </div>
                <div class="grid mt-3">
                    <div class="col-12 pl-2 py-0">
                        <div class="flex flex-column justify-between h-full">
                            <ComReservationStayListStatusBadge v-if="rs.reservation && Object.keys(rs.reservation).length !== 0"/>
                        </div>
                    </div>
                </div>
            </ComPlaceholder>
        </template>
    </ComReservationStayPanel> 
</template>
<script setup>
import { inject, ref, useDialog } from '@/plugin'
import ComReservationStayPanel from '@/views/reservation/components/ComReservationStayPanel.vue';
import ComReservationStayMoreButton from '../components/ComReservationStayMoreButton.vue'
import ComReservationStayListStatusBadge from '@/views/reservation/components/ComReservationStayListStatusBadge.vue'
import ReservationStayDetail from "@/views/reservation/ReservationStayDetail.vue"
import iconNoData from '@/assets/svg/icon-no-notic-r-comment.svg'
import {i18n} from '@/i18n';
const { t: $t } = i18n.global; 
const rs = inject("$reservation")
const gv = inject("$gv")
const dialog = useDialog()
const moment = inject('$moment')
const can_view_rate = ref(window.can_view_rate)

function onViewCustomerDetail(name) {
    window.postMessage('view_guest_detail|' + name, '*')
}

const status = ref(JSON.parse(localStorage.getItem('edoor_setting')).reservation_status)
status.value.push(
    {
        "reservation_status": "Pickup",
        "name": "require_pickup",
        "sort_order": 0
    },
    {
        "reservation_status": "Drop Off",
        "name": "require_drop_off",
        "sort_order": 0,
    }
    
)
const rowClass = (data) => {

    return [{ 'bg-purple-100': data.is_master === 1 }];
};

function getTooltip(p) {
    var data = JSON.parse(p.rooms_data)
    var html = ''
    var index = 0
    data.forEach(e => {
        index = index + 1
        if (index > 3) {
            html = html + `${e.room_type}/${e.room_number ? e.room_number : ''}\n`
        }

    });
    return `<div class='tooltip-room-stay'>${html}</div>`

}

function onFilterSelectStatus(r) {
    rs.getRoomList(r)
}

function showReservationStayDetail(selected) {
    let stayName = selected
    if (selected.data && selected.data.name) {
        stayName = selected.data.name
    }
    if  (stayName){
        window.postMessage("view_reservation_stay_detail|" + stayName,"*")
    }
    
}
function onAssignRoom(room_name, reservation_stay) {
    window.postMessage('assign_room|' + reservation_stay + '|' + room_name, '*')
}
</script>
<style scoped>
.p-datatable>.p-datatable-wrapper {
    border-radius: 0.75rem !important;
}
</style>