<template lang="">
    <ComReservationStayPanel title="Reservation Room List">

        <template #content> 
            <ComPlaceholder   :isNotEmpty="true">
                <div class="flex justify-end">
                    <div>
                        <div class="card flex justify-content-center">
                            <div class="filtr-rmm-list">
                                <ComSelect placeholder="Filter by Status" v-model="selectStatus" isMultipleSelect optionLabel="reservation_status" optionValue="name" :options="status" @onSelected="onFilterSelectStatus"></ComSelect>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="room-stay-list ress__list text-center mt-3 isMaster-guest"> 
                    <DataTable class="p-datatable-sm" v-model:selection="selecteds" sortField="name" :sortOrder="1" :value="rs.roomList" @row-dblclick="showReservationStayDetail" tableStyle="min-width: 50rem">
                        <Column selectionMode="multiple" headerStyle="width: 3rem"></Column>
                        <Column field="name" header="Res Stay#">
                        <template #body="slotProps">
                            <button @click="showReservationStayDetail(slotProps.data.name)" class="link_line_action w-auto">
                                {{slotProps.data.name}}
                            </button>
                        </template>
                        </column>
                        <Column header="Stay Date">
                            <template #body="slotProps">
                                <div>
                                    <span v-tooltip.top="'Arrival Date'">{{gv.dateFormat(slotProps.data.arrival_date)}}</span>
                                        <span class="mx-2">
                                            <i class="pi text-500 pi-arrow-right font-thin" style="font-size:8px;" />
                                        </span>
                                    <span v-tooltip.top="'Departure Date'">{{gv.dateFormat(slotProps.data.departure_date)}}</span>
                                </div>                               
                            </template>
                        </Column>
                        <Column header="Room">
                            <template #body="slotProps">
                                <div>
                                    <div v-for="(i, index)  in slotProps.data.room_type_alias.split(',').slice(0, 3)" :key="index" class="inline">
                                        {{(index != 0) ? ',' : ''}}
                                        <span v-tooltip.top="slotProps.data.room_types.split(',')[index]">{{i}}</span>/<span v-if="slotProps.data.rooms.split(',')[index] !== ''">
                                        {{ slotProps.data.rooms.split(',')[index] }}  
                                        </span>
                                        <button v-tooltip.top="'Assign Room'" @click="onAssignRoom(data)" class="link_line_action w-auto" v-else>
                                                <i class="pi pi-pencil"></i>
                                                <span v-if="slotProps.data.room_type_alias.split(',').length <= 1">
                                                Assign Room
                                                </span>
                                        </button>
                                    </div>
                                    <div v-if="slotProps.data.room_type_alias.split(',').length > 3"
                                        v-tooltip.top="{ value: `<div class='tooltip-room-stay'> ${rs.roomList?.map(stay => {
                                        return stay.room_types.split(',').slice(3).map((type, index) => `${type}/${(stay.rooms.split(',').slice(3))[index]}`).join('\n')
                                          })}</div>` , escape: true, class: 'max-w-30rem' }"
                                        class="inline rounded-xl px-2 bg-purple-cs w-auto ms-1 cursor-pointer">
                                        {{slotProps.data.room_type_alias.split(',').length - 3}} Mores
                                    </div>
                                </div>
                            </template>
                        </Column>
                        <Column header="Guest Name">
                            <template #body="slotProps">
                                <Button  class="p-0 link_line_action1 overflow-hidden text-overflow-ellipsis whitespace-nowrap max-w-12rem"  @click="onViewCustomerDetail(slotProps.data.guest_name)" link>
                                   {{slotProps.data.guest_name}}
                                </Button>
                            </template>
                        </Column>
                        <Column header="Pax">
                            <template #body="slotProps">
                                <span v-tooltip.top="'Adults'">{{slotProps.data.adult}}</span>/<span v-tooltip.top="'Children'">{{slotProps.data.child}}</span>
                            </template>
                        </Column>
                        <Column class="text-right res__room-list-right" header="Room Rate">
                            <template #body="slotProps">
                                <CurrencyFormat :value="slotProps.data.total_room_rate"/>
                            </template>
                        </Column>
                        <Column class="text-right res__room-list-right" header="Debit">
                            <template #body="slotProps">
                                <CurrencyFormat :value="slotProps.data.total_debit"/>
                            </template>
                        </Column>
                        <Column class="text-right res__room-list-right" header="Credit">
                            <template #body="slotProps">
                                <CurrencyFormat :value="slotProps.data.total_credit"/>
                            </template>
                        </Column>
                        <Column class="text-right res__room-list-right" header="Balance">
                            <template #body="slotProps">
                                <CurrencyFormat :value="slotProps.data.balance"/>
                            </template>
                        </Column>
                        <Column field="reservation_status" class="res__state__center text-center" header="Status">
                            <template #body="slotProps">
                                <ComReservationStatus :class="`data-${slotProps.data.reservation_status}`" class="border-round-3xl" :status-name="slotProps.data.reservation_status"/>
                            </template>
                        </Column>
                        <Column header="">
                            <template #body="slotProps">
                                <ComReservationStayMoreButton class="p-0" @onSelected="onSelected" @onClickDetail="showReservationStayDetail" :data="slotProps.data"/>
                            </template>
                        </Column>
                    </DataTable>
                </div>
                <div class="grid mt-3">
                    <div class="col-12 pl-2 py-0">
                        <div class="flex flex-column justify-between h-full">
                            <ComReservationStayListStatusBadge v-if="!(Object.entries(rs.reservation).length === 0)"/>
                        </div>
                    </div>
                   
                </div>
                <hr class="mt-3"/>
                <div class="pt-3">
                    <div class="flex justify-end gap-2">  
                        <Button @click="onCheckIn"  >Check In</Button>
                        <SplitButton class="spl__btn_cs sp" icon="pi pi-list" label="Mores" @click="moreOptions" :model="items" />
                        <Button class="border-1 conten-btn sp" @click="onAddRoomMore">
                            <img class="btn-add_comNote__icon me-2" :src="AddRoomIcon"/> Add More Room
                        </Button>
                        <Button class="border-1 conten-btn sp" label="Edit Booking" icon="pi pi-file-edit" />
                    </div>
                </div>  
            </ComPlaceholder>
        </template>
    </ComReservationStayPanel>
 
    <ComDialogNote :header="note.title" :visible="note.show" :loading="loading" @onOk="onSaveGroupStatus" @onClose="onCloseNote"/>
</template>
<script setup>
import {inject,ref,onMounted,useDialog, postApi,useConfirm,useToast} from '@/plugin'
import ComReservationStayPanel from '@/views/reservation/components/ComReservationStayPanel.vue';
import ComBoxStayInformation from '@/views/reservation/components/ComBoxStayInformation.vue';
import ComReservationStayMoreButton from '../components/ComReservationStayMoreButton.vue'
import ComReservationStayListStatusBadge from '@/views/reservation/components/ComReservationStayListStatusBadge.vue'
import AddRoomIcon from '@/assets/svg/icon-add-plus-sign-purple.svg'
import ReservationStayDetail from "@/views/reservation/ReservationStayDetail.vue"
import ComReservationStayAddMore from "./ComReservationStayAddMore.vue"
import ComConfirmCheckIn from '@/views/reservation/components/confirm/ComConfirmCheckIn.vue'
import GuestDetail from "@/views/guest/GuestDetail.vue"
const confirm = useConfirm()
const moment = inject('$moment')
const rs = inject("$reservation")
const gv = inject("$gv")
const selecteds = ref([])
const dialog = useDialog()
const selectStatus = ref()
const loading = ref(false)
const toast = useToast();
const socket = inject("$socket")
const frappe = inject("$frappe")
const call = frappe.call()
const note = ref({
    title: '',
    show: false,
    reservation_status:'' // No Show // Void // Cancel
})
function onViewCustomerDetail(name) {
    const dialogRef = dialog.open(GuestDetail, {
        data: {
            name: name
        },
        props: {
            header: 'Guest Detail',
            style: {
                width: '50vw',
            },
            breakpoints: {
                '960px': '75vw',
                '640px': '90vw'
            },
            modal: true
        },
        onClose: (options) => {
            console.log(options)
        }
    });
}
const status = ref(JSON.parse(localStorage.getItem('edoor_setting')).reservation_status)

const items = [
    {
        label: 'Group No Show',
        command: () => {
            onChangeStatus('No Show')
        }
    }, 
    {
        label: 'Group Cancel',
        command: () => {
            onChangeStatus('Cancelled')
        }
    },{
        label: 'Group Void',
        command: () => {
            onChangeStatus('void')
        }
    },
    {
        label: 'Group Check-In',
        command: ()=>{
            onGroupCheckIn(true)
        }
    },
    {
        label: 'Group Undo Check-In',
        command: ()=>{
            onGroupCheckIn(false)
        }
    },
    {
        label: 'Group Check Out',
        command: ()=>{
            onGroupCheckOut(true)
        }
    },
    {
        label: 'Group Undo Check Out',
        command: ()=>{
            onGroupCheckOut(false)
        }
    },
    {
        label: 'Group Build To Company',
    },
    {
        label: 'Group Build To Master Group ',
    },
    {
        label: 'Group Build To Guest',
    },
    {
        label: 'Group Build To Room and Tax to Company, Extra to Guest',
    }
];

function onFilterSelectStatus(r){
    rs.getRoomList(r)
}

function onCheckIn(){
    if (selecteds.value.length==0){
        toast.add({ severity: 'warn', summary: "Group Check In", detail:"Please select reservation stay to check in.", life: 3000 })
        return
    }
    const dialogRef = dialog.open(ComConfirmCheckIn, {
        data:{
            stays:selecteds.value
        },
        props: {
            header: 'Confirm Check In',
            style: {
                width: '450px',
            },
            modal: true,
            closeOnEscape: false
        },
        onClose: (options) => {
            const result = options.data;

            if (result) {
                rs.loading = true

                postApi("reservation.check_in", {
                    reservation: rs.reservation.name,
                    reservation_stays: selecteds.value.map(d => d["name"])
                }).then((result) => {
                    rs.loading = false
                    rs.LoadReservation(rs.reservation.name);
                    socket.emit("RefresheDoorDashboard", property.name);
                    
                

                })
                    .catch((err) => {
                        rs.loading = false
                    })
                }
        }


    })
}


function onChangeStatus(reservation_status){
    if(validateSelectReservation()){
        note.value.title = `${reservation_status}`
        note.value.show = true
        note.value.reservation_status = reservation_status
    }
    
}
function validateSelectReservation(){
    if(selecteds.value && selecteds.value.length > 0){
        return true
    }
    else{
        gv.toast('warn','Please select reservation stay.')
        return false
    }
}
function onSaveGroupStatus(txt){ 
    const data = {
        reservation: rs.reservation.name,
        stays:selecteds.value,
        status:note.value.reservation_status,
        note:txt
    } 
    postApi('reservation.update_reservation_status',data).then((r)=>{
        rs.LoadReservation(rs.reservation.name)
    })
}

function onCloseNote(){
    note.value.title = ''
    note.value.show = false
    note.value.reservation_status = ''
}
 

function onGroupCheckOut(is_not_undo = false){
    const isSelect = validateSelectReservation()
    if(isSelect){
        confirm.require({
        message: `Are you sure you want to${is_not_undo ? ' undo ' :' '}check out reservations?`,
        header: 'Check In',
        icon: 'pi pi-info-circle',
        acceptClass: 'p-button-success',
        accept: () => {
            const checkList = selecteds.value.map((r)=>r.name).join(',')
            postApi("reservation.check_out",{
                reservation: rs.reservation.name,
                reservation_stays: checkList,
                is_undo: !is_not_undo
            }).then((result) => {
                if(result){
                    rs.LoadReservation()
                }
            }).catch((error) => {
                //
            })

        }
    });
    }
}
function onAddRoomMore(){
    const dialogRef = dialog.open(ComReservationStayAddMore, {
        props: {
            header: 'Add more stay room',
            style: {
                width: '80vw',
            },
            maximizable: true,
            modal: true,
            closeOnEscape: false
        },
        onClose: (options) => {
            const data = options.data;
            if (data) {
                rs.LoadReservation(data.name)
            }
        }
    });
}
function showReservationStayDetail(selected) {
    let stayName = selected
    if(selected.data && selected.data.name){
        stayName = selected.data.name
    }
    const dialogRef = dialog.open(ReservationStayDetail, {
        data: {
            name: stayName
        },
        props: {
            header: 'Reservation Stay Detail',
            style: {
                width: '80vw',
            },
            maximizable: true,
            modal: true,
            closeOnEscape: false,
            position:"top"
        }, 
    });
}
 
</script>
<style scoped>
    .p-datatable > .p-datatable-wrapper {
        border-radius: 0.75rem !important;
    }
</style>