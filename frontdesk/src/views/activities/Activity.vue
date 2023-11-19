<template>
    <div>
        <div class="px-2">
            <ComHeader isRefresh @onRefresh="onRefresh()">
                <template #start>
                    <div class="flex align-items-center">
                        <i @click="onShowSummary" class="pi pi-bars text-3xl cursor-pointer"></i>
                        <div class="text-2xl ml-4">Activity</div>
                    </div>
                </template>
            </ComHeader>

            <div>
                <div class="grid gap-2">
                    <div v-if="showSummary" class="col-2 p-0 rounded-xl" style="width:280px">
                        <ComHousekeepingStatistic />
                    </div>
                    <div class="col rounded-xl p-0">
                        <div>
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
                                    <div v-if="isFilter">
                                        <Button class="content_btn_b" label="Clear Filter" icon="pi pi-filter-slash"
                                            @click="onClearFilter" />
                                    </div>
                                </div>
                                <div class="flex gap-2">
                                    <div>
                                        <Dropdown v-model="pageState.order_by" :options="actions" optionValue="fieldname"
                                            optionLabel="label" placeholder="Sort By" @change="loadData" />
                                    </div>
                                    <div>
                                        <!-- <Button class="content_btn_b h-full px-3" @click="onOrderTypeClick">{{order.order_type}}</Button> -->
                                        <Button class="content_btn_b h-full px-3" @click="onOrderBy()">
                                            <i v-if="pageState.order_type == 'desc'" class="pi pi-sort-alpha-down-alt" />
                                            <i v-if="pageState.order_type == 'asc'" class="pi pi-sort-alpha-down" />
                                        </Button>
                                    </div>

                                </div>
                            </div>
                        </div>

                        <!-- Show aduti trail list -->
<div class="flex h-3rem justify-end items-end overflow-hidden rounded-lg mb-3">
                        <button type="button" @click="onToggleView"
                            :class="toggleView ? 'bg-blue-500 p-button h-full p-component text-white conten-btn border-right-none border border-noround-right' : 'p-button h-full p-component conten-btn border-noround-right'">
                            <i :class="toggleView ? 'text-white' : ''" class="pi pi-align-justify me-2" />Line
                        </button>
                        <button @click="onToggleView"
                            :class=" !(toggleView) ? 'bg-blue-500 p-button h-full p-component text-white conten-btn border-left-none border border-noround-left' : 'p-button h-full p-component conten-btn border-noround-left'">
                            <i :class="!(toggleView) ? 'text-white' : ''" class="pi pi-table me-2" />Table
                        </button>
                    </div>

                    <ComPlaceholder text="No Data" :loading="gv.loading" :is-not-empty="data && data.length > 0">
                        <ComActivityTimeLine :data="data" v-if="toggleView"/>
                        <ComActivityTable v-else :data="data" />
                    </ComPlaceholder>  
                      

                        <!-- pagger -->
                        <div class="mt-3">
                        <Paginator  v-model:first="pageState.activePage" :rows="pageState.rows"
                            :totalRecords="pageState.totalRecords" :rowsPerPageOptions="[ 50, 100, 500]"
                            @page="pageChange">
                            <template #start="slotProps">
                                <strong>Total Records: <span class="ttl-column_re">{{ pageState.totalRecords
                                }}</span></strong>
                            </template>
                        </Paginator>
                        </div>
                        <!-- end pager -->
                   

                    </div>
                </div>
            </div>
        </div>
    </div>

    <OverlayPanel ref="showAdvanceSearch" style="max-width:55rem">
        <ComOverlayPanelContent style="min-width:50rem" title="Advance Filter" @onSave="onClearFilter"
            titleButtonSave="Clear Filter" icon="pi pi-filter-slash" :hideButtonClose="false"
            @onCancel="onCloseAdvanceSearch">
            <div class="grid">
                <div class="col-6">
                    <label> Start Date </label>
                    <Calendar class="w-full" :showButtonBar="true" :selectOtherMonths="true" v-model="filter.start_date" placeholder="Start Date"
                        dateFormat="dd-mm-yy" @date-select="loadData(false, $event)" showIcon />
                </div>
                <div class="col-6">
                    <label> End Date </label>
                    <Calendar class="w-full" :selectOtherMonths="true" :minDate="filter.start_date" v-model="filter.end_date" placeholder="End Date"
                        dateFormat="dd-mm-yy" showIcon @date-select="loadData(false, $event)"  />
                </div>
                <ComSelect class="col-6 " v-model="filter.type" :options="reference_doctypes" isMultipleSelect
                    optionLabel="label" placeholder="Select Filter" :maxSelectedLabels="10"
                    @onSelected="loadData(false, $event)" />
                <ComSelect v-model="filter.selected_comment_by" class="col-6" optionLabel="full_name" optionValue="name"
                    placeholder="Please Select User" doctype="User" @onSelected="loadData(false, $event)" />
            </div>

        </ComOverlayPanelContent>
    </OverlayPanel>
</template>
<script setup>
import { ref, inject, onMounted, onUnmounted, getDocList, getCount ,computed} from "@/plugin"
import Paginator from 'primevue/paginator';
import ComHousekeepingStatistic from "@/views/housekeeping/components/ComHousekeepingStatistic.vue";
import ComActivityTimeLine from "@/views/activities/components/ComActivityTimeLine.vue";
import ComActivityTable from "@/views/activities/components/ComActivityTable.vue";
const edoor_activity_show_summary = localStorage.getItem("edoor_activity_show_summary")
const gv = inject("$gv")
const working_day = JSON.parse(localStorage.getItem("edoor_working_day"))
const filter = ref({ start_date: moment(working_day.date_working_day).add(-7,'days').toDate(), end_date: moment(working_day.date_working_day).toDate(), guest: "",keyword:"" })

const data = ref()
const showSummary = ref(true)
const toggleView = ref(true)//true view as timeline, false view as table

const pageState = ref({ order_by: "modified", order_type: "desc", page: 0, rows: 50, totalRecords: 0, activePage: 0 })
const showAdvanceSearch = ref()


const reference_doctypes = ref([
    { doctype: 'Reservation', label: 'Reservation' },
    { doctype: 'Reservation Stay', label: 'Reservation stay' },
    { doctype: 'Reservation Room Rate', label: 'Room Rate' },
    { doctype: 'Customer', label: 'Guest' },
    { doctype: 'Reservation Folio', label: 'Reservation Folio' },
    { doctype: 'Folio Transaction', label: 'Folio Transaction' },
    { doctype: 'Desk Folio', label: 'Desk Folio' },
    { doctype: 'Deposit Ledger', label: 'Deposit Ledger' },

])
const actions = ref([
    { label: 'Creation', fieldname: 'creation' },
    { label: 'Last Update On', fieldname: 'modified' },
    { label: 'Audit Date', fieldname: 'custom_posting_date' },
    { label: 'Reference Document', fieldname: 'reference_doctype' },
    { label: 'Reference Number', fieldname: 'reference_name' },
    { label: 'Subject', fieldname: 'subject' },
    { label: 'Description', fieldname: 'content' },
    { label: 'Created By', fieldname: 'comment_by' }
])

const advanceSearch = (event) => {
    showAdvanceSearch.value.toggle(event);
}


if (edoor_activity_show_summary) {
    showSummary.value = edoor_activity_show_summary == "1";
}

function onToggleView(){
    toggleView.value  = !toggleView.value 
}

function onShowSummary() {
    showSummary.value = !showSummary.value
    localStorage.setItem("edoor_activity_show_summary", showSummary.value ? "1" : "0")
}



function loadData(show_loading = true) {
    filter.start_date = moment(filter.value.start_date).format("YYYY-MM-DD")
    filter.end_date = moment(filter.value.end_date).format("YYYY-MM-DD")
    
    gv.loading = show_loading
    let filters = ([
        ["custom_property", '=', window.property_name], ["custom_is_audit_trail", '=', 1],
        ['custom_posting_date', 'between', [moment(filter.value.start_date).format("YYYY-MM-DD"), moment(filter.value.end_date).format("YYYY-MM-DD")]]
    ])
    if (filter.value?.keyword) {
        filters.push(["custom_keyword", 'like', '%' + filter.value.keyword + '%'])
    }

    if (filter.value.type && filter.value.type.length > 0) {
        filters.push(["reference_doctype", 'in', filter.value.type.map((r) => r.doctype)])
    } else {
        filters.push(["reference_doctype", 'in', reference_doctypes.value.map((r) => r.doctype)])
    }

    if (filter.value?.selected_comment_by) {
        filters.push(["comment_email", '=', filter.value.selected_comment_by])
      
    }
    if (filter.value?.start_date || filter.value?.end_date) {
        filters.push(['custom_posting_date', 'between', [moment(filter.value.start_date).format("YYYY-MM-DD"), moment(filter.value.end_date).format("YYYY-MM-DD")]])
    }

    getDocList('Comment', {
        fields: ["custom_posting_date", "creation" , "reference_doctype", "reference_name", "subject", "content", "comment_by", "modified", "comment_email","custom_icon","custom_comment_by_photo"],
        orderBy: {
            field: pageState.value.order_by,
            order: pageState.value.order_type,
        },
        filters: filters,
        limit_start: ((pageState.value?.page || 0) * (pageState.value?.rows || 50)),
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
}
function getTotalRecord(filters) {
    getCount('Comment', filters)
        .then((count) => pageState.value.totalRecords = count || 0)
}

function onOrderBy(data) {
    if (pageState.value.order_type == 'asc') {
        pageState.value.order_type = 'desc'
    }
    else {
        pageState.value.order_type = 'asc'
    }
    pageState.value.page = 0
    loadData()
}
const onClearFilter = () => {
	filter.value = { start_date: moment(working_day.date_working_day).add(-7,'days').toDate(), end_date: moment(working_day.date_working_day).toDate() }
	loadData()
	showAdvanceSearch.value.hide()
}
const onCloseAdvanceSearch = () => {
    showAdvanceSearch.value.hide()
}
function pageChange(page) {
	pageState.value.page = page.page
	pageState.value.rows = page.rows
	loadData()
}


const onSearch = debouncer(() => {
    loadData();
}, 500);


const onRefresh = debouncer(() => {

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
    loadData()
})




onUnmounted(() => {
    window.socket.off("Activity")
})
const isFilter = computed(() => {
    if (moment(working_day.date_working_day).add(-7,'days').format('yyyy-MM-DD') != moment(filter.value.start_date).format('yyyy-MM-DD') || moment(working_day.date_working_day).format('yyyy-MM-DD') != moment(filter.value.end_date).format('yyyy-MM-DD')) {
        return true
    }
    else {
        return gv.isNotEmpty(filter.value, 'start_date,end_date')
    }
})

</script>