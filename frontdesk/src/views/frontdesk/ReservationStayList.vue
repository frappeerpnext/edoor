<template>
    <div class="flex-col flex" style="height: calc(100vh - 92px);">
        <div>
            <ComHeader isRefresh @onRefresh="Refresh()">
                <template #start>
                    <div :class="isMobile ? 'flex justify-content-between': ''">
<div class="text-xl md:text-2xl">Reservation Stay List</div>
                        <div class="w-50" v-if="isMobile">
<ComNewReservationMobileButton />
                        </div>
                    </div>
                </template>
                <template #end>
                    <template v-if="!isMobile">
                        <NewFITReservationButton />
                    <NewGITReservationButton />
                    </template>
                    
                </template>
            </ComHeader>
            <div class="mb-3 flex justify-between">
                <div class="flex gap-2">
                    <div v-if="!isMobile">
                        <span class="p-input-icon-left">
                            <i class="pi pi-search" />
                            <InputText v-model="filter.keyword" placeholder="Search" @input="onSearch" />
                        </span>
                    </div>
                    <div>
                        <Button icon="pi pi-sliders-h" class="content_btn_b" @click="advanceFilter" />
                    </div>
                </div>
                <div class="flex">
                    <div v-if="gv.isNotEmpty(filter, 'search_date_type')">
                        <Button class="content_btn_b" :label="isMobile ? 'Clear' : 'Clear Filter'" icon="pi pi-filter-slash"
                            @click="onClearFilter" />
                    </div>
                    <div class="px-2">
                        <ComOrderBy doctype="Reservation Stay" @onOrderBy="onOrderBy" />
                    </div>
                    <Button class="content_btn_b h-full px-3" @click="toggleShowColumn">
                        <ComIcon icon="iconEditGrid" height="16px"></ComIcon>
                    </Button>
                </div>
            </div>
        </div>
        <div class="overflow-auto h-full">
            <ComPlaceholder text="No Data" height="70vh" :loading="gv.loading" :is-not-empty="data?.length > 0">
                <DataTable  
                    class="res_list_scroll" 
                    :resizableColumns="true" 
                    columnResizeMode="expand" 
                    showGridlines
                    stateStorage="local" 
                    stateKey="table_reservation_stay_list_state" 
                    scrollable 
                    :reorderableColumns="true"
                    :value="data" 
                    :tableStyle="`min-width: ${width}%`" 
                    @row-dblclick="onViewReservationStayDetail">
                    <Column
                        v-for="c of columns.filter(r => selectedColumns.includes(r.fieldname) && r.label && (r.can_view_rate || 'Yes') == 'Yes')"
                        :key="c.fieldname" :field="c.fieldname" :header="c.label" :headerClass="c.header_class || ''"
                        :bodyClass="c.header_class || ''" :frozen="c.frozen">
                        <template #body="slotProps">
                            <Button v-if="c.fieldtype == 'Link'" class="p-0 link_line_action1"
                                @click="onOpenLink(c, slotProps.data)" link>
                                {{ slotProps.data[c.fieldname] }}
                                <span v-if="c.extra_field_separator" v-html="c.extra_field_separator"> </span>
                                <span v-if="c.extra_field">{{ slotProps.data[c.extra_field] }} </span>
                            </Button>
                            <span v-else-if="c.fieldtype == 'Date'">{{
                                moment(slotProps.data[c.fieldname]).format("DD-MM-YYYY") }} </span>
                            <ComTimeago v-else-if="c.fieldtype == 'Timeago'" :date="slotProps.data[c.fieldname]" />
                            <template v-else-if="c.fieldtype == 'Room'">
                                <div v-if="slotProps?.data && slotProps?.data?.rooms">
                                    <template v-for="(item, index) in slotProps.data.rooms.split(',')" :key="index">
                                        <span>{{ item }}</span>
                                        <span v-if="index != Object.keys(slotProps.data.rooms.split(',')).length - 1">,
                                        </span>
                                    </template>
                                </div>
                                <div @click="onAssignRoom(slotProps.data)" class="link_line_action w-auto" v-else>
                                    <i class="pi pi-pencil"></i>
                                    Assign Room
                                </div>
                            </template>
                            <template v-else-if="c.fieldname == 'owner' || c.fieldname == 'modified_by'">
                                <span>{{ slotProps.data[c.fieldname].split("@")[0] }}</span>
                            </template>
                            <CurrencyFormat v-else-if="c.fieldtype == 'Currency'" :value="slotProps.data[c.fieldname]" />
                            <span v-else-if="c.fieldtype == 'Status'"
                                class="px-2 rounded-lg text-white p-1px border-round-3xl"
                                :style="{ backgroundColor: slotProps.data['status_color'] }">{{ slotProps.data[c.fieldname]
                                }}
                            </span>
                            <span v-else-if="c.fieldname == 'reservation_type'"
                                v-tippy="slotProps.data[c.fieldname] == 'FIT' ? 'Free Independent Traveler' : 'Group Inclusive Tour'">
                                {{ slotProps.data[c.fieldname] }}
                            </span>
                            <span v-else>
                                {{ slotProps.data[c.fieldname] }}
                                <span v-if="c.extra_field_separator" v-html="c.extra_field_separator"> </span>
                                <span v-if="c.extra_field">{{ slotProps.data[c.extra_field] }} </span>
                            </span>
                        </template>
                    </Column>
                </DataTable>
            </ComPlaceholder>
        </div>
        <div>
            <Paginator class="p__paginator" v-model:first="pageState.activePage"  :rows="pageState.rows"
                :totalRecords="pageState.totalRecords" :rowsPerPageOptions="[20, 30, 40, 50]" @page="pageChange" :pageLinkSize="isMobile ? '2' : '5'">
                <template #start="slotProps">
                    <strong v-if="!isMobile">Total Records: <span class="ttl-column_re">{{ pageState.totalRecords }}</span></strong>
                </template>
            </Paginator>
        </div>
    </div>

    <OverlayPanel ref="opShowColumn" style="width:30rem;">
        <ComOverlayPanelContent ttl_header="mb-2" title="Show / Hide Columns" @onSave="OnSaveColumn" titleButtonSave="Save"
            @onCancel="onCloseColumn">
            <template #top>
                <span class="p-input-icon-left w-full mb-3">
                    <i class="pi pi-search" />
                    <InputText v-model="filter.search_field" placeholder="Search" class="w-full" />
                </span>
            </template>
            <div class="grid">
                <div class="col-6 py-1" v-for="(c, index) in getColumns.filter(r => r.label)" :key="index">
                    <Checkbox v-model="c.selected" :binary="true" :inputId="c.fieldname" />
                    <label :for="c.fieldname">{{ c.label }}</label>
                </div>
            </div>
            <template #footer-left>
                <Button class="border-none" icon="pi pi-replay" @click="onResetTable" label="Reset List" />
            </template>
        </ComOverlayPanelContent>
    </OverlayPanel>
    <OverlayPanel ref="showAdvanceSearch" style="max-width:70rem">
        <ComOverlayPanelContent title="Advance Filter" @onSave="onClearFilter" titleButtonSave="Clear Filter"
            icon="pi pi-filter-slash" :hideButtonClose="false" @onCancel="onCloseAdvanceSearch">
            <div class="grid">
                <div class="col-12" v-if="isMobile">
                        <span class="p-input-icon-left w-full">
                            <i class="pi pi-search" />
                            <InputText class="w-full" v-model="filter.keyword" placeholder="Search" @input="onSearch" />
                        </span>
                    </div>
                <div class="col-6 md:col-3">
                    <ComAutoComplete isFull optionLabel="business_source_type" optionValue="name"
                        v-model="filter.selected_business_source_type" @onSelected="onSearch"
                        placeholder="Business Source Type" doctype="Business Source Type" />
                </div>
                <div class="col-6 md:col-3">
                    <ComAutoComplete isFull groupFilterField="business_source_type"
                        :groupFilterValue="filter.selected_business_source_type" optionLabel="business_source"
                        optionValue="name" v-model="filter.selected_business_source" @onSelected="onSearch"
                        placeholder="Business Source" doctype="Business Source"
                        :filters="[['property', '=', property.name]]" />
                </div>
                <div class="col-6 md:col-3">
                    <ComSelect isFull v-model="filter.selected_reservation_type" @onSelected="onSearch"
                        placeholder="Reservation Type" :options="['GIT', 'FIT']" />
                </div>
                <div class="col-6 md:col-3">
                    <ComSelect isFull optionLabel="reservation_status" optionValue="name"
                        v-model="filter.selected_reservation_status" @onSelected="onSearch" placeholder="Reservation Status"
                        doctype="Reservation Status" />
                </div>
                <div class="col-6 md:col-3">
                    <ComSelect isFull optionLabel="building" optionValue="name" v-model="filter.selected_building"
                        @onSelected="onSearch" placeholder="Building" doctype="Building"
                        :filters="[['property', '=', property.name]]" />
                </div>
                <div class="col-6 md:col-3">
                    <ComSelect isFull optionLabel="room_type" optionValue="name" v-model="filter.selected_room_type"
                        @onSelected="onSearch" placeholder="Room Type" doctype="Room Type"
                        :filters="[['property', '=', property.name]]">
                    </ComSelect>
                </div>
                <div class="col-6 md:col-3">
                    <ComSelect isFull groupFilterField="room_type_id" :groupFilterValue="filter.selected_room_type"
                        optionLabel="room_number" optionValue="name" v-model="filter.selected_room_number"
                        @onSelected="onSearch" placeholder="Room Name" doctype="Room"
                        :filters="[['property', '=', property.name]]">
                    </ComSelect>
                </div>
                <div class="col-6 md:col-3">
                    <ComSelect isFull v-model="filter.search_date_type" :options="dataTypeOptions" optionLabel="label"
                        optionValue="value" placeholder="Search Date Type" :clear="false"
                        @onSelectedValue="onSelectFilterDate" :filters="[['property', '=', property.name]]"></ComSelect>
                </div>
                <div class="col-6" v-if="filter.search_date_type"> 
                    <Calendar :selectOtherMonths="true" hideOnRangeSelection dateFormat="dd-mm-yy" class="w-full"
                        v-model="filter.date_range" selectionMode="range" :manualInput="false" @date-select="onDateSelect"
                        placeholder="Select Date Range" showIcon />
                </div>
            </div>
        </ComOverlayPanelContent>
    </OverlayPanel>
</template>
<script setup>
import { inject, ref, reactive, useToast, getCount, getDocList, onMounted, getApi, computed, getDoc, onUnmounted } from '@/plugin'

import { useDialog } from 'primevue/usedialog';
import NewFITReservationButton from '@/views/reservation/components/NewFITReservationButton.vue';
import NewGITReservationButton from "@/views/reservation/components/NewGITReservationButton.vue"
import ComReservationStayAssignRoom from '@/views/reservation/components/ComReservationStayAssignRoom.vue';
import Paginator from 'primevue/paginator';
import ComOrderBy from '@/components/ComOrderBy.vue';
import { Timeago } from 'vue2-timeago'
import ComNewReservationMobileButton from "@/views/dashboard/components/ComNewReservationMobileButton.vue"
const isMobile = ref(window.isMobile) 
const showAdvanceSearch = ref()
const moment = inject("$moment")
const gv = inject("$gv")
const toast = useToast()
const opShowColumn = ref();
const width = ref(0)

const columns = ref([
    { fieldname: 'reservation', label: 'Reservation #', header_class: "text-center", fieldtype: "Link", post_message_action: "view_reservation_detail", default: true },
    { fieldname: 'name', label: 'Stay #', header_class: "text-center", fieldtype: "Link", post_message_action: "view_reservation_stay_detail", default: true },
    { fieldname: 'reference_number', label: 'Ref. #', },
    { fieldname: 'reservation_type', label: 'Res. Type', header_class: "text-center", default: true },
    { fieldname: 'reservation_date', label: 'Res. Date', header_class: "text-center", fieldtype: "Date", frozen: true, default: true },
    { fieldname: 'arrival_date', label: 'Arrival', fieldtype: "Date", header_class: "text-center", default: true },
    { fieldname: 'departure_date', label: 'Departure', fieldtype: "Date", header_class: "text-center", default: true },
    { fieldname: 'room_nights', label: 'Room Night(s)', header_class: "text-center", default: true },
    { fieldname: 'rooms', label: 'Rooms', fieldtype: "Room", header_class: "text-center", default: true },
    { fieldname: 'rate_type', label: 'Rate Type', default: false },
    { fieldname: 'room_types', label: 'Room Type', default: false },
    { fieldname: 'room_rate', label: 'Room Rate', default: false },
    { fieldname: 'adult', label: 'Pax(A/C)', extra_field: "child", extra_field_separator: "/", header_class: "text-center", default: true },
    { fieldname: 'guest', extra_field: "guest_name", extra_field_separator: "-", label: 'Guest', fieldtype: "Link", post_message_action: "view_guest_detail", default: true },
    { fieldname: 'guest_email', label: 'Email',  default: false },
    { fieldname: 'business_source', label: 'Business Source', default: true },
    { fieldname: 'adr', label: 'ADR', fieldtype: "Currency", header_class: "text-right", default: true, can_view_rate: window.can_view_rate ? 'Yes' : 'No' },
    { fieldname: 'total_room_rate', label: 'Total Room Rate', fieldtype: "Currency", header_class: "text-right", default: true, can_view_rate: window.can_view_rate ? 'Yes' : 'No' },
    { fieldname: 'total_debit', label: 'Debit', fieldtype: "Currency", header_class: "text-right", default: true, can_view_rate: window.can_view_rate ? 'Yes' : 'No' },
    { fieldname: 'total_credit', label: 'Credit', fieldtype: "Currency", header_class: "text-right", default: true, can_view_rate: window.can_view_rate ? 'Yes' : 'No' },
    { fieldname: 'balance', label: 'Balance', fieldtype: "Currency", header_class: "text-right", default: true, can_view_rate: window.can_view_rate ? 'Yes' : 'No' },
    { fieldname: 'owner', label: 'Created By' },
    { fieldname: 'creation', fieldtype: "Timeago", label: 'Creation', default: true },
    { fieldname: 'modified_by', label: 'Modified By' },
    { fieldname: 'modified', fieldtype: "Timeago", label: 'Last Modified', header_class: "text-center" },
    { fieldname: 'reservation_status', fieldtype: "Status", label: "Status", header_class: "text-center" },
    { fieldname: 'status_color' },
])

const getColumns = computed(() => {
    if (filter.value.search_field) {
        return columns.value.filter(r => (r.label || "").toLowerCase().includes(filter.value.search_field.toLowerCase())).sort((a, b) => a.label.localeCompare(b.label));
    } else {
        return columns.value.filter(r => r.label).sort((a, b) => a.label.localeCompare(b.label));
    }
})
const selectedColumns = ref([]);

const toggleShowColumn = (event) => {
    opShowColumn.value.toggle(event);
}

function OnSaveColumn(event) {
    selectedColumns.value = columns.value.filter(r => r.selected).map(x => x.fieldname)
    pageState.value.selectedColumns = selectedColumns.value
    localStorage.setItem("page_state_reservation_stay", JSON.stringify(pageState.value))
    opShowColumn.value.toggle(event);
}

function onResetTable() {
    localStorage.removeItem("page_state_reservation_stay")
    localStorage.removeItem("table_reservation_stay_list_state")
    window.location.reload()

}

const onCloseColumn = () => {
    opShowColumn.value.hide()
}

const dataTypeOptions = reactive([
    { label: 'Search Date', value: '' },
    { label: 'Arrival Date', value: 'arrival_date' },
    { label: 'Departure Date', value: 'departure_date' },
    { label: 'Reservation Date', value: 'reservation_date' },
    { label: 'Cancel/No Show/Voided Date', value: 'cancelled_date' }
])
const data = ref([])

const filter = ref({})
let dateRange = reactive({
    start: '',
    end: ''
})
const pageState = ref({ order_by: "modified", order_type: "desc", page: 0, rows: 20, totalRecords: 0, activePage: 0 })

const working_date = ref('')
const property = JSON.parse(localStorage.getItem("edoor_property"))
const dialog = useDialog();

function onOpenLink(column, data) {
    window.postMessage(column.post_message_action + "|" + data[column.fieldname], '*')
}


const Refresh = debouncer(() => {
    loadData();
    pageState.value.page = 0
}, 500);

function onDateSelect() {
  if (filter.value.date_range && filter.value.date_range[0] && filter.value.date_range[1]) {
    dateRange.start = moment(filter.value.date_range[0]).format("YYYY-MM-DD")
    dateRange.end = moment(filter.value.date_range[1]).format("YYYY-MM-DD")
    loadData()
  }
}
function pageChange(page) {
    pageState.value.page = page.page
    pageState.value.rows = page.rows

    loadData()
}

function loadData(show_loading = true) {
    gv.loading = show_loading
    let filters = [
        ["Reservation Stay", "property", '=', property.name]
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
    if (filter.value?.selected_reservation_type) {
        filters.push(["reservation_type", '=', filter.value.selected_reservation_type])
    }

    if (filter.value?.selected_room_type) {
        filters.push(["Reservation Stay Room", "room_type_id", "=", filter.value.selected_room_type])
    }
    if (filter.value?.selected_room_number) {
        filters.push(["Reservation Stay Room", "room_id", "=", filter.value.selected_room_number])
    }

    if (filter.value?.search_date_type && filter.value.date_range != null) {
        filters.push([filter.value.search_date_type, '>=', dateRange.start])
        filters.push([filter.value.search_date_type, '<=', dateRange.end])
    }

    let fields = [...columns.value.map(r => r.fieldname), ...columns.value.map(r => r.extra_field)]
    fields = [...fields, ...selectedColumns.value]

    fields = [...new Set(fields.filter(x => x))]

    getDocList('Reservation Stay', {
        fields: fields,
        orderBy: {
            field: '`tabReservation Stay`.' + pageState.value.order_by,
            order: pageState.value.order_type,
        },
        filters: filters,
        limit_start: ((pageState.value?.page || 0) * (pageState.value?.rows || 20)),
        limit: pageState.value?.rows || 20,
    })
        .then((doc) => {
            data.value = doc
            gv.loading = false
        })
        .catch((error) => {
            gv.loading = false
            toast.add({ severity: 'error', summary: 'Error Message', detail: error, life: 3000 });
        });
    getTotalRecord(filters)

    localStorage.setItem("page_state_reservation_stay", JSON.stringify(pageState.value))

}
function getTotalRecord(filters) {

    getCount('Reservation Stay', filters)
        .then((count) => pageState.value.totalRecords = count || 0)

}
function onOrderBy(data) {
    pageState.value.order_by = data.order_by
    pageState.value.order_type = data.order_type
    pageState.value.page = 0
    loadData()

}

function onSelectFilterDate(event) {
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


getApi('frontdesk.get_working_day', {
    property: JSON.parse(localStorage.getItem("edoor_property")).name
}).then((r) => {
    working_date.value = r.message?.date_working_day
})

const actionRefreshData = async function (e) {
    if (e.isTrusted && typeof (e.data) != 'string') {
        if(e.data.action=="ReservationStayList"){
            setTimeout(()=>{
                loadData(false)
            },1000*2)
            
        }
    };
}

onMounted(() => {
    if(window.isMobile){
        let elem = document.querySelectorAll(".p-dialog");
        if (elem){
            elem = elem[elem.length-1]
            elem?.classList.add("p-dialog-maximized"); // adds the maximized class
        }
    }
    width.value = 100
    window.addEventListener('message', actionRefreshData, false); 
    let state = localStorage.getItem("page_state_reservation_stay")
    if (state) {
        state = JSON.parse(state)
        state.page = 0
        pageState.value = state
        if (state.selectedColumns) {
            selectedColumns.value = state.selectedColumns

        } else {
            selectedColumns.value = columns.value.filter(r => r.default).map(x => x.fieldname)
        }
    } else {
        selectedColumns.value = columns.value.filter(r => r.default).map(x => x.fieldname)
    }
    columns.value.forEach(r => {
        r.selected = selectedColumns.value.includes(r.fieldname)
    });
    loadData()
    getApi("frontdesk.get_meta", { doctype: "Reservation Stay" }).then((result) => {
        result.message.fields.filter(r => r.in_list_view == 1 && !columns.value.map(x => x.fieldname).includes(r.fieldname)).forEach(r => {
            let header_class = ""

            if (["Date", "Int"].includes(r.fieldtype)) {
                header_class = "text-center"
            } else if (["Currency"].includes(r.fieldtype)) {
                header_class = "text-right"
            }

            columns.value.push({
                fieldname: r.fieldname,
                label: r.label,
                fieldtype: r.fieldtype.toLowerCase(),
                header_class: header_class,
                selected: selectedColumns.value.includes(r.fieldname)
            })
        })
    })

})

const advanceFilter = (event) => {
    showAdvanceSearch.value.toggle(event);
}
const onClearFilter = () => {
    filter.value = {}
    loadData()
    showAdvanceSearch.value.hide()
}
const onCloseAdvanceSearch = () => {
    showAdvanceSearch.value.hide()
}

function onAssignRoom(data) {
    getDoc("Reservation Stay", data.name).then(doc => {
        const stay_room = doc.stays.find(r => !r.room_id)
        if (stay_room) {
            dialog.open(ComReservationStayAssignRoom, {
                data: { stay_room: stay_room },
                props: {
                    header: `Assign Room`,
                    style: {
                        width: '80vw',
                    },
                    modal: true,
                    closeOnEscape: false,
                    position: 'top',
                    breakpoints:{
                '960px': '80vw',
                '640px': '100vw'
            },
                },
                onClose: (options) => {
                    if (options.data && options.data.message) {
                        setTimeout(() => {
                            rs.getReservationDetail(options.data.message.name)
                        }, 1500);
                    }
                }
            })
        }
    }) 
}

onUnmounted(() => {
    window.removeEventListener('message', actionRefreshData, false);
})
</script>