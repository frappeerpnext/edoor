<template>
    <h1>Reservation List</h1>
 
 
    <span class="p-input-icon-left">
        <i class="pi pi-search" />

        <InputText v-model="keyword_document_number" placeholder="Search" @input="onSearchByDocumentNumber" />
        <Dropdown v-model="filter.selected_business_source" :options="filter.business_source_list" optionLabel="name"
            placeholder="Business Source" class="w-full md:w-14rem" />
    </span>


<NewFITReservationButton/>
    <hr />
    <DataTable :value="data" tableStyle="min-width: 50rem">
        <Column field="name" header="Document Number">
            <template #body="slotProps">
                <Button @click="onViewReservationDetail(slotProps.data.name)" link>
                    {{ slotProps.data.name }}
                </Button>
            </template>
        </Column>
        <Column field="reference_number" header="Ref. #"></Column>
        <Column field="guest_name" header="Guest Name">
            <template #body="slotProps">
                <Button @click="onViewCustomerDetail(slotProps.data.guest)" link>
                    {{ slotProps.data.guest }} - {{ slotProps.data.guest_name }}
                </Button>
            </template>
        </Column>
        <Column field="business_source" header="Business Source"></Column>
        <Column field="room_numbers" header="Room No"></Column>
        <Column field="arrival_date" header="Arrival">
            <template #body="slotProps">
                {{ moment(slotProps.data.arrival_date).format("DD/MM/YYYY") }}
            </template>
        </Column>
        <Column field="departure_date" header="Departure">
            <template #body="slotProps">
                {{ moment(slotProps.data.departure_date).format("DD/MM/YYYY") }}
            </template>
        </Column>
        <Column field="guest_type" header="Guest Type"></Column>
        <Column field="reservation_status" header="Status"></Column>
    </DataTable> 
    <button @click="Refresh">Refersh</button>
</template>
<script setup>
import { inject, ref, reactive } from '@/plugin'
import GuestDetail from "@/views/guest/GuestDetail.vue"
import ReservationDetail from "@/views/reservation/ReservationDetail.vue"
import { useDialog } from 'primevue/usedialog';
import NewFITReservationButton from '../reservation/components/NewFITReservationButton.vue';
 

const frappe = inject('$frappe')
const moment = inject("$moment")
 

const data = ref([])
const db = frappe.db();
const keyword_document_number = ref('')
const filter = reactive({
    business_source_list: [],
    selected_business_source: {}
})

const property = JSON.parse(localStorage.getItem("edoor_property"))

const dialog = useDialog();
loadData();
getBusinessScoure();

function Refresh(){
    loadData()
}
function loadData() {
    db.getDocList('Reservation', {
        fields: [
            'name',
            'creation',
            'reference_number',
            'guest',
            'guest_name',
            'business_source',
            'room_numbers',
            'reservation_status',
            'arrival_date',
            'departure_date',
            'guest_type'
        ],
        filters: [
            ["keyword", 'like', '%' + keyword_document_number.value + '%'],
            ["property",'=',property.name]
        ],

    })
        .then((doc) => {
            data.value = doc
        })
        .catch((error) => console.error(error));

}

function getBusinessScoure() {
    db.getDocList('Business Source', {
        fields: ['name']
    }).then((doc) => {
        filter.business_source_list = doc
    }).catch((error) => console.error(error));
}


const onSearchByDocumentNumber = debouncer(() => {
    loadData();
}, 500);


function debouncer(fn, delay) {
    var timeoutID = null;
    return function () {
        clearTimeout(timeoutID);
        var args = arguments;
        var that = this;
        timeoutID = setTimeout(function () {
            fn.apply(that, args);
        }, delay);
    };
}

 
function onViewReservationDetail(name) {
    const dialogRef = dialog.open(ReservationDetail, {
        data: {
            name: name
        },
        props: {
            header: 'Reservation Detail',
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

 
</script>