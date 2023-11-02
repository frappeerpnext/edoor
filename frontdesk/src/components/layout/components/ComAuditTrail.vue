<template>
	<div class="flex-col flex" style="height: calc(100vh - 92px);">
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
					<div v-if="gv.isNotEmpty(filter, 'search_date_type')">
						<Button class="content_btn_b" label="Clear Filter" icon="pi pi-filter-slash" @click="onClearFilter" />
					</div>
				</div>
				<div class="flex gap-2">
					<div>
						<Dropdown v-model="order.order_by" :options="actions" optionValue="fieldname" optionLabel="label"
							placeholder="Sort By" @change="loadData" />
					</div>
					<div>
						<!-- <Button class="content_btn_b h-full px-3" @click="onOrderTypeClick">{{order.order_type}}</Button> -->
						<Button class="content_btn_b h-full px-3" @click="onOrderTypeClick">
							<i v-if="order.order_type == 'desc'" class="pi pi-sort-alpha-down" />
							<i v-if="order.order_type == 'asc'" class="pi pi-sort-alpha-up" />
						</Button>
					</div>
					<SplitButton class="border-split-none" label="Print" icon="pi pi-print" :model="items" />
				</div>
			</div>
		</div>
		<div class="overflow-auto h-full">
			<ComPlaceholder text="No Data" height="70vh" :loading="loading.value" :is-not-empty="data.length > 0">
				<DataTable class="res_list_scroll" :resizableColumns="true" columnResizeMode="fit" showGridlines
					stateStorage="local" stateKey="table_audit_trail_list_state" :reorderableColumns="true" :value="data"
					tableStyle="min-width: 50rem" @row-dblclick="onViewReservationStayDetail">
					<Column field="custom_posting_date" header="Audit date">
						<template #body="slotProps">
							{{ moment(slotProps.data.custom_posting_date).format("DD-MM-YYYY") }}
						</template>
					</Column>
					<Column field="reference_doctype" header="Reference Type"></Column>
					<Column field="reference_name" header="Reference Name"></Column>
					<Column field="subject" header="Subject"></Column>
					<Column field="content" header="Description">
						<template #body="slotProps">
							<div v-html="slotProps.data.content"></div>
						</template>
					</Column>
					<Column field="comment_by" header="By"></Column>
					<Column field="modified" header=" Date & Time"><template #body="slotProps">
							<Timeago :datetime="slotProps.data.modified" long></Timeago>
						</template>
					</Column>
				</DataTable>
			</ComPlaceholder>
		</div>
		<div>
			<Paginator class="p__paginator" v-model:first="pageState.activePage" :rows="pageState.rows"
				:totalRecords="pageState.totalRecords" :rowsPerPageOptions="[20, 30, 40, 50, 100,500]" @page="pageChange">
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
				<div>
					<span>
						<div class="card flex justify-content-center"> 
							<ComSelect v-model="filter.type" :options="referenceType" isMultipleSelect optionLabel="label"
								placeholder="Select Filter" :maxSelectedLabels="3" @onSelected="loadData(false, $event)"/>
						</div>
					</span>
				</div>
			</div>
		</ComOverlayPanelContent>
	</OverlayPanel>
</template>
<script setup>
import { inject, ref, reactive, useToast, getCount, getDocList, onMounted, getApi, computed, onUnmounted } from '@/plugin'

import { useDialog } from 'primevue/usedialog';
import Paginator from 'primevue/paginator';
import ComOrderBy from '@/components/ComOrderBy.vue';
import { Timeago } from 'vue2-timeago'


const showAdvanceSearch = ref()
const moment = inject("$moment")
const gv = inject("$gv")
const toast = useToast()
const opShowColumn = ref();
const loading = ref(false)
const selectedReferenceType = ref();
const referenceType = ref([
	{ fieldname: 'Reservation', label: 'Reservation' },
	{ fieldname: 'Reservation Stay', label: 'Reservation stay' },
	{ fieldname: 'guest', label: 'Guest' },
	{ fieldname: 'Reservation Folio', label: 'Reservation Folio' },
	{ fieldname: 'Folio Transaction', label: 'Folio Transaction' },
	{ fieldname: 'owner', label: 'Create By' },
	{ fieldname: 'custom_posting_date', label: 'Audit Date' }

]);

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
const order = ref({ order_by: "modified", order_type: "desc" })
const toggleShowColumn = (event) => {
	opShowColumn.value.toggle(event);
}
const data = ref([])

const filter = ref({})
let dateRange = reactive({
	start: '',
	end: ''
})

const pageState = ref({ order_by: "modified", order_type: "desc", page: 0, rows: 20, totalRecords: 0, activePage: 0 })
const dialog = useDialog();

function onOpenLink(column, data) {
	window.postMessage(column.post_message_action + "|" + data[column.fieldname], '*')
}

function Refresh() {
	pageState.value.page = 0
	loadData()
}


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
	loading.value = show_loading
	let filters = ([
		["custom_property", '=', window.property_name], ["custom_is_audit_trail", '=', 1]
	])
	if (filter.value?.keyword) {
		filters.push(["keyword", 'like', '%' + filter.value.keyword + '%'])
	}
	if (filter.value.type && filter.value.type.length > 0) {
    	filters.push(["reference_doctype", 'in', filter.value.type.map((r)=>r.label)])
  	} 
	getDocList('Comment', {
		fields: ["custom_posting_date", "reference_doctype", "reference_name", "subject", "content", "comment_by", "modified"],
		orderBy: {
			field: pageState.value.order_by,
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
			toast.add({ severity: 'error', summary: 'Error Message', detail: error, life: 3000 });
		});
	getTotalRecord(filters)
}
function getTotalRecord(filters) {
	getCount('Comment', filters)
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

</script>