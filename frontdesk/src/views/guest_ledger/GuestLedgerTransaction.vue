<template>
    <div class="flex-col flex" style="height: calc(100vh - 92px);">
        <div>
            <ComHeader isRefresh @onRefresh="Refresh()">
                <template #start>
                    <div class="flex">
                        <div class="flex align-items-center">
                            <div @click="loadData()" class="text-2xl">Guest ledger Transaction</div>
                        </div>
                    </div>
                </template>
                <template #end>
                    <Button class="conten-btn" @click="onPrint"><i class="pi pi-print mr-2"></i> Print</Button>
                </template>
            </ComHeader>
            <div class="flex justify-between">
                <div>
                    <div class="flex gap-2">
                        <div class="col-3 p-0">
                            <div class="p-input-icon-left w-full">
                                <i class="pi pi-search" />
                                <InputText class="w-full" v-model="filter.keyword" placeholder="Search" @input="onSearch" />
                            </div>
                            <!-- <InputText class="w-full" v-model="filter.keyword" placeholder="Search" @input="onSearch" /> -->
                        </div>
                        <div>
                            <ComAutoComplete v-model="filter.room_id" class="w-full" placeholder="Room" doctype="Room"
                                @onSelected="onSearch" />
                        </div>
                        <div class="w-20rem">
                            <ComAutoComplete v-model="filter.account_code" class="w-full" placeholder="Account Code" doctype="Account Code"
                                @onSelected="onSearch" />
                        </div>
                        
                        <div>
                            <div class="flex gap-2">
                                <Button icon="pi pi-sliders-h" class="content_btn_b" @click="advanceFilter" />
                                <div v-if="isFilter" >
                                    <Button class="content_btn_b whitespace-nowrap" label="Clear Filter" icon="pi pi-filter-slash"
                                        @click="onClearFilter" />
                                </div>
                            </div>
                        </div>
                        
                    </div>
                </div> 
                <div class="flex">
                    <div class="px-2">
                        <ComOrderBy doctype="Folio Transaction" @onOrderBy="onOrderBy" />
                    </div>
                    <Button class="content_btn_b h-full px-3" @click="toggleShowColumn">
                        <ComIcon icon="iconEditGrid" height="16px"></ComIcon>
                    </Button>
                </div>
            </div>
            <div>
                <div class="flex w-full gap-3 mb-3 mt-3">
                    <div :class="(index === summary.length - 1) ? 'bg-green-50 border-green-edoor' : 'bg-white'"
                        class="flex flex-column rounded-lg  grow p-2 shadow-charge-total border" v-for="(s, index) in summary"
                        :key="index">
                        <span class="text-500 uppercase text-sm text-end">{{ s.label }}</span><span
                            class="text-xl line-height-2 font-semibold text-end">
                            <span>{{ s.value }}</span></span>
                    </div>
                </div>
            </div>
        </div>
        <div class="overflow-auto h-full">
            <ComPlaceholder text="No Data"  :loading="gv.loading"  :is-not-empty="data?.length > 0">
                <DataTable 
                class="tb-cs-datatable"
                resizableColumns 
                columnResizeMode="fit" 
                showGridlines 
                stateStorage="local"
                stateKey="table_guest_ledger_state" 
                :reorderableColumns="true" 
                :value="data" 
                tableStyle="min-width: 50rem" 
                paginator
                :rows="20" 
                :rowsPerPageOptions="[20, 30, 40, 50]">
                <div class="absolute bottom-6 left-4">
                    <strong>Total Records: <span class="ttl-column_re">{{pageState.totalRecords}}</span></strong>
                </div>
                    <Column v-for="c of columns?.filter(r => r.label && selectedColumns?.includes(r.fieldname))" :key="c.fieldname" :field="c.fieldname" :header="c.label"
                        :headerClass="c.header_class || ''" :bodyClass="c.header_class || ''">
                        <template #body="slotProps">
                            <Button v-if="c.fieldtype == 'Link'" :class="'p-0 ' + (slotProps.data[c.fieldname] != '' ? 'link_line_action1' : '')" @click="onOpenLink(c, slotProps.data)"
                                link>
                                {{ slotProps.data[c.fieldname] }}
                                <span v-if="c.extra_field_separator" v-html="c.extra_field_separator"> </span>
                                <span v-if="c.extra_field">{{ slotProps.data[c.extra_field] }} </span>
                            </Button>
                            <span v-else-if="c.fieldtype == 'Date' && slotProps.data[c.fieldname]">{{
                                moment(slotProps.data[c.fieldname]).format("DD-MM-YYYY") }} </span>
                            <span v-else-if="c.fieldtype == 'Datetime'">{{ moment(slotProps.data[c.fieldname]).format("DD-MM-YYYY h:mm a")
                            }} </span>
                            <ComTimeago v-else-if="c.fieldtype == 'Timeago'" :date="slotProps.data[c.fieldname]" />
                            <div v-else-if="c.fieldtype == 'Room'" class="rounded-xl px-2 me-1 bg-gray-edoor inline room-num"
                                v-if="slotProps?.data && slotProps?.data?.room_number">
                                <template v-for="(item, index) in slotProps.data.room_number.split(',')" :key="index">
                                    <span>{{ item }}</span>
                                    <span v-if="index != Object.keys(slotProps.data.room_number.split(',')).length - 1">, </span>
                                </template>
                            </div>
                            <CurrencyFormat v-else-if="c.fieldtype == 'Currency'" :value="slotProps.data[c.fieldname]" />
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
            
        </div>
    </div>
    <OverlayPanel ref="opShowColumn" style="width:30rem;">
        <ComOverlayPanelContent title="Show / Hide Columns" @onSave="OnSaveColumn" ttl_header="mb-2" titleButtonSave="Save"
            @onCancel="onCloseColumn">
            <template #top>
                <div class="p-input-icon-left mb-3 w-full">
                    <i class="pi pi-search" />
                    <InputText class="w-full" v-model="filter.search_field" placeholder="Search" />
                </div>
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
    <OverlayPanel ref="showAdvanceSearch" style="width:70rem">
        <ComOverlayPanelContent title="Advance Filter" @onSave="onClearFilter" titleButtonSave="Clear Filter"
            icon="pi pi-filter-slash" :hideButtonClose="false" @onCancel="onCloseAdvanceSearch">
            <div class="grid">
                <div class="col-4">
                    <Calendar panelClass="no-btn-clear" class="w-full"  showButtonBar :selectOtherMonths="true" v-model="filter.start_date" placeholder="Start Date"
                        dateFormat="dd-mm-yy" @date-select="onDateSelect" showIcon />
                </div>
                <div class="col-4">
                    <Calendar panelClass="no-btn-clear" showButtonBar class="w-full" :selectOtherMonths="true" v-model="filter.end_date" placeholder="End Date"
                        dateFormat="dd-mm-yy" showIcon @date-select="onDateSelect" />
                </div>
                <div class="col-4">
                    <ComAutoComplete v-model="filter.business_source" class="w-full" placeholder="Business Source"
                        doctype="Business Source" @onSelected="onSearch" />
                </div>
                <div class="col-4">
                    <ComAutoComplete v-model="filter.reservation" class="w-full" placeholder="Reservation #"
                        doctype="Reservation" @onSelected="onSearch" :filters="{ property: property.name }" />
                </div>
                <div class="col-4">
                    <ComAutoComplete v-model="filter.reservation_stay" class="w-full" placeholder="Reservation Stay #"
                        doctype="Reservation Stay" @onSelected="onSearch" :filters="{ property: property.name }" />
                </div>
                <div class="col-4">

                    <div class="py-2 flex items-center w-full p-dropdown-label p-inputtext p-placeholder">

                        <Checkbox class="me-2" inputId="show-ms" @change="onSearch" v-model="filter.is_master_folio"
                            :binary="true" :trueValue="1" :falseValue="0" />
                        <label ref="show-ms">
                            <span>Show Master Folio Only</span>
                        </label>
                    </div>
                </div>
            </div>
        </ComOverlayPanelContent>
    </OverlayPanel>
</template>
<script setup>
import { ref, onMounted, onUnmounted, inject, computed, useDialog, watch } from '@/plugin'
import { Timeago } from 'vue2-timeago'
import ComIFrameModal from '@/components/ComIFrameModal.vue';
import ComOrderBy from '@/components/ComOrderBy.vue';

const dialog = useDialog();
const edoor_setting = JSON.parse(localStorage.getItem("edoor_setting"))
const property = JSON.parse(localStorage.getItem("edoor_property"))
const data = ref()
const gv = inject("$gv")
const frappe = inject('$frappe');
const call = frappe.call();
const columns = ref()
const summary = ref()
const moment = inject("$moment")
const filter = ref({ status: 'All Status', start_date: moment().startOf('month').toDate(), end_date: moment().toDate(), guest: "",keyword: "" })
const defaultFilter = JSON.parse(JSON.stringify(filter.value))
const order = ref({order_by: "modified", order_type: "desc"})
const selectedColumns = ref([])
const sortOptions = ref([
    { "fieldname": "modified", label: "Last Update On" },
    { "fieldname": "creation", label: "Created On" },
    { "fieldname": "name", label: "ID" }
])
const pageState = ref({ order_by: "modified", order_type: "desc", page: 0, rows: 20, totalRecords: 0 })
const opShowColumn = ref();

const getColumns = computed(() => {
    if (filter.value.search_field) {
        return columns.value.filter(r => (r.label || "").toLowerCase().includes(filter.value.search_field.toLowerCase())).sort((a, b) => a.label.localeCompare(b.label));
    } else {
        return columns.value.filter(r => r.label).sort((a, b) => a.label.localeCompare(b.label));
    }
})

const isFilter = computed(()=>{
    if(moment().startOf('month').format('yyyy-MM-DD') != moment(filter.value.start_date).format('yyyy-MM-DD') || moment().format('yyyy-MM-DD') != moment(filter.value.end_date).format('yyyy-MM-DD')){
        return true
    }
    else{
        return gv.isNotEmpty(filter.value,'start_date,end_date',{ status: 'All Status'})
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
            "doctype": "Business Branch",
            name: window.property_name,
            report_name: "Guest Ledger Transaction Report",
            fullheight: true,
            filter_options:["start_date","end_date","reservation","reservation_stay","business_source","guest","is_master"]
        },
        props: {
            header: "Guest Ledger Transaction",
            style: {
                width: '80vw',
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
    pageState.value.page=0
    loadData();
}, 500);

function loadData(show_loading=true) {
    data.value = []
    summary.value = []
    gv.loading = show_loading
    const filters = JSON.parse(JSON.stringify(filter.value))
    filters.start_date = moment(filter.value.start_date).format('yyyy-MM-DD')
    filters.end_date = moment(filter.value.end_date).format('yyyy-MM-DD')
    filters.property = property.name
    filters.order_by = order.value.order_by
    filters.order_type = order.value.order_type
    call.get("frappe.desk.query_report.run", {
        report_name: edoor_setting.guest_ledger_transaction_report,
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

    window.socket.on("GuestLedgerTransaction", (arg) => {
        if (arg.property == window.property_name) { 
        setTimeout(function () {
            loadData(false)
        }, 3000)
    }
    })

    let state = JSON.parse(localStorage.getItem("page_state_guest_ledger"))
    if (state) {
        if (state.selectedColumns) {
            selectedColumns.value = state.selectedColumns
        }
    }
    const pagerState = JSON.parse(localStorage.getItem("table_guest_ledger_state"))
    if(pagerState){
        pagerState.first = 0
        localStorage.setItem("table_guest_ledger_state",JSON.stringify(pagerState))
    } 
    
    loadData()
})

onUnmounted(() => {
    window.socket.off("GuestLedgerTransaction");
})

const showAdvanceSearch = ref()

const advanceFilter = (event) => {
    showAdvanceSearch.value.toggle(event);
}

const onClearFilter = () => {
    filter.value = JSON.parse(JSON.stringify(defaultFilter))
    filter.value.start_date = gv.dateApiFormat(filter.value.start_date)
    filter.value.end_date = gv.dateApiFormat(filter.value.end_date)
    loadData()
    showAdvanceSearch.value.hide()
}

const onCloseAdvanceSearch = () => {
    showAdvanceSearch.value.hide()
}

function onOrderBy(data) {
    order.value.order_by = data.order_by
    pageState.value.order_type = data.order_type
    const pagerState = JSON.parse(localStorage.getItem("table_guest_ledger_state")) 
    pagerState.first = 0
    localStorage.setItem("table_guest_ledger_state",JSON.stringify(pagerState))
    loadData()
}

const onCloseColumn = () => {
    opShowColumn.value.hide()
}
</script>