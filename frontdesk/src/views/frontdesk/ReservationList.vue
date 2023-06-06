<template>
    <div>
        <ComHeader isRefresh @onRefresh="Refresh()">
            <template #start>
                <div>Reservation List</div>
            </template>
            <template #end>
                <NewFITReservationButton />
            </template>
        </ComHeader>
        <div>

            <span class="p-input-icon-left">
                <i class="pi pi-search" />
                <InputText v-model="filter.keyword" placeholder="Search" @input="onSearch" />
            </span>

            <ComSelect optionLabel="business_source_type" optionValue="name" v-model="filter.selected_business_source_type"
                @onSelected="onSearch" placeholder="Business Source Type" doctype="Business Source Type" />

            <ComSelect isFilter groupFilterField="business_source_type"
                :groupFilterValue="filter.selected_business_source_type" optionLabel="business_source" optionValue="name"
                v-model="filter.selected_business_source" @onSelected="onSearch" placeholder="Business Source"
                doctype="Business Source" />

            <ComSelect optionLabel="reservation_status" optionValue="name" v-model="filter.selected_reservation_status"
                @onSelected="onSearch" placeholder="Reservation Status" doctype="Reservation Status" />

            <ComSelect optionLabel="building" optionValue="name" v-model="filter.selected_building" @onSelected="onSearch"
                placeholder="Building" doctype="Building" />

            <ComSelect isFilter optionLabel="room_type" optionValue="name" v-model="filter.selected_room_type"
                @onSelected="onSearch" placeholder="Room Type" doctype="Room Type"></ComSelect>

            <ComSelect isFilter groupFilterField="room_type_id" :groupFilterValue="filter.selected_room_type"
                optionLabel="room_number" optionValue="name" v-model="filter.selected_room_number" @onSelected="onSearch"
                placeholder="Room Name" doctype="Room"></ComSelect>

            <ComSelect v-model="filter.search_date_type" :options="dataTypeOptions" optionLabel="label" optionValue="value"
                placeholder="Seach Date Type" :clear="false" @onSelectedValue="onSelectFilterDate($event)"></ComSelect>

            <Calendar hideOnRangeSelection v-if="filter.search_date_type" dateFormat="dd-MM-yy" v-model="filter.date_range"
                selectionMode="range" :manualInput="false" @date-select="onDateSelect" placeholder="Select Date Range" />
        </div>

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
    </div>
</template>
<script setup>
import { inject, ref, reactive, useToast } from '@/plugin'
import GuestDetail from "@/views/guest/GuestDetail.vue"
import ReservationDetail from "@/views/reservation/ReservationDetail.vue"
import { useDialog } from 'primevue/usedialog';
import NewFITReservationButton from '../reservation/components/NewFITReservationButton.vue';

const dates = ref()
const frappe = inject('$frappe')
const moment = inject("$moment")
const gv = inject("$gv")
const toast = useToast()

const dataTypeOptions = reactive([
    { label: 'Search Date', value: '' },
    { label: 'Arrival Date', value: 'arrival_date' },
    { label: 'Departure Date', value: 'departure_date' },
    { label: 'Reservation Date', value: 'reservation_date' }])
const data = ref([])
const db = frappe.db();
const call = frappe.call();
const filter = ref({})
let dateRange = reactive({
    start: '',
    end: ''
})
const working_date = ref('')
const property = JSON.parse(localStorage.getItem("edoor_property"))
const dialog = useDialog();
loadData();


function Refresh() {
    loadData()
}
function onDateSelect() {
    if (filter.value.date_range && filter.value.date_range[0] && filter.value.date_range[1]) {
        dateRange.start = moment(filter.value.date_range[0]).format("YYYY-MM-DD")
        dateRange.end = moment(filter.value.date_range[1]).format("YYYY-MM-DD")
        loadData()
    }
}
function loadData() {
    gv.loading = true
    let filters = [
        ["property", '=', property.name]
    ]
    if (filter.value?.keyword) {
        filters.push(["keyword", 'like', '%' + filter.value.keyword + '%'])
    }
    if (filter.value?.selected_business_source_type) {
        filters.push(["business_source_type", '=', filter.value.selected_business_source_type])
    }
    if (filter.value?.selected_business_source) {
        filters.push(["business_source", '=', filter.value.selected_business_source])
    }
    if (filter.value?.selected_reservation_status) {
        filters.push(["reservation_status", '=', filter.value.selected_reservation_status])
    }

    if (filter.value?.selected_room_type) {
        filters.push(["business_source", '=', filter.value.selected_room_type])
    }
    if (filter.value?.selected_room_number) {
        filters.push(["reservation_status", '=', filter.value.selected_room_number])
    }

    if (filter.value?.search_date_type && filter.value.date_range != null) {
        filters.push([filter.value.search_date_type, '>=', dateRange.start])
        filters.push([filter.value.search_date_type, '<=', dateRange.end])
    }
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
        filters: filters
    })
        .then((doc) => {
            data.value = doc
            gv.loading = false
        })
        .catch((error) => {
            gv.loading = false
            toast.add({ severity: 'error', summary: 'Error Message', detail: error, life: 3000 });
        });

}
function onSelectFilterDate(event) {
    filter.value.search_date_type = event
    if (filter.value.search_date_type == '')
        filter.value.date_range = null
    loadData()
}



const onSearch = debouncer(() => {
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
                width: '80vw',
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

call.get('edoor.api.frontdesk.get_working_day', {
    property: JSON.parse(localStorage.getItem("edoor_property")).name
}).then((r) => {
    working_date.value = r.message?.date_working_day
    // const startDate = moment(working_date.value)
    // const endDate = moment(working_date.value).add(1, 'days')
    // filter.value.date_range = [new Date(startDate), new Date(endDate)];
})
</script>