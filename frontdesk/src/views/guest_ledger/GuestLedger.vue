<template>
    
    <div class="flex-col flex view_sroll_mobile_table" style="height: calc(100vh - 92px);">
        <div>
            <ComHeader isRefresh @onRefresh="Refresh()">
                <template #start>
                    <div class="flex">
                        <div class="flex align-items-center">
                            <div class="text-2xl">{{ $t('Guest Ledger') }} </div>
                        </div>
                    </div>
                </template>
            </ComHeader>
            <div class="flex justify-between">
                <div>
                    <div class="flex gap-2">
                        <template v-if="!isMobile">
                        <div class="p-0">
                            <div class="p-input-icon-left w-full">
                                <i class="pi pi-search" />
                                <InputText class="w-full" v-model="filter.keyword" :placeholder=" $t('Search') " @input="onSearch" />
                            </div>
                         </div>
                       
                    </template>
                        <div>
                            <div class="flex gap-2">
                                <Button icon="pi pi-sliders-h" class="content_btn_b" @click="advanceFilter" />
                                <div v-if="isFilter">
                                    <Button class="content_btn_b whitespace-nowrap" :label="isMobile ? $t('Clear') : $t('Clear Filter') "
                                        icon="pi pi-filter-slash" @click="onClearFilter" />
                                </div>
                            </div>
                        </div>

                    </div>
                </div>
                <div class="flex">
                    <div class="px-2">
                        <ComOrderBy doctype="Customer" @onOrderBy="onOrderBy" />
                                 </div>
                    <Button class="content_btn_b h-full px-3" @click="toggleShowColumn">
                        <ComIcon icon="iconEditGrid" height="16px"></ComIcon>
                    </Button>
                </div>
            </div>
            <div>
                <ComSummaryofBalence :summary="summary" :start_date="working_day.date_working_day" :end_date="working_day.date_working_day" />
            </div>
        </div>
        <div class="overflow-auto h-full">
            <ComPlaceholder text="No Data" :loading="gv.loading" :is-not-empty="data?.length > 0">

                <DataTable class="tb-cs-datatable" @page="onPage" :resizableColumns="true" columnResizeMode="fit"
                    showGridlines stateStorage="local" stateKey="table_guest_ledger_state" :reorderableColumns="true"
                    scrollable :value="data" paginator :rows="20" :rowsPerPageOptions="[20, 30, 40, 50]"
                    tableStyle="min-width: 50rem">
                    <div class="absolute bottom-6 left-4">
                        <strong>{{ $t('Total Records') }} : <span class="ttl-column_re">{{ pageState.totalRecords }}</span></strong>
                    </div>
                    <Column v-for="c of columns?.filter(r => r.label && selectedColumns?.includes(r.fieldname))"
                        :key="c.fieldname" :field="c.fieldname" :header="$t(c.label) " :headerClass="c.header_class || ''"
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
                            <ComTimeago v-else-if="c.fieldtype == 'Timeago'" :date="slotProps.data[c.fieldname]" />
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
                                :style="{ backgroundColor: slotProps.data['reservation_status_color'] }">
                                {{ $t(slotProps.data[c.fieldname]) }}</span>
                            <span v-else-if="c.fieldtype == 'Check'">
                                <span v-if="slotProps.data[c.fieldname]">
                                    <ComIcon v-if="c.label == 'Master Folio'" v-tippy="'Is Master Folio'"
                                        style="height: 14px;margin: auto;" icon="iconCrown" />
                                    <span v-else>YES</span>
                                </span>
                                <span v-else>
                                </span>
                            </span>
                            <template v-else-if="c.fieldtype == 'status'">
                            
                                <ComOpenStatus :status="slotProps.data[c.fieldname]" />
                            </template>
                            <span v-else>
                                <span>{{ slotProps.data[c.fieldname] }} </span>
                                <span v-if="c.extra_field_separator" v-html="c.extra_field_separator"> </span>
                                <span v-if="c.extra_field">{{ slotProps.data[c.extra_field] }} </span>
                            </span>

                        </template>
                    </Column>
                </DataTable>
            </ComPlaceholder>
        </div>
        <div>
            <Paginator class="p__paginator" v-model:first="pageState.activePage" :rows="pageState.rows"
                :totalRecords="pageState.totalRecords" :rowsPerPageOptions="[20, 30, 40, 50]" @page="pageChange">
                <template #start="slotProps">
                    <strong> {{ $t('Total Records') }} : <span class="ttl-column_re">{{ pageState.totalRecords }}</span></strong>
                </template>
            </Paginator>
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
                <Button class="border-none" icon="pi pi-replay" @click="onResetTable" :label=" $t('Reset List') " />
            </template>
        </ComOverlayPanelContent>
    </OverlayPanel>
    <OverlayPanel ref="showAdvanceSearch" >
        <ComOverlayPanelContent title="Advance Filter" @onSave="onClearFilter" titleButtonSave="Clear Filter"
            icon="pi pi-filter-slash" :hideButtonClose="false" @onCancel="onCloseAdvanceSearch">
            <div class="grid">
                <template v-if="isMobile">

                        
<div class="col-12">
    <div class="p-input-icon-left w-full">
        <i class="pi pi-search" />
        <InputText class="w-full" v-model="filter.keyword" :placeholder=" $t('Search') " @input="onSearch" />
    </div>
    <!-- <InputText class="w-full" v-model="filter.keyword" placeholder="Search" @input="onSearch" /> -->
</div>
<div class="col-6">
    <ComSelect :options="['All Status','Open', 'Closed']" placeholder="All Status" v-model="filter.status"
        :clear="false" @onSelected="onSearch" />
</div>
<div class="col-6">
    <ComSelect v-model="filter.reservation_status" placeholder="Reservation Status"
        doctype="Reservation Status" @onSelected="onSearch" />
</div>
</template>
               
                <div class="col-6 md:col-4">
                    <ComAutoComplete v-model="filter.business_source" class="w-full" placeholder="Business Source"
                        doctype="Business Source" @onSelected="onSearch" />
                </div>
                <div class="col-6 md:col-4">
                    <ComAutoComplete v-model="filter.guest" class="w-full" placeholder="Guest" doctype="Customer"
                        @onSelected="onSearch" />
                </div>
                <div class="col-6 md:col-4">
                    <ComAutoComplete v-model="filter.reservation" class="w-full" placeholder="Reservation #"
                        doctype="Reservation" @onSelected="onSearch" :filters="{ property: property.name }" />
                </div>
                <div class="col-6 md:col-4">
                    <ComAutoComplete v-model="filter.reservation_stay" class="w-full" placeholder="Reservation Stay #"
                        doctype="Reservation Stay" @onSelected="onSearch" :filters="{ property: property.name }" />
                </div>
            </div>
        </ComOverlayPanelContent>
    </OverlayPanel>
</template>
<script setup>
import { ref, onMounted, onUnmounted, inject, computed, useDialog } from '@/plugin'
import { Timeago } from 'vue2-timeago'
import ComIFrameModal from '@/components/ComIFrameModal.vue';
import ComOrderBy from '@/components/ComOrderBy.vue';
import ComSummaryofBalence from '@/views/city_ledger/components/ComSummaryofBalence.vue' 
import {i18n} from '@/i18n';
const { t: $t } = i18n.global;
const dialog = useDialog();
const edoor_setting = JSON.parse(localStorage.getItem("edoor_setting"))
const property = JSON.parse(localStorage.getItem("edoor_property"))
const working_day = JSON.parse(localStorage.getItem("edoor_working_day"))
const data = ref()
const gv = inject("$gv")
const frappe = inject('$frappe');
const call = frappe.call();
const columns = ref()
const summary = ref()
const moment = inject("$moment")
const filter = ref({ guest: "", keyword: "" })
const defaultFilter = JSON.parse(JSON.stringify(filter.value))
const order = ref({ order_by: "modified", order_type: "desc" })

const isMobile = ref(window.isMobile) 
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

const isFilter = computed(() => {
     
        return gv.isNotEmpty(filter.value, 'start_date,end_date,order_by,order_type', { status: 'All Status' })

  
})

function onOpenLink(column, data) {
    window.postMessage(column.post_message_action + "|" + data[column.fieldname], '*')
}
function pageChange(page) {
    pageState.value.page = page.page
    pageState.value.rows = page.rows
    loadData()
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
            name: property.name,
            report_name: gv.getCustomPrintFormat("Guest Ledger Report"),
            fullheight: true,
            filter_options:["start_date","end_date","reservation","reservation_stay","business_source","guest","reservation_status","is_master"]
        },
        props: {
            header: "Guest Ledger",
            style: {
                width: '90vw',
            },
            position: "top",
            modal: true,
            maximizable: true,
            closeOnEscape: false,
            breakpoints:{
                '960px': '90vw',
                '640px': '100vw'
            },
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

 


function onDateSelect(d) {
    onSearch()
}

const onSearch = debouncer(() => {
    loadData();
}, 500);
const Refresh = debouncer(() => {
    pageState.value.page = 0
    loadData();
}, 500);


function loadData(show_loading = true) {
    gv.loading = show_loading
    const filters = JSON.parse(JSON.stringify(filter.value))
    filters.start_date = moment(filter.value.start_date).format("YYYY-MM-DD")
    filters.end_date = moment(filter.value.end_date).format("YYYY-MM-DD")
    filters.property = property.name
    filters.order_by = order.value.order_by
    filters.order_type = order.value.order_type
    filters.keyword = gv.keyword(filter.value.keyword)
    call.get("frappe.desk.query_report.run", {
        report_name: edoor_setting.guest_ledger_report_name,
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

const actionRefreshData = async function (e) {
    if (e.isTrusted && typeof (e.data) != 'string') {
        if(e.data.action=="GuestLedger"){
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
    window.addEventListener('message', actionRefreshData, false); 
    let state = JSON.parse(localStorage.getItem("page_state_guest_ledger"))
    if (state) {
        if (state.selectedColumns) {
            selectedColumns.value = state.selectedColumns
        }
    }
    loadData()
})

const showAdvanceSearch = ref()
const advanceFilter = (event) => {
    showAdvanceSearch.value.toggle(event);
}

const onClearFilter = () => {
    filter.value = JSON.parse(JSON.stringify(defaultFilter))
    filter.value.start_date = moment(filter.value.start_date).toDate();
    filter.value.end_date = moment(filter.value.end_date).toDate();
    loadData()
    showAdvanceSearch.value.hide()
}

const onCloseAdvanceSearch = () => {
    showAdvanceSearch.value.hide()
}

function onOrderBy(data) {
    order.value.order_type = order.value.order_type == "desc" ? "asc" : "desc"
    pageState.value.order_type = data.order_type
    pageState.value.page = 0
    loadData()
}


const onCloseColumn = () => {
    opShowColumn.value.hide()
}

onUnmounted(() => {
    window.removeEventListener('message', actionRefreshData, false);
})
</script>