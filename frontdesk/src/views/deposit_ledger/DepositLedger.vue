<template>
    <div class="flex-col flex" style="height: calc(100vh - 92px);">
        <div>
            <ComHeader colClass="col-6" isRefresh @onRefresh="Refresh()">
                <template #start>
                    <div class="text-xl md:text-2xl"> {{ $t('Deposit Ledger') }} </div>
                </template>
                <template #end>
                    <Button class="border-none white-space-nowrap" :label="isMobile ? 'Add New ' : $t('Add New Deposit Ledger') " icon="pi pi-plus"
                        @click="onAddDepositLedger()" />
                </template>
            </ComHeader>
        </div>
        <div class="mb-3 flex justify-between">
            <div class="flex gap-2">
                <div v-if="!isMobile" >
                    <span class="p-input-icon-left">
                        <i class="pi pi-search" />
                        <InputText v-model="filter.keyword" :placeholder="$t('Search')" @input="onSearch" />
                    </span>
                </div>
                <div>
                    <Button icon="pi pi-sliders-h" class="content_btn_b" @click="advanceSearch" />
                </div>
                <div v-if="gv.isNotEmpty(filter, 'search_date_type')">
                    <Button class="content_btn_b" :label="isMobile ? 'Clear' : 'Clear Filter' " icon="pi pi-filter-slash" @click="onClearFilter" />
                </div>
                <div>

                </div>
            </div>
            <div class="flex gap-2">
                <div>
                    <ComOrderBy doctype="Deposit Ledger" @onOrderBy="onOrderBy" />
                </div>
                <Button class="content_btn_b h-full px-3" @click="toggleShowColumn">
                    <ComIcon icon="iconEditGrid" height="16px"></ComIcon>
                </Button>
            </div>
        </div>
        <div class="overflow-auto h-full">

            <ComPlaceholder text="No Data" height="70vh" :loading="gv.loading" :is-not-empty="data.length > 0">
                <DataTable class="res_list_scroll" :resizableColumns="true" showGridlines stateStorage="local"
                    stateKey="table_deposit_ledger_state" :reorderableColumns="true" :value="data"
                    tableStyle="min-width: 50rem" @row-dblclick="onViewReservationStayDetail">
                    <Column
                        v-for="c of columns.filter(r => selectedColumns.includes(r.fieldname) && r.label && (r.can_view_rate || 'Yes') == 'Yes')"
                        :key="c.fieldname" :field="c.fieldname" :header="$t(c.label)"
                        :headerClass="[c.header_class, 'white-space-nowrap'] || 'white-space-nowrap'"
                        :bodyClass="c.header_class || ''" :frozen="c.frozen">
                        <template #body="slotProps">
                            <Button v-if="c.fieldtype == 'Link' && slotProps.data[c.fieldname]"
                                class="p-0 link_line_action1" @click="onOpenLink(c, slotProps.data)" link>
                                {{ slotProps.data[c.fieldname] }}
                                <span v-if="c.extra_field_separator" v-html="c.extra_field_separator"> </span>
                                <span v-if="c.extra_field">{{ slotProps.data[c.extra_field] }} </span>
                            </Button>
                            <span v-else-if="c.fieldtype == 'Date'">{{
                                moment(slotProps.data[c.fieldname]).format("DD-MM-YYYY") }}
                            </span>
                            <ComTimeago v-else-if="c.fieldtype == 'Timeago'" :date="slotProps.data[c.fieldname]" />
                            <div v-else-if="c.fieldtype == 'Room'" v-if="slotProps?.data && slotProps?.data?.room_numbers">
                                <template v-for="(item, index) in slotProps.data.room_numbers.split(',')" :key="index">
                                    <span>{{ item }}</span>
                                    <span v-if="index != Object.keys(slotProps.data.room_numbers.split(',')).length - 1">,
                                    </span>
                                </template>
                            </div>
                            <CurrencyFormat v-else-if="c.fieldtype == 'Currency'" :value="slotProps.data[c.fieldname]" />
                            <template v-else-if="c.fieldtype == 'Status'">
                                <ComOpenStatus :status="slotProps.data[c.fieldname]" />
                            </template>
                            <template v-else-if="c.fieldname == 'owner' || c.fieldname == 'modified_by'">
                                <span>{{  slotProps.data[c.fieldname].split("@")[0] }}</span>
                            </template>

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
            <Paginator class="p__paginator" v-model:first="pageState.activePage" :rows="pageState.rows"
                :totalRecords="pageState.totalRecords" :rowsPerPageOptions="[20, 30, 40, 50]" @page="pageChange">
                <template #start="slotProps">
                    <strong>{{ $t('Total Records') }} : <span class="ttl-column_re">{{ pageState.totalRecords }}</span></strong>
                </template>
            </Paginator>
        </div>
    </div>
    <OverlayPanel ref="opShowColumn" id="res_list_hideshow" style="width:30rem;">
        <ComOverlayPanelContent title="Show / Hide Columns" @onSave="OnSaveColumn" ttl_header="mb-2" titleButtonSave="Save"
            @onCancel="onCloseColumn">
            <template #top>
                <span class="p-input-icon-left w-full mb-3">
                    <i class="pi pi-search" />
                    <InputText v-model="filter.search_field" :placeholder="$t('Search')" class="w-full" />
                </span>
            </template>
            <ul class="res__hideshow">
                <li class="mb-2" v-for="(c, index) in getColumns.filter(r => r.label)" :key="index">
                    <Checkbox v-model="c.selected" :binary="true" :inputId="c.fieldname" />
                    <label :for="c.fieldname"> {{ $t(c.label) }}</label>
                </li>
            </ul>
            <template #footer-left>
                <Button class="border-none" icon="pi pi-replay" @click="onResetTable" :label="$t('Reset List')" />
            </template>
        </ComOverlayPanelContent>
    </OverlayPanel>
    <OverlayPanel ref="showAdvanceSearch" style="max-width:50rem">
        <ComOverlayPanelContent title="Advance Filter" @onSave="onClearFilter" titleButtonSave="Clear Filter"
            icon="pi pi-filter-slash" :hideButtonClose="false" @onCancel="onCloseAdvanceSearch">
            <div class="grid">
                <div class="col-12" v-if="isMobile" >
                    <span class="p-input-icon-left w-full">
                        <i class="pi pi-search" />
                        <InputText v-model="filter.keyword" class="w-full" :placeholder="$t('Search')" @input="onSearch" />
                    </span>
                </div>
                    <ComAutoComplete class="col-6 input-wrp-search-autocomplete" width="100%" optionLabel="customer_name_en" optionValue="name"
                        v-model="filter.selected_guest" @onSelected="onSearch" placeholder="Guest" doctype="Customer" />

                    <ComSelect class="col-6" v-model="filter.selected_status" @onSelected="onSearch"
                        placeholder="Status" :options="['Open', 'Closed']" />
                    <ComSelect class="col-6" isFilter optionLabel="room_type" optionValue="name"
                        v-model="filter.selected_room_type" @onSelected="onSearch" placeholder="Room Type" doctype="Room Type"
                        :filters="{ property: property.name }"></ComSelect>

                    <ComSelect class="col-6" isFilter groupFilterField="room_type_id"
                        :groupFilterValue="filter.selected_room_type" optionLabel="room_number" optionValue="name"
                        v-model="filter.selected_room_number" @onSelected="onSearch" placeholder="Room Name" doctype="Room"
                        :filters="{ property: property.name }"></ComSelect>
             
                
                <div class="col-6">
                    <Checkbox inputId="filter_date" @change="onFilterDate" v-model="filter.filter_date" :binary="true"/>
                    <lable class="ml-1" for="filter_date">{{ $t('Filter Date') }} </lable>
                </div>
                <div class="col-6">
                    <Calendar class="w-full" v-if="filter.filter_date" v-model="filter.selected_dates" :selectOtherMonths="true" panelClass="no-btn-clear"
                    @date-select="onSearch" dateFormat="dd-mm-yy" showIcon showButtonBar selectionMode="range" placeholder="Date Range" />
                </div>
            </div>

                <div class="col-6" v-if="filter.search_date_type">
                    <Calendar :selectOtherMonths="true" class="w-full" hideOnRangeSelection v-if="filter.search_date_type"
                        dateFormat="dd-MM-yy" v-model="filter.date_range" selectionMode="range" :manualInput="false"
                        @date-select="onDateSelect" placeholder="Select Date Range" showIcon />
                </div>
        </ComOverlayPanelContent>
    </OverlayPanel>
</template>
<script setup>
import { inject, ref, reactive, useToast, getCount, getDocList, onMounted, getApi, computed, onUnmounted } from '@/plugin'
import { useDialog } from 'primevue/usedialog';
import Paginator from 'primevue/paginator';
import ComOrderBy from '@/components/ComOrderBy.vue';
import ComAddDepositLedger from '@/views/deposit_ledger/components/ComAddDepositLedger.vue';
import {i18n} from '@/i18n';
const { t: $t } = i18n.global;
const showAdvanceSearch = ref()
const moment = inject("$moment")
const gv = inject("$gv")
const toast = useToast()
const opShowColumn = ref();
const isMobile = ref(window.isMobile) 
const property = JSON.parse(localStorage.getItem("edoor_property"))
 
const columns = ref([
    { fieldname: 'name', label: 'Deposit #', fieldtype: "Link", post_message_action: "view_deposit_ledger_detail", default: true },
    { fieldname: 'posting_date', label: 'Posting Date', fieldtype: "Date", header_class: "text-center", frozen: true, default: true },
    { fieldname: 'guest', label: 'Guest', fieldtype: "Link", extra_field: "guest_name", extra_field_separator: "-", post_message_action: "view_customer_detail", default: true },
    { fieldname: 'room_number', label: 'Room', default: true, extra_field: "room_type", },
    { fieldname: 'total_debit', label: 'Debit', fieldtype: "Currency", header_class: "text-right", default: true, can_view_rate: window.can_view_rate ? 'Yes' : 'No' },
    { fieldname: 'total_credit', label: 'Credit', fieldtype: "Currency", header_class: "text-right", default: true, can_view_rate: window.can_view_rate ? 'Yes' : 'No' },
    { fieldname: 'balance', label: 'Balance', fieldtype: "Currency", header_class: "text-right", default: true, can_view_rate: window.can_view_rate ? 'Yes' : 'No' },
    { fieldname: 'owner', label: 'Created By', },
    { fieldname: 'creation', fieldtype: "Timeago", label: 'Creation', header_class: "text-center", },
    { fieldname: 'status', fieldtype: "Status", label: 'Status', header_class: "text-center", default: true },
    { fieldname: 'modified_by', label: 'Modified By', default: true },
    { fieldname: 'modified', fieldtype: "Timeago", label: 'Last Modified', header_class: "text-center", default: true },

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
    localStorage.setItem("page_state_deposit_ledger", JSON.stringify(pageState.value))
    opShowColumn.value.toggle(event);
    loadData()
}
const onCloseColumn = () => {
    opShowColumn.value.hide()
}


const data = ref([])

const filter = ref({selected_status:"Open",filter_date:false})
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
    let filters = [
        ["Deposit Ledger", "property", '=', property.name]
    ]
    if(filter.value.filter_date){
        
        if(filter.value.selected_dates){
            
            if(filter.value.selected_dates.length>1){
                
                if (filter.value.selected_dates[0] && filter.value.selected_dates[1]){
                    
                    filters.push(["posting_date", 'between', [moment(filter.value.selected_dates[0]).format("YYYY-MM-DD"),moment(filter.value.selected_dates[1]).format("YYYY-MM-DD")]])            
                     
                }else {
                    return
                }
            }else {
                return
            }
        }
    }
    if (filter.value?.keyword) {
        filters.push(["name", 'like', '%' + filter.value.keyword + '%'])
    }
    if (filter.value?.selected_status) {
        filters.push(["status", "=", filter.value.selected_status])
    }
    if (filter.value?.selected_guest) {
        filters.push(["guest", "=", filter.value.selected_guest])
    }
    if (filter.value?.selected_room_type) {
        filters.push(["room_type_id", "=", filter.value.selected_room_type])
    }
    if (filter.value?.selected_room_number) {
        filters.push(["room_id", '=', filter.value.selected_room_number])
    }

    

    let fields = [...columns.value.map(r => r.fieldname), ...columns.value.map(r => r.extra_field)]
    fields = [...fields, ...selectedColumns.value]
    fields = [...new Set(fields.filter(x => x))]
    gv.loading = show_loading
    getDocList('Deposit Ledger', {
        fields: fields,
        orderBy: {
            field: '`tabDeposit Ledger`.' + pageState.value.order_by,
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
    localStorage.setItem("page_state_deposit_ledger", JSON.stringify(pageState.value))
}

function getTotalRecord(filters) {
    getCount('Deposit Ledger', filters)
        .then((count) => pageState.value.totalRecords = count || 0)
}

function onOrderBy(data) {
    pageState.value.order_by = data.order_by
    pageState.value.order_type = data.order_type
    pageState.value.page = 0
    loadData()
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

function onFilterDate(){
    if (!filter.value.filter_date){
        onSearch()
    }
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

getApi('frontdesk.get_working_day', {
    property: JSON.parse(localStorage.getItem("edoor_property")).name
}).then((r) => {
    working_date.value = r.message?.date_working_day

})

const actionRefreshData = async function (e) {
    if (e.isTrusted && typeof (e.data) != 'string') {
        if(e.data.action=="DepositLedger"){
            setTimeout(()=>{
                loadData(false)
            },1000*3)
            
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
    window.addEventListener('message', actionRefreshData, false)

    let state = localStorage.getItem("page_state_deposit_ledger")
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
    getApi("frontdesk.get_meta", { doctype: "Deposit Ledger" }).then((result) => {
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
    onClearFilter()
})

function onResetTable() {
    localStorage.removeItem("page_state_deposit_ledger")
    localStorage.removeItem("table_deposit_ledger_state")
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
    window.removeEventListener('message', actionRefreshData, false)
})


function onAddDepositLedger(data) {
    dialog.open(ComAddDepositLedger, {
        data: { data },
        props: {
            header: $t(`Add New Deposit Ledger`),
            style: {
                width: '50vw',
            },
            modal: true,
            closeOnEscape: false,
            position: 'top',
            breakpoints:{
                '960px': '50vw',
                '640px': '100vw'
            },
        },
        onClose: (options) => {
            const data = options.data;
            if (data) {
                window.postMessage("view_deposit_ledger_detail|" + data.name,"*")
                setTimeout(() => {
                    loadData(false)    
                }, 5000);
                
            }
        }
    });
}
</script>

 