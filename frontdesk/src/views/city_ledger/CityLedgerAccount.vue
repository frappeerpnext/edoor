<template>
    <div class="flex-col flex" style="height: calc(100vh - 92px);">
        <div>
            <ComHeader colClass="col-6" isRefresh @onRefresh="Refresh()">
                <template #start>
                    <div class="text-xl md:text-2xl">City Ledger Account</div>
                </template>
                <template #end>
                    <Button class="border-none" @click="onAddCityLedgerAccount">
                        
                        <template v-if="!isMobile">
                            {{ $t('Add New City Ledger Account') }}

                        </template>
                        <template v-else>
                            {{ $t('Add New') }}                             
                        </template>
                        </Button>
                </template>
            </ComHeader>
            <div class="mb-3">
                <div class="flex justify-between">
                    <div class="flex flex-wrap gap-2">
                        <div v-if="!isMobile" class="w-20rem">
                            <div class="p-input-icon-left w-full">
                                <i class="pi pi-search" />
                                <InputText class="w-full" v-model="filter.keyword" :placeholder=" $t('Search') " @input="onSearch" />
                            </div>
                        </div>
                        <div>
                            <div class="flex gap-3">
                                <Button icon="pi pi-sliders-h" class="content_btn_b" @click="advanceFilter" />
                                <div v-if="gv.isNotEmpty(filter)">
                                    <Button class="content_btn_b" :label="isMobile ? $t('Clear') : $t('Clear Filter')" icon="pi pi-filter-slash" @click="onClearFilter" />
                                </div>
                            </div>
                        </div>
                        <OverlayPanel ref="showAdvanceSearch">
                            <ComOverlayPanelContent title="Advance Filter" @onSave="onClearFilter" titleButtonSave="Clear Filter" icon="pi pi-filter-slash" :hideButtonClose="false" @onCancel="onCloseAdvanceSearch">
                                <div class="grid">
                                    <div v-if="isMobile" class="col-12">
                            <div class="p-input-icon-left w-full">
                                <i class="pi pi-search" />
                                <InputText class="w-full" v-model="filter.keyword" :placeholder="$t('Search')" @input="onSearch" />
                            </div>
                        </div>
                                    <div class="col-6">
                                        <ComAutoComplete :filters="[['property', '=', property.name]]"
                                            v-model="filter.selected_city_ledger_type" @onSelected="onSearch"
                                            placeholder="City Ledger Type" doctype="City Ledger Type"  class="pb-2 w-full"/> 
                                    </div>
                                    <div class="col-6">
                                        <ComAutoComplete :filters="[['property', '=', property.name]]"
                                            v-model="filter.selected_business_source" @onSelected="onSearch"
                                            placeholder="Business Source" doctype="Business Source"  class="pb-2 w-full"/>
                                    </div>
                                </div>
                            </ComOverlayPanelContent>
                        </OverlayPanel>
                        
                    </div>
                    <div class="flex grap-2">
                        <div class="px-2">
                            <ComOrderBy doctype="City Ledger" @onOrderBy="onOrderBy" />
                        </div>
                        <div>
                            <Button class="content_btn_b h-full px-3" @click="toggleShowColumn">
                            <ComIcon icon="iconEditGrid" height="16px"></ComIcon>
                        </Button>
                        </div>
                        
                    </div>
                </div>
            </div>
        </div>
        <div class="overflow-auto h-full">
            <ComPlaceholder text="No Data" :loading="gv.loading" :is-not-empty="data.length > 0">
                <DataTable 
                    resizableColumns 
                    columnResizeMode="expand" 
                    showGridlines stateStorage="local"
                    stateKey="table_city_ledger_list_state" 
                    :reorderableColumns="true" 
                    :value="data"
                    tableStyle="min-width: 50rem" 
                    @row-dblclick="onViewReservationStayDetail" 
                    :rows="20">
                    <Column v-for="c of columns.filter(r => selectedColumns.includes(r.fieldname) && r.label)"
                        :key="c.fieldname" :field="c.fieldname" :header="$t(c.label)" :headerClass="c.header_class || ''"
                        :bodyClass="c.header_class || ''" :frozen="c.frozen">

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
                                moment(slotProps.data[c.fieldname]).format("DD-MM-YYYY h:mm a") }} </span>
                            <ComTimeago v-else-if="c.fieldtype == 'Timeago'" :date ="slotProps.data[c.fieldname]"/>
                            <div v-else-if="c.fieldtype == 'Room'" class="rounded-xl px-2 me-1 bg-gray-edoor inline room-num"
                                v-if="slotProps?.data && slotProps?.data?.rooms">
                                <template v-for="(item, index) in slotProps.data.rooms.split(',')" :key="index">
                                    <span>{{ item }}</span>
                                    <span v-if="index != Object.keys(slotProps.data.rooms.split(',')).length - 1">, </span>
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
        <div v-if="data.length > 0">
            <Paginator class="p__paginator" v-model:first="pageState.activePage" :rows="pageState.rows" :totalRecords="pageState.totalRecords"
                :rowsPerPageOptions="[20, 30, 40, 50]" :pageLinkSize="isMobile ? '2' : '5'" @page="pageChange">
                <template #start="slotProps">
                    <strong v-if="!isMobile">{{ $t('Total Records') }} : <span class="ttl-column_re">{{ pageState.totalRecords }}</span></strong>
                </template>
            </Paginator>
        </div>
    </div>

    <OverlayPanel ref="opShowColumn" style="width:35rem;">
        <ComOverlayPanelContent title="Show / Hide Columns" @onSave="OnSaveColumn" ttl_header="mb-2" titleButtonSave="Save"
            @onCancel="onCloseColumn">
            <template #top>
                <div class="p-input-icon-left mb-3 w-full">
                    <i class="pi pi-search" />
                    <InputText class="w-full" v-model="filter.search_field" :placeholder="$t('Search') " />
                </div>
            </template>
            <div class="grid">
                <div class="col-6 py-1" v-for="(c, index) in getColumns.filter(r => r.label)" :key="index">

                    <Checkbox v-model="c.selected" :binary="true" :inputId="c.fieldname" />
                    <label :for="c.fieldname">{{ $t(c.label)  }}</label>
                </div>
            </div>
            <template #footer-left>
                <Button class="border-none" icon="pi pi-replay" @click="onResetTable" :label=" $t('Reset List') " />
            </template>
        </ComOverlayPanelContent>
        <!-- <Button @click="OnSaveColumn">Save</Button> -->
    </OverlayPanel>
</template>
<script setup>
import { inject, ref, getCount, getDocList, onMounted, onUnmounted, getApi, useDialog, computed } from '@/plugin'
import Paginator from 'primevue/paginator';
import ComOrderBy from '@/components/ComOrderBy.vue';
import { Timeago } from 'vue2-timeago'
import ComAddCityLedgerAccount from '@/views/city_ledger/components/ComAddCityLedgerAccount.vue';
import {i18n} from '@/i18n';
const { t: $t } = i18n.global;
const moment = inject("$moment")
const gv = inject("$gv")
// const toast = useToast()
const dialog = useDialog()
const opShowColumn = ref();
const data = ref([])
const filter = ref({})
const pageState = ref({ order_by: "modified", order_type: "desc", page: 0, rows: 20, totalRecords: 0, activePage: 0 })
const property = JSON.parse(localStorage.getItem("edoor_property"))
const isMobile = ref(window.isMobile) 


const columns = ref([
    { fieldname: 'name', label: 'City Ledger Code', header_class: 'text-center', fieldtype: "Link", post_message_action: "view_city_ledger_detail", default: true },
    { fieldname: 'city_ledger_name', label: 'City Ledger Name', default: true },
    { fieldname: 'city_ledger_type', label: 'City Ledger Type', default: true },
    { fieldname: 'business_source', label: 'Business Source', default: true },
    { fieldname: 'company_name', label: 'Company Name', default: true },
    { fieldname: 'phone_number', label: 'Phone Number', default: true },
    { fieldname: 'email_address', label: 'Email Address', default: true },
    { fieldname: 'contact_name', label: 'Contact Name', default: true },
    { fieldname: 'contact_phone_number', label: 'Contact Phone Number', default: true },
    { fieldname: 'total_debit', label: 'Total Debit', fieldtype: "Currency", default: true, header_class: "text-right" },
    { fieldname: 'total_credit', label: 'Total Credit', fieldtype: "Currency", default: true, header_class: "text-right" },
    { fieldname: 'balance', label: 'Balance', fieldtype: "Currency", default: true, header_class: "text-right" },
])

const selectedColumns = ref([]);

const toggleShowColumn = (event) => {
    opShowColumn.value.toggle(event);
}

function OnSaveColumn(event) {
    selectedColumns.value = columns.value.filter(r => r.selected).map(x => x.fieldname)
    pageState.value.selectedColumns = selectedColumns.value
    localStorage.setItem("page_state_city_ledger", JSON.stringify(pageState.value))
    opShowColumn.value.toggle(event);
}

function onResetTable() {
    localStorage.removeItem("page_state_city_ledger")
    localStorage.removeItem("table_city_ledger_list_state")
    window.location.reload()
}

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

const Refresh = debouncer(() => {
    pageState.value.page = 0
    loadData();
}, 500);
function pageChange(page) {
    pageState.value.page = page.page
    pageState.value.rows = page.rows
    loadData()
}

function loadData(show_loading=true) {
    gv.loading = show_loading
    let filters = [
        ["property", "=", property.name]
    ]
    if (filter.value?.keyword) {
        filters.push(["keyword", 'like', '%' + filter.value.keyword + '%'])
    }
    if (filter.value?.selected_city_ledger_type) {
        filters.push(["city_ledger_type", '=', filter.value.selected_city_ledger_type])
    }
    if (filter.value?.selected_business_source) {
        filters.push(["business_source", '=', filter.value.selected_business_source])
    }

    let fields = [...columns.value.map(r => r.fieldname), ...columns.value.map(r => r.extra_field)]
    fields = [...fields, ...selectedColumns.value]

    fields = [...new Set(fields.filter(x => x))]

    getDocList('City Ledger', {

        fields: fields,
        orderBy: {
            field: '`tabCity Ledger`.' + pageState.value.order_by,
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

    });
    getTotalRecord(filters)
    localStorage.setItem("page_state_city_ledger", JSON.stringify(pageState.value))

}
function getTotalRecord(filters) {
    getCount('City Ledger', filters)
        .then((count) => pageState.value.totalRecords = count || 0)
}
function onOrderBy(data) {
    pageState.value.order_by = data.order_by
    pageState.value.order_type = data.order_type
    pageState.value.page = 0
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

const actionRefreshData = async function (e) {
    if (e.isTrusted && typeof (e.data) != 'string') {
        if(e.data.action=="CityLedgerAccount"){
            setTimeout(()=>{
                loadData(false)
            },1000*3)
            
        }
    };
}

onMounted(() => {
    //socket reload
    window.addEventListener('message', actionRefreshData, false)
    if(window.isMobile){
        let elem = document.querySelectorAll(".p-dialog");
        if (elem){
            elem = elem[elem.length-1]
            elem?.classList.add("p-dialog-maximized"); // adds the maximized class
        }
    }
    let state = localStorage.getItem("page_state_city_ledger")
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
    getApi("frontdesk.get_meta", { doctype: "City Ledger" }).then((result) => {
 
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

function onAddCityLedgerAccount() {
    if(!gv.cashier_shift?.name){
        gv.toast('error', 'Please Open Cashier Shift.')
        return
    }
    dialog.open(ComAddCityLedgerAccount, {
        data: {
            // name: name.value,
        },
        props: {
            header: `Add New City Ledger Account`,
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
                loadData()
            }
        }
    });
}

onUnmounted(() => {
    window.removeEventListener('message', actionRefreshData, false)
})

const showAdvanceSearch = ref()
const advanceFilter = (event) => {
    showAdvanceSearch.value.toggle(event);
}

const onClearFilter = () => {
    filter.value = {};
    loadData();
    showAdvanceSearch.value.hide()
}

const onCloseAdvanceSearch = () => {
    showAdvanceSearch.value.hide()
}

const onCloseColumn = () => {
    opShowColumn.value.hide()
}

</script>