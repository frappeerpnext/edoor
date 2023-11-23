<template>
    <div>
        <ComHeader isRefresh @onRefresh="Refresh()">
            <template #end>
                <Button class="conten-btn" @click="AddTransaction(d)"
                    v-for="(d, index) in setting.account_group.filter(r => r.show_in_city_ledger == 1)" :key="index">Post
                    {{ d.account_name }}</Button>
                <Button @click="viewCityLedgerReport" class="conten-btn">
                    <i class="pi pi-print mr-2"></i> Print 
                </Button>
            </template>
        </ComHeader>
        <div class="flex justify-between mb-3">
            <div class="flex gap-2">
                <div>
                    <div class="p-input-icon-left w-full">
                        <i class="pi pi-search" />
                        <InputText class="w-full" v-model="filter.keyword" placeholder="Search" @input="onSearch" />
                    </div>
                </div>
                <div class="w-5">
                    <ComAutoComplete class="w-full" v-model="filter.selected_guest" @onSelected="onSearch"
                        placeholder="Guest" doctype="Customer" isFilter />
                </div>
                <div class="flex gap-2">
                    <Button icon="pi pi-sliders-h" class="content_btn_b" @click="advanceFilter" />
                    <div v-if="gv.isNotEmpty(filter)">
                        <Button class="content_btn_b w-max" label="Clear Filter" icon="pi pi-filter-slash"
                            @click="onClearFilter" />
                    </div>
                </div>
                
            </div>
            <div class="flex grap-2">
                <div class="px-2">
                    <ComOrderBy doctype="Folio Transaction" @onOrderBy="onOrderBy" />
                </div>
                <Button class="content_btn_b h-full px-3" @click="toggleShowColumn">
                    <ComIcon icon="iconEditGrid" height="16px"></ComIcon>
                </Button>
            </div>
        </div>
        <OverlayPanel ref="showAdvanceSearch" style="width:50rem">
            <ComOverlayPanelContent title="Advance Filter" @onSave="onClearFilter" titleButtonSave="Clear Filter"
                icon="pi pi-filter-slash" :hideButtonClose="false" @onCancel="onCloseAdvanceSearch">
                <div class="grid">
                    <div class="col-6">
                        <ComAutoComplete class="w-full" v-model="filter.selected_reservation" @onSelected="onSearch"
                            placeholder="Reservation #" doctype="Reservation" :filters="{ property: property.name }" />
                    </div>
                    <div class="col-6">
                        <ComAutoComplete class="w-full" v-model="filter.selected_reservation_stay" @onSelected="onSearch"
                            placeholder="Reservation Stay" doctype="Reservation Stay" :filters="{ property: property.name }" />
                    </div>
                    <div class="col-6">
                        <ComSelect :filters="[['property', '=', property.name]]" v-model="filter.selected_room_type"
                            @onSelected="onSearch" placeholder="Room Type" doctype="Room Type" isFilter
                            optionLabel="room_type" optionValue="name" />
                    </div>
                    <div class="col-6">
                        <ComSelect class="w-full" :filters="[['property', '=', property.name]]" optionLabel="room_number"
                            optionValue="name" v-model="filter.selected_room" @onSelected="onSearch" placeholder="Room"
                            doctype="Room" isFilter />
                    </div>
                    <div class="col-6">
                        <ComAutoComplete class="w-full" @onSelected="onSearch" v-model="filter.selected_account_code"
                            placeholder="Account Code" doctype="Account Code" isFilter />
                    </div>
                    <div class="col-6">
                        <ComSelect class="w-full" @onSelected="onSearch" v-model="filter.selected_account_category"
                            placeholder="Account Category" doctype="Account Category" isFilter />
                    </div>
                    <div class="col-6">
                        <div class="flex relative">
                            <Calendar :selectOtherMonths="true" class="w-full" inputClass="pl-6" hideOnRangeSelection dateFormat="dd-mm-yy"
                                v-model="filter.date_range" selectionMode="range" :manualInput="false"
                                @date-select="onDateSelect" placeholder="Select Date Range"
                                :disabled="!filter.search_by_date" showIcon />
                            <div class="check-box-filter">
                                <Checkbox v-model="filter.search_by_date" :binary="true" @change="onChecked" />
                            </div>
                        </div>
                    </div>
                </div>
            </ComOverlayPanelContent>
        </OverlayPanel>
        <div v-if="cityLedgerAmountSummary">
            <div class="flex w-full gap-2 mb-3">
                <div class="flex flex-column rounded-lg  grow p-2 shadow-charge-total border">
                    <span class="text-500 uppercase text-sm text-end">opening Balance</span><span
                        class="text-xl line-height-2 font-semibold text-end">
                        <span>
                            <CurrencyFormat :value="cityLedgerAmountSummary?.opening_balance" />
                        </span></span>
                </div>
                <div class="flex flex-column rounded-lg grow p-2 shadow-charge-total border">
                    <span class="text-500 uppercase text-sm text-end">total debit</span><span
                        class="text-xl line-height-2 font-semibold text-end">
                        <span>
                            <CurrencyFormat :value="cityLedgerAmountSummary?.debit" />
                        </span></span>
                </div>
                <div class="flex flex-column rounded-lg grow p-2 shadow-charge-total  border">
                    <span class="text-500 uppercase text-sm text-end">total credit</span><span
                        class="text-xl line-height-2 font-semibold text-end">
                        <span>
                            <CurrencyFormat :value="cityLedgerAmountSummary?.credit" />
                        </span></span>
                </div>
                <div class="flex flex-column rounded-lg grow p-2 shadow-charge-total bg-green-50 border border-green-edoor">
                    <span class="text-500 uppercase text-sm text-end">balance</span><span
                        class="text-xl line-height-2 font-semibold text-end">
                        <span>
                            <CurrencyFormat :value="cityLedgerAmountSummary?.balance" />
                        </span></span>
                </div>
            </div>
        </div>
        <div style="min-height:42rem;">
            <ComPlaceholder text="No Data" :loading="loading" :is-not-empty="data.length > 0">
                <DataTable 
                :rowClass="rowClass"
                resizableColumns 
                columnResizeMode="fit" 
                showGridlines 
                stateStorage="local"
                stateKey="table_folio_transaction_list_state" 
                :reorderableColumns="false" 
                :value="data"
                tableStyle="min-width: 50rem;" 
                @row-dblclick="onViewReservationStayDetail" 
                scrollHeight="70vh">
                    <Column v-for="c of columns.filter(r => selectedColumns.includes(r.fieldname) && r.label)"
                        :key="c.fieldname" :field="c.fieldname" :header="c.label" :headerClass="c.header_class || ''"
                        :bodyClass="c.header_class || ''" :frozen="c.frozen">
                        <template #body="slotProps">
                            <Button v-if="c.fieldtype == 'Link' && slotProps.data[c.fieldname]" class="p-0 link_line_action1"
                                @click="onOpenLink(c, slotProps.data)" link>
                                {{ slotProps.data[c.fieldname] }}
                                <span v-if="c.extra_field_separator" v-html="c.extra_field_separator"> </span>
                                <span v-if="c.extra_field">{{ slotProps.data[c.extra_field] }} </span>
                            </Button>
                            <span v-else-if="c.fieldtype == 'Date'">{{ moment(slotProps.data[c.fieldname]).format("DD-MM-YYYY") }}
                            </span>
                            
                            <ComTimeago v-else-if="c.fieldtype == 'Timeago'" :date='slotProps.data[c.fieldname]' />
                
                            <template v-else-if="c.fieldtype == 'Owner'">
                                    <div v-if="slotProps?.data && slotProps?.data?.owner">
                                        <template v-for="(item) in slotProps.data?.owner?.split('@')[0]" :key="index">
                                            <span>{{ item }}</span>
                                        </template>
                                    </div>
                                </template>
                                
                            <CurrencyFormat v-else-if="c.fieldtype == 'currency'" :value="slotProps.data[c.fieldname]" />
                            <div v-else-if="c.fieldtype == 'Debit'">
                                <CurrencyFormat v-if="slotProps.data.type == 'Debit'" :value="slotProps.data[c.fieldname]" />
                                <span v-else>-</span>
                            </div>
                            <div v-else-if="c.fieldtype == 'Credit'">
                                <CurrencyFormat v-if="slotProps.data.type == 'Credit'" :value="slotProps.data[c.fieldname]" />
                                <span v-else>-</span>
                            </div>


                            <span v-else>
                                <div v-if="slotProps.data[c.fieldname]">
                                    {{ slotProps.data[c.fieldname] }}
                                    <span v-if="c.extra_field_separator" v-html="c.extra_field_separator"> </span>
                                    <span v-if="c.extra_field">{{ slotProps.data[c.extra_field] }} </span>
                                </div>
                            </span>

                        </template>

                    </Column>
                    <Column>
                        <template #body="slotProps">
                            <ComCityLedgerTransactionMoreOption @onEdit="onEditFolioTransaction(slotProps.data.name)" @onDelete="onDeleteCityLedgerTransaction(slotProps.data.name)"/>
                        </template>
                    </Column>
                </DataTable>
                <Paginator class="p__paginator bg-ed-paging" :rows="pageState.rows" :totalRecords="pageState.totalRecords"
                    :rowsPerPageOptions="[20, 30, 40, 50]" @page="pageChange">
                    <template #start="slotProps">
                        <strong>Total Records: <span class="ttl-column_re">{{ pageState.totalRecords }}</span></strong>
                    </template>
                </Paginator>
            </ComPlaceholder>
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
</template>
<script setup>
import { inject, ref, useConfirm, watch, getCount, getDocList, onMounted, onUnmounted, getApi, useDialog, computed, deleteDoc } from '@/plugin'
import Paginator from 'primevue/paginator';
import ComOrderBy from '@/components/ComOrderBy.vue';
import ComDialogNote from "@/components/form/ComDialogNote.vue";
import ComCityLedgerTransactionMoreOption from "../components/ComCityLedgerTransactionMoreOption.vue"
import ComPrintReservationStay from '@/views/reservation/components/ComPrintReservationStay.vue'
import ComAddFolioTransaction from '@/views/reservation/components/ComAddFolioTransaction.vue';
const props = defineProps({
    name: String
})
const confirm = useConfirm()
const moment = inject("$moment")
const gv = inject("$gv")
const dialog = useDialog()
const opShowColumn = ref();
const cityLedgerAmountSummary = ref()
const data = ref([])
const filter = ref({})
const loading = ref(false)
const pageState = ref({ order_by: "modified", order_type: "desc", page: 0, rows: 20, totalRecords: 0 })
const property = JSON.parse(localStorage.getItem("edoor_property"))
const setting = JSON.parse(localStorage.getItem("edoor_setting"))
const working_day = JSON.parse(localStorage.getItem("edoor_working_day"))
const dialogRef = inject("dialogRef")
const rowClass = (data) => {
    return [{ 'auto-post': data.is_auto_post }];

};
const viewCityLedgerReport = () => {
    dialog.open(ComPrintReservationStay, {
        data: {
            doctype: "Reservation%20Stay",
            reservation_stay: data.value.reservation_stay,
            folio_number: name.value,
            report_name: gv.getCustomPrintFormat("eDoor Reservation Stay Folio Summary Report"),
            // "eDoor%20Reservation%20Stay%20Folio%20Summary%20Report",
            view: "print"
        },
        props: {
            header: "Folio Summary Report",
            style: {
                width: '80vw',
            },
            position:"top",
            modal: true,
            maximizable: true,
            closeOnEscape: false

        },
    });
}

const columns = ref([
    { fieldname: 'name', label: 'Folio Transaction', header_class: "text-center", fieldtype: "Link", post_message_action: "view_folio_transaction_detail", default: true },
    { fieldname: 'posting_date', label: 'Date', fieldtype: "Date", default: true, header_class: "text-center" },
    { fieldname: 'room_number', label: 'Room(s)',fieldtype: "Rooms" ,  header_class: "text-center" },
    { fieldname: 'account_code', extra_field: "account_name", extra_field_separator: "-", label: 'Account Code', default: true },
    { fieldname: 'guest', extra_field: "guest_name", extra_field_separator: "-", label: 'Guest', fieldtype: "Link", post_message_action: "view_guest_detail", default: true },
    { fieldname: 'total_amount', label: 'Debit', fieldtype: "Debit" , default: true, header_class: "text-right" },
    { fieldname: 'total_amount', label: 'Credit', fieldtype: "Credit", default: true, header_class: "text-right" },
    { fieldname: 'type', default: true },
    { fieldname: 'is_auto_post' },
    { fieldname: 'parent_reference' },
    { fieldname: 'payment_by', label: 'Pay by' },
    { fieldname: 'payment_by_phone_number', label: 'Phone No.' },
    { fieldname: 'owner', label: 'User', default: true,fieldtype:"Owner" },
    { fieldname: 'modified_by', label: 'Modified By' , fieldtype: "Owner"},
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
    localStorage.setItem("page_state_folio_transaction", JSON.stringify(pageState.value))
    opShowColumn.value.toggle(event);
}


function onResetTable() {
    localStorage.removeItem("page_state_folio_transaction")
    localStorage.removeItem("table_folio_transaction_list_state")
    window.location.reload()
}
const getColumns = computed(() => {
    if (filter.value.search_field) {
        return columns.value.filter(r => (r.label || "").toLowerCase().includes(filter.value.search_field.toLowerCase())).sort((a, b) => a.label.localeCompare(b.label));
    } else {
        return columns.value.filter(r => r.label).sort((a, b) => a.label.localeCompare(b.label));
    }
})

function AddTransaction(account_code) {
    const dialogRef = dialog.open(ComAddFolioTransaction, {
        data: {
            new_doc: {
                transaction_type: "City Ledger",
                transaction_number: props.name,
                property: property.name,
                account_group: account_code.name
            },
            balance:cityLedgerAmountSummary.value?.balance || 0,
            account_code_filter:{
                is_city_ledger_account:1
            }
        },
        props: {
            header: 'Post ' + account_code.account_name + ' to City Ledger ' + props.name,
            style: {
                width: '50vw',
            },

            modal: true,
            position: "top",
            closeOnEscape: false
        },
        onClose: (options) => {
            const data = options.data;

            if (data) {
                loadData()
            }

        }
    })
}
function onEditFolioTransaction(name) {
    // if(disabled){
    //     gv.toast("warn","city ledger transaction can't edit")
    //     return
    // }
    const dialogRef = dialog.open(ComAddFolioTransaction, {
        data: {
            folio_transaction_number: name
        },
        props: {
            header: 'Edit City Ledger Transaction - ' + name,
            style: {
                width: '50vw',
            },
            modal: true,
            position: 'top',
            closeOnEscape: false
        },
        onClose: (options) => {
            const doc = options.data;
            if (doc) {
                loadData()
            }

        }
    })
}

function onDeleteCityLedgerTransaction(name) {
    const dialogRef = dialog.open(ComDialogNote, {
        data: {
                api_url: "utils.delete_doc",
                method: "DELETE",
                confirm_message: "Are you sure you want to delete this record?",
                data:{ doctype: "Folio Transaction", name: name },
            },
        props: {
            header: "Delete Transaction" + " " + name,
            style: {
                width: '50vw',
            },
            modal: true,
            maximizable: false,
            closeOnEscape: false,
            position: "top"
        },
        onClose: (options) => {
            if(options.data){
                loadData()
                window.socket.emit("CityLedgerAccount",window.property_name)
                window.socket.emit("ComCityLedgerDetail",window.property_name)
            }
            
            loading.value = false;
            
         }
    });
 
}

function onOpenLink(column, data) {
    window.postMessage(column.post_message_action + "|" + data[column.fieldname], '*')
}
function pageChange(page) {
    pageState.value.page = page.page
    pageState.value.rows = page.rows

    loadData()
}
function onDateSelect() {
    if (filter.value.date_range && filter.value.date_range[1]) {
        loadData()
    }
}
function onChecked() { 
    if(!filter.value.search_by_date){
        filter.value.date_range = null
    }
    if (!filter.value.search_by_date) {
        loadData()
    } else {
        onDateSelect()
    }
}

function loadData() {

   loading.value = true

    
    let filters = [
        ["property", "=", property.name],
        ["transaction_type", "=", "City Ledger"],
        ["transaction_number", "=", props.name],
    ]
    if (filter.value?.keyword) {
        filters.push(["keyword", 'like', '%' + filter.value.keyword + '%'])
    }
    if (filter.value.date_range && filter.value.search_by_date) {
        filters.push(['posting_date', 'between', [moment(filter.value.date_range[0]).format("YYYY-MM-DD"), moment(filter.value.date_range[1]).format("YYYY-MM-DD")]])
    }
    if (filter.value?.selected_reservation) {
        filters.push(["reservation", '=', filter.value.selected_reservation])
    }
    if (filter.value?.selected_reservation_stay) {
        filters.push(["reservation_stay", '=', filter.value.selected_reservation_stay])
    }
    if (filter.value?.selected_room) {
        filters.push(["room_id", '=', filter.value.selected_room])
    }
    if (filter.value?.selected_room_type) {
        filters.push(["room_type_id", '=', filter.value.selected_room_type])
    }
    if (filter.value?.selected_guest) {
        filters.push(["guest", '=', filter.value.selected_guest])
    }
    if (filter.value?.selected_account_code) {
        filters.push(["account_code", '=', filter.value.selected_account_code])
    }
    if (filter.value?.selected_account_category) {
        filters.push(["account_category", '=', filter.value.selected_account_category])
    }

    let fields = [...columns.value.map(r => r.fieldname), ...columns.value.map(r => r.extra_field)]
    fields = [...fields, ...selectedColumns.value]

    fields = [...new Set(fields.filter(x => x))]
    fields.push('reference_folio_transaction')
    getDocList('Folio Transaction', {

        fields: fields,
        orderBy: {
            field: '`tabFolio Transaction`.' + pageState.value.order_by,
            order: pageState.value.order_type,
        },
        filters: filters,
        limit_start: ((pageState.value?.page || 0) * (pageState.value?.rows || 20)),
        limit: pageState.value?.rows || 20,
    })
        .then((doc) => {
            data.value = doc
            loading.value = false
        })
        .catch((error) => {
            loading.value = false

        });
    getTotalRecord(filters)

    localStorage.setItem("page_state_folio_transaction", JSON.stringify(pageState.value))

    getApi("utils.get_city_ledger_amount_summary", {
        filters: {
            end_date: working_day.date_working_day,
            city_ledger: props.name
        }
    }).then((result) => {
        cityLedgerAmountSummary.value = result.message
    })

}
function getTotalRecord(filters) {

    getCount('Folio Transaction', filters)
        .then((count) => pageState.value.totalRecords = count || 0)

}
function onOrderBy(data) {
    pageState.value.order_by = data.order_by
    pageState.value.order_type = data.order_type
    pageState.value.page = 0
    loadData()

}

const Refresh = debouncer(() => {
    pageState.value.page = 0
    loadData()
}, 500);

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

    let state = localStorage.getItem("page_state_folio_transaction")
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
    
    getApi("frontdesk.get_meta", { doctype: "Folio Transaction" }).then((result) => {
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
        loadData()
    })
})

// Filter 
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