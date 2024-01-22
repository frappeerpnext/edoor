<template>
    <div class="flex-col flex" style="height: calc(100vh - 92px);">
        <div>
            <ComHeader isRefresh @onRefresh="Refresh()">
                <template #start>
                    <div class="text-2xl">Reservation List</div>
                </template>
                <template #end>
                    <NewFITReservationButton />
                    <NewGITReservationButton />
                </template>
            </ComHeader>
            <div class="mb-3 flex justify-between">
                <div class="flex gap-2">
                    <div>
                        <span class="p-input-icon-left">
                            <i class="pi pi-search" />
                            <InputText v-model="filter.keyword" placeholder="Search" @input="onSearch" />
                        </span>
                    </div>
                    <div>
                        <Button icon="pi pi-sliders-h" class="content_btn_b" @click="advanceSearch" />
                    </div>
                    <div v-if="gv.isNotEmpty(filter, 'search_date_type')">
                        <Button class="content_btn_b" label="Clear Filter" icon="pi pi-filter-slash" @click="onClearFilter" />
                    </div>
                   
                </div>
                <div class="flex gap-2">
                    <div>
                        <ComOrderBy doctype="Reservation" @onOrderBy="onOrderBy" />
                    </div>
                    <Button class="content_btn_b h-full px-3" @click="toggleShowColumn">
                        <ComIcon icon="iconEditGrid" height="16px"></ComIcon>
                    </Button>
                </div>
            </div>
        </div>
        <div class="overflow-auto h-full">
            <ComPlaceholder text="No Data" height="70vh" :loading="gv.loading" :is-not-empty="data.length > 0">
                <DataTable 
                class="res_list_scroll" 
                :resizableColumns="true" 
                columnResizeMode="expand" 
                showGridlines
                stateStorage="local" 
                stateKey="table_reservation_list_state" 
                :reorderableColumns="true" 
                :value="data"
                tableStyle="min-width: 50rem" 
                @row-dblclick="onViewReservationStayDetail">
                    <Column  v-for="c of columns.filter(r => selectedColumns.includes(r.fieldname) && r.label && (r.can_view_rate || 'Yes')=='Yes')" :key="c.fieldname"
                        :field="c.fieldname" :header="c.label"
                        :headerClass="[c.header_class, 'white-space-nowrap'] || 'white-space-nowrap'"
                        :bodyClass="c.header_class || ''" :frozen="c.frozen"
                        >
                        <template #body="slotProps">
                            <Button v-if="c.fieldtype == 'Link'" class="p-0 link_line_action1"
                                @click="onOpenLink(c, slotProps.data)" link>
                                {{ slotProps.data[c.fieldname] }}
                                <span v-if="c.extra_field_separator" v-html="c.extra_field_separator"> </span>
                                <span v-if="c.extra_field">{{ slotProps.data[c.extra_field] }} </span>
                            </Button>
                            <span v-else-if="c.fieldtype == 'Date'">{{ moment(slotProps.data[c.fieldname]).format("DD-MM-YYYY") }}
                            </span>
                            <ComTimeago v-else-if="c.fieldtype == 'Timeago'" :date='slotProps.data[c.fieldname]' />
                            <div v-tippy="slotProps.data.room_numbers" class="overflow-hidden text-overflow-ellipsis" v-else-if="c.fieldtype == 'Room'" v-if="slotProps?.data && slotProps?.data?.room_numbers">
                             

                                <template v-for="(item, index) in slotProps.data.room_numbers.split(',')" :key="index">
                                    <span>{{ item }}</span>
                                    <span v-if="index != Object.keys(slotProps.data.room_numbers.split(',')).length - 1">,
                                    </span>
                                </template>
                            </div>
                            <div v-tippy="slotProps.data.room_type_alias" class="overflow-hidden text-overflow-ellipsis" v-else-if="c.fieldtype == 'room_type'" v-if="slotProps?.data && slotProps?.data?.room_type_alias">
                                <template v-for="(item, index) in slotProps.data.room_type_alias.split(',')" :key="index">
                                    <span>{{ item }}</span>
                                    <span v-if="index != Object.keys(slotProps.data.room_type_alias.split(',')).length - 1">, </span>
                                </template>
                            </div>
                            <template v-else-if="c.fieldname == 'owner' || c.fieldname == 'modified_by'">
                                <span>{{  slotProps.data[c.fieldname].split("@")[0] }}</span>
                            </template>
                            <CurrencyFormat v-else-if="c.fieldtype == 'Currency'" :value="slotProps.data[c.fieldname]" />
                            <span v-else-if="c.fieldtype == 'Status'" class="px-2 rounded-lg text-white p-1px border-round-3xl"
                                :style="{ backgroundColor: slotProps.data['status_color'] }">{{ slotProps.data[c.fieldname]
                                }}
                            </span>
                            <span v-else-if="c.fieldname == 'reservation_type'" v-tippy="slotProps.data[c.fieldname]=='FIT'?'Free Independent Traveler':'Group Inclusive Tour'">
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
            <Paginator class="p__paginator" v-model:first="pageState.activePage" :rows="pageState.rows" :totalRecords="pageState.totalRecords"
                :rowsPerPageOptions="[20, 30, 40, 50]" @page="pageChange">
                <template #start="slotProps">
                    <strong>Total Records: <span class="ttl-column_re">{{ pageState.totalRecords }}</span></strong>
                </template>
            </Paginator>
        </div>
    </div>
    <OverlayPanel ref="opShowColumn" id="res_list_hideshow">
        <ComOverlayPanelContent title="Show / Hide Columns" @onSave="OnSaveColumn" ttl_header="mb-2" titleButtonSave="Save"
            @onCancel="onCloseColumn">
            <template #top>
                <span class="p-input-icon-left w-full mb-3">
                    <i class="pi pi-search" />
                    <InputText v-model="filter.search_field" placeholder="Search" class="w-full" />
                </span>
            </template>
            <ul class="res__hideshow">
                <li class="mb-2" v-for="(c, index) in getColumns.filter(r => r.label)" :key="index">
                    <Checkbox v-model="c.selected" :binary="true" :inputId="c.fieldname" />
                    <label :for="c.fieldname">{{ c.label }}</label>
                </li>
            </ul>
            <template #footer-left>
                <Button class="border-none" icon="pi pi-replay" @click="onResetTable" label="Reset List" />
            </template>
        </ComOverlayPanelContent>
    </OverlayPanel>
    <OverlayPanel ref="showAdvanceSearch" style="max-width:70rem">
        <ComOverlayPanelContent title="Advance Filter" @onSave="onClearFilter" titleButtonSave="Clear Filter"
            icon="pi pi-filter-slash" :hideButtonClose="false" @onCancel="onCloseAdvanceSearch">
            <div class="grid">
                <ComAutoComplete class="col-3 input-wrp-search-autocomplete" width="100%" optionLabel="business_source_type" optionValue="name"
                    v-model="filter.selected_business_source_type" @onSelected="onSearch" placeholder="Business Source Type"
                    doctype="Business Source Type" />
                <ComAutoComplete class="col-3 input-wrp-search-autocomplete" width="100%" optionLabel="business_source" optionValue="name"
                    v-model="filter.selected_business_source" @onSelected="onSearch" placeholder="Business Source "
                    doctype="Business Source" />
                <ComSelect class="col-3" width="100%" v-model="filter.selected_reservation_type" @onSelected="onSearch"
                    placeholder="Reservation Type" :options="['GIT', 'FIT']" />

                <ComSelect class="col-3" width="100%" optionLabel="reservation_status" optionValue="name"
                    v-model="filter.selected_reservation_status" @onSelected="onSearch" placeholder="Reservation Status"
                    doctype="Reservation Status" />
                <ComSelect class="col-3" width="100%" isFilter optionLabel="room_type" optionValue="name"
                    v-model="filter.selected_room_type" @onSelected="onSearch" placeholder="Room Type" doctype="Room Type"
                    :filters="{ property: property.name }"></ComSelect>

                <ComSelect class="col-3" width="100%" isFilter groupFilterField="room_type_id"
                    :groupFilterValue="filter.selected_room_type" optionLabel="room_number" optionValue="name"
                    v-model="filter.selected_room_number" @onSelected="onSearch" placeholder="Room Name" doctype="Room"
                    :filters="{ property: property.name }"></ComSelect>

                <ComSelect class="col-3" width="100%" v-model="filter.search_date_type" :options="dataTypeOptions"
                    optionLabel="label" optionValue="value" placeholder="Search Date Type" :clear="false"
                    @onSelectedValue="onSelectFilterDate($event)"></ComSelect>
                <div class="col-6" v-if="filter.search_date_type">
                    <Calendar :selectOtherMonths="true" class="w-full" hideOnRangeSelection v-if="filter.search_date_type" dateFormat="dd-MM-yy"
                        v-model="filter.date_range" selectionMode="range" :manualInput="false" @date-select="onDateSelect"
                        placeholder="Select Date Range" showIcon />
                </div>
            </div>
        </ComOverlayPanelContent>
    </OverlayPanel>
</template>
<script setup>
import { inject, ref, reactive, useToast, getCount, getDocList, onMounted, getApi, computed,onUnmounted } from '@/plugin'

import { useDialog } from 'primevue/usedialog';
import NewFITReservationButton from '../reservation/components/NewFITReservationButton.vue';
import NewGITReservationButton from "@/views/reservation/components/NewGITReservationButton.vue"
import Paginator from 'primevue/paginator';
import ComOrderBy from '@/components/ComOrderBy.vue';
import { Timeago } from 'vue2-timeago'

const showAdvanceSearch = ref()
const moment = inject("$moment")
const gv = inject("$gv")
const toast = useToast()
const opShowColumn = ref();
const property = JSON.parse(localStorage.getItem("edoor_property"))

const columns = ref([
    { fieldname: 'name', label: 'Reservation #', fieldtype: "Link", post_message_action: "view_reservation_detail", default: true },
    { fieldname: 'reference_number', label: 'Ref. #' },
    { fieldname: 'reservation_type', label: 'Res. Type', header_class: "text-center", default: true },
    { fieldname: 'reservation_date', label: 'Res. Date', fieldtype: "Date", header_class: "text-center", frozen: true, default: true },
    { fieldname: 'arrival_date', label: 'Arrival', fieldtype: "Date", header_class: "text-center", default: true },
    { fieldname: 'departure_date', label: 'Departure', fieldtype: "Date", header_class: "text-center", default: true },
    { fieldname: 'room_nights', label: 'Room Nights', header_class: "text-center", default: true },
    { fieldname: 'room_type_alias', fieldtype: "room_type", label: 'Room Type', default: true },
    { fieldname: 'room_numbers', label: 'Rooms', fieldtype: "Room", header_class:"", default: true },
    { fieldname: 'adult', label: 'Pax(A/C)', extra_field: "child", extra_field_separator: "/", header_class: "text-center", default: true },
    { fieldname: 'guest', extra_field: "guest_name", extra_field_separator: "-", label: 'Guest', fieldtype: "Link", post_message_action: "view_guest_detail", default: true },
    { fieldname: 'guest_type', label: 'Guest Type ', default: true },
    { fieldname: 'group_code', label: 'Group Code', extra_field: "group_name", extra_field_separator: "<br/>", default: true },
    { fieldname: 'business_source', label: 'Business Source', default: true },
    { fieldname: 'total_reservation_stay', label: 'Total Stay #', header_class: "text-center", default: true },
    { fieldname: 'adr', label: 'ADR', fieldtype: "Currency", header_class: "text-right", default: true, can_view_rate:window.can_view_rate?'Yes':'No' },
    { fieldname: 'total_room_rate', label: 'Total Room Rate', fieldtype: "Currency", header_class: "text-right", default: true ,can_view_rate:window.can_view_rate?'Yes':'No' },
    { fieldname: 'total_debit', label: 'Debit', fieldtype: "Currency", header_class: "text-right", default: true,can_view_rate:window.can_view_rate?'Yes':'No'  },
    { fieldname: 'total_credit', label: 'Credit', fieldtype: "Currency", header_class: "text-right", default: true,can_view_rate:window.can_view_rate?'Yes':'No'  },
    { fieldname: 'balance', label: 'Balance', fieldtype: "Currency", header_class: "text-right", default: true,can_view_rate:window.can_view_rate?'Yes':'No'  },
    { fieldname: 'owner', label: 'Created By'},
    { fieldname: 'creation', fieldtype: "Timeago", label: 'Creation', header_class: "text-center", default: true },
    { fieldname: 'modified_by', label: 'Modified By' },
    { fieldname: 'modified', fieldtype: "Timeago", label: 'Last Modified', header_class: "text-center" },
    { fieldname: 'reservation_status', fieldtype: "Status", label: 'Status', header_class: "text-center", default: true },
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
    localStorage.setItem("page_state_reservation", JSON.stringify(pageState.value))
    opShowColumn.value.toggle(event);
    loadData()
}
const onCloseColumn = () => {
    opShowColumn.value.hide()
}

const dataTypeOptions = reactive([
    { label: 'Search Date', value: '' },
    { label: 'Arrival Date', value: 'arrival_date' },
    { label: 'Departure Date', value: 'departure_date' },
    { label: 'Reservation Date', value: 'reservation_date' }])
const data = ref([])

const filter = ref({})
let dateRange = reactive({
    start: '',
    end: ''
})

const pageState = ref({ order_by: "modified", order_type: "desc", page: 0, rows: 20, totalRecords: 0, activePage: 0 })
const working_date = ref('')
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
        ["Reservation", "property", '=', property.name]
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
        filters.push(["room_types", "like", "%" + filter.value.selected_room_type + "%"])
    }
    if (filter.value?.selected_room_number) {
        filters.push(["room_numbers", 'like', '%' + filter.value.selected_room_number + '%'])
    }

    if (filter.value?.search_date_type && filter.value.date_range != null) {
        filters.push([filter.value.search_date_type, '>=', dateRange.start])
        filters.push([filter.value.search_date_type, '<=', dateRange.end])
    }

    let fields = [...columns.value.map(r => r.fieldname), ...columns.value.map(r => r.extra_field)]
    fields = [...fields, ...selectedColumns.value]
    fields = [...new Set(fields.filter(x => x))]
    getDocList('Reservation', {
        fields: fields,
        orderBy: {
            field: '`tabReservation`.' + pageState.value.order_by,
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
    localStorage.setItem("page_state_reservation", JSON.stringify(pageState.value))
}
function getTotalRecord(filters) {
    getCount('Reservation', filters)
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
        if(e.data.action=="ReservationList"){
            setTimeout(()=>{
                loadData(false)
            },1000*10)
            
        }
    };
}

onMounted(() => { 
    window.addEventListener('message', actionRefreshData, false);

    let state = localStorage.getItem("page_state_reservation")
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
    getApi("frontdesk.get_meta", { doctype: "Reservation" }).then((result) => {
    
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

function onResetTable() {
    localStorage.removeItem("page_state_reservation")
    localStorage.removeItem("table_reservation_list_state")
    window.location.reload()
}

const advanceSearch = (event) => {
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

onUnmounted(() => {
    window.socket.off("ReservationList");
})

</script>