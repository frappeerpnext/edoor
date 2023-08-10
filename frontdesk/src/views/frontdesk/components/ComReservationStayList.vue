<template> 
    <ComDialogContent hideButtonOK :loading="loading" @onClose="onClose">
        <ComPlaceholder text="No Documents" :loading="loading" :isNotEmpty="data.length > 0">
            <DataTable :value="data" tableStyle="min-width: 50rem">
                <Column field="name" header="Document Number" headerClass="text-center" bodyClass="text-center">
                    <template #body="slotProps">
                        <Button class="p-0 link_line_action1" @click="onViewReservationDetail(slotProps.data.name)" link>
                            {{ slotProps.data.name }}
                        </Button>
                    </template>
                </Column>
                <Column field="reference_number" header="Ref. #"></Column>
                <Column field="guest_name" header="Guest Name">
                    <template #body="slotProps">
                        <Button class="p-0 link_line_action1" @click="onViewCustomerDetail(slotProps.data.guest)" link>
                            {{ slotProps.data.guest }} - {{ slotProps.data.guest_name }}
                        </Button>
                    </template>
                </Column>
                <Column field="business_source" header="Business Source"></Column>
                <Column field="rooms" header="Room No">
                    <template #body="slotProps">
                        <span v-if="slotProps.data.rooms_data">
                            <span v-for="(item, index) in JSON.parse(slotProps.data.rooms_data)" :key="index">
                                <span v-tooltip.top="item.room_type">{{ item.room_type_alias }}</span>/
                                <span v-if="item.room_number">
                                    <span>{{ item.room_number }}</span>{{ (index !== JSON.parse(slotProps.data.rooms_data).length - 1) ? ', ' : '' }}
                                </span>
                                <span v-else>
                                    <button v-tooltip.top="'Assign Room'" @click="onAssignRoom(item.name,slotProps.data.name)" class="link_line_action w-auto cursor-pointer">
                                        <i class="pi pi-pencil"></i>
                                        <span> Assign Room</span>
                                    </button>{{ (index !== JSON.parse(slotProps.data.rooms_data).length - 1) ? ', ' : '' }} 
                                </span>
                            </span>
                        </span>
                    </template>
                </Column>
                <Column header="Stay Date" headerClass="text-center" bodyClass="text-center">
                    <template #body="slotProps">
                        <span>{{ gv.dateFormat(slotProps.data.departure_date) }} &#8594; {{ gv.dateFormat(slotProps.data.arrival_date) }}</span>
                    </template>
                </Column> 
                <Column field="reservation_status" header="Status" headerClass="text-center" bodyClass="text-center">
                    <template #body="slotProps">
                        <ComReservationStatus :statusName="slotProps.data.reservation_status"/>
                    </template>
                </Column>
            </DataTable>
        </ComPlaceHolder>
    </ComDialogContent> 
</template>
<script setup>
import { inject, onMounted,useDialog,getDocList,ref,onUnmounted } from '@/plugin'
import GuestDetail from "@/views/guest/GuestDetail.vue"
import ReservationStayDetail from "@/views/reservation/ReservationStayDetail.vue"
import ComPlaceholder from "@/components/layout/components/ComPlaceholder.vue"
const dialogRef = inject("dialogRef")
const gv = inject("$gv")
const socket = inject("$socket")
const dialog = useDialog();
const loading = ref(false)
const data = ref([])
const pageState = ref({order_by:"modified", order_type:"desc",page:0,rows:20,totalRecords:0})


onMounted(() => { 
    loadData(); 
})

function loadData() {
    loading.value = true
    getDocList('Reservation Stay', {
        fields: [
            'name',
            'creation',
            'reference_number',
            'guest',
            'guest_name',
            'business_source',
            'rooms',
            'reservation_status',
            'arrival_date',
            'departure_date',
            'room_type_alias',
            'rooms_data'
        ],
        filters: dialogRef.value.data.filters
    }).then((doc) => {
        data.value = doc
        loading.value = false
    })
    .catch((error) => {
        loading.value = false
    })

}
socket.on("RefreshReservationStayList", (arg) => {

    if(arg ==property.name){
        loadData()
    }    

})
function onClose(){
    dialogRef.value.close()
}
function onViewReservationDetail(name) {
    const dialogRef = dialog.open(ReservationStayDetail, {
        data: {
            name: name
        },
        props: {
            header: 'Reservation Stay Detail',
            style: {
                width: '80vw',
            },
            breakpoints: {
                '960px': '100vw',
                '640px': '100vw'
            },
            modal: true,
            maximizable: true,
            closeOnEscape: false,
            position: 'top'
        },
        onClose: (options) => {
            console.log(options)
        }
    });
}



function onViewCustomerDetail(name) {
    const dialogRef = dialog.open(GuestDetail, {
        data: {
            name: name
        },
        props: {
            header: 'Guest Detail',
            style: {
                width: '75vw',
            },
            breakpoints: {
                '960px': '75vw',
                '640px': '90vw'
            },
            modal: true,
            maximizable: true,
            closeOnEscape: false,
            position: 'top'
        },
        onClose: (options) => {
            //
        }
    });
}

function onAssignRoom(room_name, reservation_stay){
    window.postMessage('assign_room|' + reservation_stay + '|' + room_name, '*')
}
onUnmounted(() => {
    socket.off("RefreshReservationStayList");
})
</script>