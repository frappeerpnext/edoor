<template>
    <div class="flex-col flex" style="height: calc(100vh - 92px);">
        <div>
            <ComHeader isRefresh @onRefresh="Refresh()">
                <template #start>
                    <div class="text-2xl">Vendor</div>
                </template>
                <template #end>
                    <Button class="border-none" label="Add New Vendor" icon="pi pi-plus" @click="onAddNewVendor" />
                </template>
            </ComHeader>
            <div class="mb-3 flex justify-between">
                <div class="flex flex-wrap gap-2">
                    <div>
                        <span class="p-input-icon-left">
                            <i class="pi pi-search" />
                            <InputText v-model="filter.keyword" placeholder="Search" @input="onSearch" />
                        </span>
                    </div>
                    <div>
                        <Button icon="pi pi-sliders-h" class="content_btn_b" @click="advanceFilter" />
                    </div>
                    <div v-if="gv.isNotEmpty(filter)">
                        <Button class="content_btn_b" label="Clear Filter" icon="pi pi-filter-slash"
                            @click="onClearFilter" />
                    </div>

                </div>
                <div class="flex grap-2">
                    <div class="px-2">
                        <ComOrderBy doctype="Vendor" @onOrderBy="onOrderBy" />
                    </div>
                    <Button class="content_btn_b h-full px-3" @click="toggleShowColumn">
                        <ComIcon icon="iconEditGrid" height="16px"></ComIcon>
                    </Button>
                </div>
            </div>
        </div>
        <div class="overflow-auto h-full">
            <ComPlaceholder text="No Data" :loading="gv.loading" :is-not-empty="pageState.totalRecords > 0">
                <DataTable class="res_list_scroll" :resizableColumns="true" columnResizeMode="fit" showGridlines
                    stateStorage="local" stateKey="table_vendor_list_state" scrollable :reorderableColumns="true"
                    :value="data" tableStyle="min-width: 50rem" @row-dblclick="onViewReservationStayDetail">
                    <Column v-for="c of columns.filter(r => selectedColumns.includes(r.fieldname) && r.label)"
                        :key="c.fieldname" :headerClass="c.header_class || ''" :field="c.fieldname" :header="c.label"
                        :labelClass="c.header_class || ''" :bodyClass="c.header_class || ''" :frozen="c.frozen">
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
            <Paginator class="p__paginator" :rows="pageState.rows" :totalRecords="pageState.totalRecords"
                :rowsPerPageOptions="[20, 30, 40, 50]" @page="pageChange">
                <template #start="slotProps">
                    <strong>Total Records: <span class="ttl-column_re">{{ pageState.totalRecords }}</span></strong>
                </template>
            </Paginator>
        </div>
    </div>
    <OverlayPanel ref="opShowColumn" style="width:35rem">
        <ComOverlayPanelContent title="Show / Hide Columns" @onSave="OnSaveColumn" ttl_header="mb-2" titleButtonSave="Save"
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

    <OverlayPanel ref="showAdvanceSearch" style="width:40rem">
        <ComOverlayPanelContent title="Advance Filter" @onSave="onClearFilter" titleButtonSave="Clear Filter"
            icon="pi pi-filter-slash" :hideButtonClose="false" @onCancel="onCloseAdvanceSearch">
            <div class="grid">
                <div class="col-6">
                    <ComSelect width="100%" v-model="filter.selected_vendor_type" @onSelected="onSearch" placeholder="Vendor Type"
                        :options="['Individual', 'General', 'Company']" />
                </div>
                <div class="col-6">
                    <ComSelect isFull v-model="filter.selected_vendor_group" @onSelected="onSearch" placeholder="Vendor Group"
                        doctype="Vendor Group" isFilter />
                </div>
            </div>
        </ComOverlayPanelContent>
    </OverlayPanel>
</template>
<script setup>
import { inject, ref, getCount, getDocList, onMounted, getApi, useDialog, computed, onUnmounted } from '@/plugin'
import Paginator from 'primevue/paginator';
import ComOrderBy from '@/components/ComOrderBy.vue';
import { Timeago } from 'vue2-timeago'
import ComAddVendor from '@/views/vendor/ComAddVendor.vue';

const moment = inject("$moment")
const gv = inject("$gv")
const dialog = useDialog()
const opShowColumn = ref();
const data = ref([])
const filter = ref({})
const showAdvanceSearch = ref()
const pageState = ref({ order_by: "modified", order_type: "desc", page: 0, rows: 20, totalRecords: 0 })
const property = JSON.parse(localStorage.getItem("edoor_property"))

const columns = ref([
    { fieldname: 'name', label: 'Vendor', default: true, fieldtype: "Link", post_message_action: "view_vendor_detail", }, //fieldtype:"Link", 
    { fieldname: 'vendor_name', label: 'Vendor Name', default: true },
    { fieldname: 'vendor_type', label: 'Vendor Type', default: true },
    { fieldname: 'vendor_group', label: 'Vendor Group', default: true },
    { fieldname: 'company', label: 'Company', default: true },
    { fieldname: 'province', label: 'Province', default: true },
    { fieldname: 'phone_number', label: 'Phone Number', default: true },
    { fieldname: 'email_address', label: 'Email Address', default: true },
    { fieldname: 'website', label: 'Website', default: true },

    { fieldname: 'owner', label: 'Created By' },
    { fieldname: 'creation', fieldtype: "Timeago", label: 'Creation', header_class: "text-center", default: true },
    { fieldname: 'modified_by', label: 'Modified By' },
    { fieldname: 'modified', fieldtype: "Timeago", label: 'Last Modified', header_class: "text-center" },

    { fieldname: 'note', label: 'Note', default: true },

])

const selectedColumns = ref([]);
const toggleShowColumn = (event) => {
    opShowColumn.value.toggle(event);
}

function OnSaveColumn(event) {
    selectedColumns.value = columns.value.filter(r => r.selected).map(x => x.fieldname)
    pageState.value.selectedColumns = selectedColumns.value
    localStorage.setItem("page_state_vendor", JSON.stringify(pageState.value))
    opShowColumn.value.toggle(event);
    loadData()
}

function onResetTable() {
    localStorage.removeItem("page_state_vendor")
    localStorage.removeItem("table_vendor_list_state")
    window.location.reload()
}
const getColumns = computed(() => {
    if (filter.value.search_field) {
        return columns.value.filter(r => (r.label || "").toLowerCase().includes(filter.value.search_field.toLowerCase())).sort((a, b) => a.label.localeCompare(b.label));
    } else {
        return columns.value.filter(r => r.label).sort((a, b) => a.label.localeCompare(b.label));
    }
})



const Refresh = debouncer(() => {
    pageState.value.page = 0
    loadData()
}, 500);

function pageChange(page) {
    pageState.value.page = page.page
    pageState.value.rows = page.rows

    loadData()
}

function loadData(show_loading = true) {
    gv.loading = show_loading
    let filters = []

    if (filter.value?.keyword) {
        filters.push(["keyword", 'like', '%' + filter.value.keyword + '%'])
    }
    if (filter.value?.selected_vendor_type) {
        filters.push(["vendor_type", '=', filter.value.selected_vendor_type])
    }
    if (filter.value?.selected_vendor_group) {
        filters.push(["vendor_group", '=', filter.value.selected_vendor_group])
    }

    let fields = [...columns.value.map(r => r.fieldname), ...columns.value.map(r => r.extra_field)]
    fields = [...fields, ...selectedColumns.value]

    fields = [...new Set(fields.filter(x => x))]

    getDocList('Vendor', {

        fields: fields,
        orderBy: {
            field: '`tabVendor`.' + pageState.value.order_by,
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
    localStorage.setItem("page_state_vendor", JSON.stringify(pageState.value))
}

function getTotalRecord(filters) {
    getCount('Vendor', filters)
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

onMounted(() => {
    let state = localStorage.getItem("page_state_vendor")
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
    getApi("frontdesk.get_meta", { doctype: "Vendor" }).then((result) => {
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


    window.socket.on("Vendor", (arg) => {

        if (arg == window.property_name) {

            loadData(false)

        }
    })
})

function onAddNewVendor() {
    if(!gv.cashier_shift?.name){
        gv.toast('error', 'Please Open Cashier Shift.')
        return
    }
    dialog.open(ComAddVendor, {
        data: {
            // name: name.value,
        },
        props: {
            header: `Add New Vendor`,
            style: {
                width: '50vw',
            },
            modal: true,
            closeOnEscape: false,
            position: 'top'
        },
        onClose: (options) => {
            const data = options.data;
            if (data) {
                loadData(data.name)
            }
        }
    });
}
function onOpenLink(column, data) {
    window.postMessage(column.post_message_action + "|" + data[column.fieldname], '*')
}

const onCloseColumn = () => {
    opShowColumn.value.hide()
}

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

onUnmounted(() => {
    window.socket.off("Vendor");
})

</script>