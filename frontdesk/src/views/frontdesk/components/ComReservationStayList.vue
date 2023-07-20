<template> 
    <ComDialogContent hideButtonOK :loading="loading" @onClose="onClose">
        <DataTable :value="data" tableStyle="min-width: 50rem">
            <Column field="name" header="Document Number">
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
            <Column field="rooms" header="Room No"></Column>
            <Column field="arrival_date" header="Arrival">
                <template #body="slotProps">
                    <span>{{ gv.dateFormat(slotProps.data.arrival_date) }}</span>
                </template>
            </Column>
            <Column field="departure_date" header="Departure">
                <template #body="slotProps">
                    <span>{{ gv.dateFormat(slotProps.data.departure_date) }}</span>
                </template>
            </Column> 
            <Column field="reservation_status" header="Status">
                <template #body="slotProps">
                    <ComReservationStatus :statusName="slotProps.data.reservation_status"/>
                </template>
            </Column>
        </DataTable>
    </ComDialogContent> 
</template>
<script setup>
import { inject, onMounted,useDialog,getDocList,ref } from '@/plugin'
import GuestDetail from "@/views/guest/GuestDetail.vue"
import ReservationStayDetail from "@/views/reservation/ReservationStayDetail.vue"
const dialogRef = inject("dialogRef")
const gv = inject("$gv")
const dialog = useDialog();
const loading = ref(false)
const data = ref([])
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
            'departure_date'
        ],
        filters: dialogRef.value.data.filters
    }).then((doc) => {
        console.log(doc)
        data.value = doc
        console.log(data.value)
        loading.value = false
    })
    .catch((error) => {
        loading.value = false
    })

}
function onClose(){
    dialogRef.value.close()
}
function onViewReservationDetail(name) {
    const dialogRef = dialog.open(ReservationStayDetail, {
        data: {
            name: name
        },
        props: {
            header: 'Reservation Detail',
            style: {
                width: '80vw',
            },
            breakpoints: {
                '960px': '100vw',
                '640px': '100vw'
            },
            modal: true,
            maximizable: true,
            closeOnEscape: false
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
                width: '50vw',
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

</script>