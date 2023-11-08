<template>
    <div class="flex-col flex" style="height: calc(100vh - 92px);">
        <div>
            <ComHeader isRefresh @onRefresh="Refresh()">
                <template #start>
                    <div class="text-2xl">City Ledger</div>
                </template>
                <template #end>
                    <SplitButton class="spl__btn_cs sp" @click="onPrint" label="Print" icon="pi pi-print" />
                </template>
            </ComHeader>
            <div class="flex justify-between">
                <div>
                    <div class="flex gap-2">
                        <div class="p-0">
                            <div class="p-input-icon-left w-full">
                                <i class="pi pi-search" />
                                <InputText v-model="filter.keyword" placeholder="Search" @input="onSearch" />
                            </div>
                        </div>
                        <div>
                            <div class="flex gap-2">
                                <Button icon="pi pi-sliders-h" class="content_btn_b" @click="advanceFilter" />

                                <div v-if="isFilter">
                                    <Button class="content_btn_b whitespace-nowrap" label="Clear Filter"
                                        icon="pi pi-filter-slash" @click="onClearFilter" />
                                </div>
                            </div>
                        </div>
                        

                    </div>
                </div>
                <div class="flex gap-2">
                    <div>
                        <Dropdown v-model="order.order_by" :options="sortOptions" optionValue="fieldname"
                            optionLabel="label" placeholder="Sort By" @change="onSelectOrderBy" />
                    </div>
                    <div>
                        <!-- <Button class="content_btn_b h-full px-3" @click="onOrderTypeClick">{{order.order_type}}</Button> -->
                        <Button class="content_btn_b h-full px-3" @click="onOrderTypeClick">
                            <i v-if="order.order_type == 'desc'" class="pi pi-sort-alpha-down" />
                            <i v-if="order.order_type == 'asc'" class="pi pi-sort-alpha-up" />
                        </Button>
                    </div>
                    <Button class="content_btn_b h-full px-3" @click="toggleShowColumn">
                        <ComIcon icon="iconEditGrid" height="16px"></ComIcon>
                    </Button>
                </div>
            </div>
            <div>
                <div class="flex w-full gap-3 mb-3 mt-3">
                    <div :class="(index === summary.length - 1) ? 'bg-green-50 border-green-edoor' : 'bg-white'"
                        class="flex flex-column rounded-lg  grow p-2 shadow-charge-total border"
                        v-for="(s, index) in summary" :key="index">
                        <span class="text-500 uppercase text-sm text-end">{{ s.label }}</span>
                        <span class="text-xl line-height-2 font-semibold text-end">
                            <span>{{ s.value }}</span>
                        </span>
                    </div>
                </div>
            </div>
        </div>
        <div class="overflow-auto h-full">
            <ComPlaceholder text="No Data" :loading="gv.loading" :is-not-empty="data && data.length > 0">
                <DataTable 
                class="tb-cs-datatable"
                :resizableColumns="true"
                columnResizeMode="fit" 
                showGridlines 
                stateStorage="local"
                stateKey="table_guest_ledger_state" 
                :reorderableColumns="true" :value="data"
                tableStyle="min-width: 50rem" 
                paginator 
                :rows="20" 
                :rowsPerPageOptions="[20, 30, 40, 50]">
                <div class="absolute bottom-6 left-4">
                    <strong>Total Records: <span class="ttl-column_re">{{ pageState.totalRecords }}</span></strong>
                </div>
                    <Column v-for="c of columns?.filter(r => r.label && selectedColumns?.includes(r.fieldname))"
                        :key="c.fieldname" :field="c.fieldname" :header="c.label" :headerClass="c.header_class || ''"
                        :bodyClass="c.header_class || ''">
                        <template #body="slotProps">
                          
                            <Button v-if="c.fieldtype == 'Link'" class="p-0 link_line_action1"
                                @click="onOpenLink(c, slotProps.data)" link>
                                {{ slotProps.data[c.fieldname] }}
                                <span v-if="c.extra_field_separator" v-html="c.extra_field_separator"> </span>
                                <span v-if="c.extra_field">{{ slotProps.data[c.extra_field] }} </span>
                            </Button>
                            <span v-else-if="c.fieldtype == 'Date' && slotProps.data[c.fieldname]">{{
                                moment(slotProps.data[c.fieldname]).format("DD-MM-YYYY") }} </span>
                            <span v-else-if="c.fieldtype == 'Datetime'">{{
                                moment(slotProps.data[c.fieldname]).format("DD-MM-YYYY h:mm a")
                            }} </span>
                         
                            <ComTimeago v-else-if="c.fieldtype == 'Timeago'" :date="slotProps.data[c.fieldname]"  />
                            <div v-else-if="c.fieldtype == 'Room'"
                                class="rounded-xl px-2 me-1 bg-gray-edoor inline room-num"
                                v-if="slotProps?.data && slotProps?.data?.rooms">
                                <template v-for="(item, index) in slotProps.data.rooms.split(',')" :key="index">
                                    <span>{{ item }}</span>
                                    <span v-if="index != Object.keys(slotProps.data.rooms.split(',')).length - 1">, </span>
                                </template>
                            </div>
                            <CurrencyFormat v-else-if="c.fieldtype == 'Currency'" :value="slotProps.data[c.fieldname]" />
                            <span v-else-if="c.fieldtype == 'ReservationStatus'"
                                class="px-2 rounded-lg me-2 text-white p-1px border-round-3xl"
                                :style="{ backgroundColor: slotProps.data['reservation_status_color'] }">{{
                                    slotProps.data[c.fieldname]
                                }}</span>
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
    </div>

    <OverlayPanel ref="opShowColumn" style="width:30rem;">
        <ComOverlayPanelContent title="Show / Hide Columns" @onSave="OnSaveColumn" ttl_header="mb-2" titleButtonSave="Save"
            @onCancel="onCloseColumn">
            <template #top>
                <div class="p-input-icon-left mb-3 w-full">
                    <i class="pi pi-search" />
                    <InputText v-model="filter.search_field" placeholder="Search" class="w-full" />
                </div>
            </template>
            <div class="grid">
                <div class="col-6 py-1" v-for="(c, index) in getColumns.filter(r => r.label)" :key="index">
                    <Checkbox v-model="c.selected" :binary="true" :inputId="c.fieldname" />
                    <label :for="c.fieldname">{{ c.label }}</label>
                </div>
            </div>
            <template #footer-left>
                <Button class="border-none" icon="pi pi-replay" label="Reset List" @click="onResetTable" />
            </template>
        </ComOverlayPanelContent>
    </OverlayPanel>

    <OverlayPanel ref="showAdvanceSearch" style="width:70rem">
        <ComOverlayPanelContent title="Advance Filter" @onSave="onClearFilter" titleButtonSave="Clear Filter"
            icon="pi pi-filter-slash" :hideButtonClose="false" @onCancel="onCloseAdvanceSearch">
            <div class="grid">
                <div class="col-4">
                    <Calendar class="w-full" :selectOtherMonths="true" v-model="filter.start_date" placeholder="Start Date"
                        dateFormat="dd-mm-yy" @date-select="onDateSelect" showIcon />
                </div>
                <div class="col-4">
                    <Calendar class="w-full" :selectOtherMonths="true" v-model="filter.end_date" placeholder="End Date"
                        dateFormat="dd-mm-yy" showIcon @date-select="onDateSelect" />
                </div>
                <div class="col-4">
                    <ComAutoComplete v-model="filter.business_source" class="pb-2 w-full" placeholder="Business Source"
                        doctype="Business Source" @onSelected="onSearch" />
                </div>
                <div class="col-4">
                    <ComAutoComplete v-model="filter.city_ledger_type" class="pb-2 w-full" placeholder="City Ledger Type"
                        doctype="City Ledger Type" @onSelected="onSearch" :filters="['property', '=', property.name]" />
                </div>
                <!-- <Button @click="onSearch">Refresh</Button> -->
            </div>
        </ComOverlayPanelContent>
    </OverlayPanel>
</template>

<script setup>
import { ref, onMounted, onUnmounted, inject, computed, useDialog } from '@/plugin'
import { Timeago } from 'vue2-timeago'
import ComIFrameModal from '@/components/ComIFrameModal.vue';
const dialog = useDialog();
const edoor_setting = JSON.parse(localStorage.getItem("edoor_setting"))
const property = JSON.parse(localStorage.getItem("edoor_property"))
const working_day = JSON.parse(localStorage.getItem("edoor_working_day"))
const data = ref()
const frappe = inject('$frappe');
const gv = inject('$gv');
const call = frappe.call();
const columns = ref()
const summary = ref()
const showAdvanceSearch = ref()
const moment = inject("$moment")
const filter = ref({ start_date: moment(working_day.date_working_day).startOf('month').toDate(), end_date: moment(working_day.date_working_day).toDate(), guest: "",keyword:"" })
const pageState = ref({ order_by: "modified", order_type: "desc", page: 0, rows: 20, totalRecords: 0 })
const order = ref({ order_by: "modified", order_type: "desc" })
const defaultFilter = JSON.parse(JSON.stringify(filter.value))
// const loading = ref(false)
const selectedColumns = ref([])

const sortOptions = ref([
    { "fieldname": "modified", label: "Last Update On" },
    { "fieldname": "creation", label: "Created On" },
    { "fieldname": "name", label: "ID" }
])

// const pageState = ref({})
const opShowColumn = ref();

const getColumns = computed(() => {
    if (filter.value.search_field) {
        return columns.value.filter(r => (r.label || "").toLowerCase().includes(filter.value.search_field.toLowerCase())).sort((a, b) => a.label.localeCompare(b.label));
    } else {
        return columns.value.filter(r => r.label).sort((a, b) => a.label.localeCompare(b.label));
    }
})

function onOpenLink(column, data) {
    window.postMessage(column.post_message_action + "|" + data[column.fieldname], '*')
}



const toggleShowColumn = (event) => {
    opShowColumn.value.toggle(event);
}

function OnSaveColumn(event) {
    selectedColumns.value = columns.value.filter(r => r.selected).map(x => x.fieldname)
    pageState.value.selectedColumns = selectedColumns.value
    localStorage.setItem("page_state_guest_ledger", JSON.stringify(pageState.value))
    opShowColumn.value.toggle(event);
}

function onResetTable() {
    localStorage.removeItem("page_state_guest_ledger")
    localStorage.removeItem("table_guest_ledger_state")
    window.location.reload()
}

function onPrint() {
    const dialogRef = dialog.open(ComIFrameModal, {

        data: {
            "doctype": "Customer",
            name: property.name,
            report_name: "xx",
            fullheight: true
        },
        props: {
            header: "U print me",
            style: {
                width: '90vw',
            },
            position: "top",
            modal: true,
            maximizable: true,
            closeOnEscape: false
        }

    });
}

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

function onOrderTypeClick() {
    order.value.order_type = order.value.order_type == "desc" ? "asc" : "desc"
    loadData()
}

function onSelectOrderBy() {
    loadData()
}

function onDateSelect(d) {
    onSearch()
}

const onSearch = debouncer(() => {
    loadData();
}, 500);

const Refresh = debouncer(() => {
    loadData();
}, 500);
function loadData() {
    gv.loading = true
    const filters = JSON.parse(JSON.stringify(filter.value))
    filters.start_date = moment(filter.value.start_date).format("YYYY-MM-DD")
    filters.end_date = moment(filter.value.end_date).format("YYYY-MM-DD")
    filters.property = property.name
    filters.order_by = order.value.order_by
    filters.order_type = order.value.order_type
    call.get("frappe.desk.query_report.run", {
        report_name: edoor_setting.city_ledger_report_name,
        filters: filters
    }).then((result) => {
        columns.value = result.message.columns
        if (selectedColumns.value && selectedColumns.value.length == 0) {
            selectedColumns.value = columns.value.filter(r => r.default).map(r => r.fieldname)
        }
        columns.value.forEach(r => {
            r.selected = selectedColumns.value.includes(r.fieldname)
        });

        data.value = result.message.result.slice(0, -1)
        pageState.value.totalRecords = data.value.length
        summary.value = result.message.report_summary
        sortOptions.value = [...sortOptions.value, ...columns.value]
        gv.loading = false

    }).catch((err) => {
        gv.loading = false

        if (err._server_messages) {

            const _server_messages = JSON.parse(err._server_messages)

            _server_messages.forEach(r => {
                window.postMessage('show_alert|' + JSON.parse(r).message.replace("Error: ", ""), '*')
            });
        } else {
            window.postMessage('show_alert|' + err.exception, '*')
        }
    })
}

onMounted(() => {

    window.socket.on("CityLedger", (arg) => {
        if (arg == property.name) {
            setTimeout(function () {
                loadData()
            }, 3000)
        }
    })

    let state = JSON.parse(localStorage.getItem("page_state_guest_ledger"))

    if (state) {
        if (state.selectedColumns) {
            selectedColumns.value = state.selectedColumns
        }
    }
    loadData()
})

onUnmounted(() => {
    window.socket.off("CityLedger");
})

const advanceFilter = (event) => {
    showAdvanceSearch.value.toggle(event);
}

const onCloseColumn = () => {
    opShowColumn.value.hide()
}
const onCloseAdvanceSearch = () => {
    showAdvanceSearch.value.hide()
}

const onClearFilter = () => {
    filter.value = JSON.parse(JSON.stringify(defaultFilter))
    filter.value.start_date = moment(filter.value.start_date).toDate()
    filter.value.end_date = moment(filter.value.end_date).toDate()
    loadData()
    showAdvanceSearch.value.hide()
}

const isFilter = computed(() => {
    if (moment(working_day.date_working_day).startOf('month').format('yyyy-MM-DD') != moment(filter.value.start_date).format('yyyy-MM-DD') || moment(working_day.date_working_day).format('yyyy-MM-DD') != moment(filter.value.end_date).format('yyyy-MM-DD')) {
        return true
    }
    else {
        return gv.isNotEmpty(filter.value, 'start_date,end_date')
    }
})
</script>