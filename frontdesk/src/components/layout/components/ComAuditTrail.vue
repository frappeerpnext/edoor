<template>
	<ComDialogContent   hideButtonClose titleButtonOK="Ok" :hideIcon="false" :hideButtonOK="true" :loading="loading">
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
							<div class="flex h-btn-cs justify-end items-end overflow-hidden rounded-lg mb-3">
			
			<button type="button" @click="onToggleView"
				:class="toggleView ? 'bg-blue-500 p-button h-full p-component text-white conten-btn border-right-none border border-noround-right' : 'p-button h-full p-component conten-btn border-noround-right'">
				<i :class="toggleView ? 'text-white' : ''" class="pi pi-align-justify me-2" />Line
			</button>
			<button @click="onToggleView"
				:class=" !(toggleView) ? 'bg-blue-500 p-button h-full p-component text-white conten-btn border-left-none border border-noround-left' : 'p-button h-full p-component conten-btn border-noround-left'">
				<i :class="!(toggleView) ? 'text-white' : ''" class="pi pi-table me-2" />Table
			</button>
		</div>
					</div>
				
					<div>
						<Dropdown class="h-btn-cs" v-model="pageState.order_by" :options="actions" optionValue="fieldname" optionLabel="label"
							placeholder="Sort By" @change="loadData" />
					</div>
					<div class="">
						<!-- <Button class="content_btn_b h-full px-3" @click="onOrderTypeClick">{{order.order_type}}</Button> -->
						<Button class="content_btn_b h-btn-cs px-3" @click="onOrderBy()">
							<i v-if="pageState.order_type == 'desc'" class="pi pi-sort-alpha-down-alt" /> 
        					<i v-if="pageState.order_type == 'asc'" class="pi pi-sort-alpha-down" />  
						</Button>
					</div>
					<div>
						<Button class="content_btn_b h-btn-cs" label="Print" icon="pi pi-print" @click="onPrint" :reservation="name" />
						<Button   @click="Refresh()" icon="pi pi-refresh" class="content_btn_b  ml-2"></Button>
					</div>
					
				</div>
			</div>
		</div>
		<div class="overflow-auto h-full pb-4">
			<ComPlaceholder text="No Data" MaxHeight="70vh" :loading="loading.value" :is-not-empty="data.length > 0">
				<DataTable 
					class="res_list_scroll" 
					:resizableColumns="true" 
					columnResizeMode="expand" 
					showGridlines
					stateStorage="local" 
					stateKey="table_audit_trail_list_state" 
					:reorderableColumns="true" 
					:value="data"
					v-if="!toggleView "
					tableStyle="min-width: 50rem" 
					@row-dblclick="onViewReservationStayDetail">
						<Column field="custom_posting_date" header="Audit date">
							<template #body="slotProps">
								{{ moment(slotProps.data.custom_posting_date).format("DD-MM-YYYY") }}
							</template>
						</Column>
						<Column field="reference_doctype" header="Reference Type"></Column>
						<Column field="reference_name" header="Reference Name">
							<template #body="slotProps">
								<Button class="p-0 link_line_action1" @click="onOpenLink(slotProps.data)" link>
									{{ slotProps.data.reference_name }}

								</Button>
							</template>

						</Column>
						<Column field="subject" header="Subject"></Column>
						<Column field="content" header="Description">
							<template #body="slotProps">
								<div class="white-space-nowrap overflow-hidden text-overflow-ellipsis content-note-comment" style="width:500px" v-html="slotProps.data.content" v-tippy="slotProps.data.content"></div>
							</template>
						</Column>
						<Column field="comment_by" header="By"></Column>
						<Column field="modified" header=" Date & Time"><template #body="slotProps">
								<ComTimeago :date="slotProps.data.modified" />

							</template>
						</Column>
				</DataTable>
			
				<ComActivityTimeLine v-else :data="data"/>
			</ComPlaceholder>
		</div>
		<hr>
		<div class="">
			<Paginator class="p__paginator " v-model:first="pageState.activePage" :rows="pageState.rows"
				:totalRecords="pageState.totalRecords" :rowsPerPageOptions="[20, 30, 40, 50, 100, 500]" @page="pageChange">
				<template #start="slotProps">
					<strong>Total Records: <span class="ttl-column_re">{{ pageState.totalRecords }}</span></strong>
				</template>
			</Paginator>
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
		<OverlayPanel ref="showAdvanceSearch" style="max-width:80rem">
			<ComOverlayPanelContent style="min-width:50rem" title="Advance Filter" @onSave="onClearFilter"
				titleButtonSave="Clear Filter" icon="pi pi-filter-slash" :hideButtonClose="false"
				@onCancel="onCloseAdvanceSearch">
				<div class="grid">
				
					<div class="col-6">
						<Calendar class="w-full" :selectOtherMonths="true" v-model="filter.custom_posting_date"
							placeholder="Please Select Date" dateFormat="dd-mm-yy"  @update:modelValue="loadData(false, $event)" showIcon />
					</div>
					<ComSelect class="col-6 " v-model="filter.type" :options="ref_data?.referenceTypes" v-if="ref_data?.referenceTypes.length>1" isMultipleSelect
						optionLabel="label" placeholder="Select Filter" :maxSelectedLabels="3"
						@onSelected="loadData(false, $event)" /> 
					<ComSelect v-model="filter.selected_comment_by" class="col-6" optionLabel="full_name" optionValue="name"
						placeholder="Please Select User" doctype="User" @onSelected="loadData(false, $event)" />
				</div>
			</ComOverlayPanelContent>
		</OverlayPanel>
	</ComDialogContent>
</template>
<script setup>
import { inject, ref, reactive, useToast, getCount, getDocList, onMounted, useDialog, getApi, computed, onUnmounted } from '@/plugin'
import Paginator from 'primevue/paginator';

import ComIFrameModal from "@/components/ComIFrameModal.vue";
import ComActivityTimeLine from "@/views/activities/components/ComActivityTimeLine.vue";


const showAdvanceSearch = ref()
const moment = inject("$moment")
const gv = inject("$gv")
const toast = useToast()
const opShowColumn = ref();
const loading = ref(false)
const dialogRef = inject("dialogRef");

const ref_data = ref()
const toggleView = ref(true)
function onToggleView(){
    toggleView.value  = !toggleView.value 
}
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

const data = ref([])
const filter = ref({})
let dateRange = reactive({
	start: '',
	end: ''
})

const pageState = ref({ order_by: "modified", order_type: "desc", page: 0, rows: 20, totalRecords: 0, activePage: 0 })
const dialog = useDialog();

function onOpenLink(data) {
	const action = ("view_" + data.reference_doctype.toLowerCase().replaceAll(" ", "_") + "_detail")

	window.postMessage(action + '|' + data.reference_name, '*')
}

const Refresh = debouncer(() => {
	loadData();
	pageState.value.page = 0
}, 500);

function pageChange(page) {
	pageState.value.page = page.page
	pageState.value.rows = page.rows
	loadData()
}
function loadData(show_loading = true) {

	loading.value = show_loading
	let filters = ([
		["custom_property", '=', window.property_name], ["custom_is_audit_trail", '=', 1],
		[ref_data.value.filter_key,"=", ref_data.value.docname]
	])
	if (filter.value?.keyword) {
		filters.push(["custom_keyword", 'like', '%' + filter.value.keyword + '%'])
	}

	if (filter.value.type && filter.value.type.length > 0) {
		filters.push(["reference_doctype", 'in', filter.value.type.map((r) => r.doctype)])
	} else {
		filters.push(["reference_doctype", 'in', ref_data.value.referenceTypes.map((r) => r.doctype)])
	}
 
	if (filter.value?.custom_posting_date) {
        const formattedDate = moment(filter.value.custom_posting_date, 'DD-MM-YYYY').format('YYYY-MM-DD');
        filters.push(['custom_posting_date', '=', formattedDate]);
    }

	if (filter.value?.selected_comment_by) { 
        filters.push(['comment_by', '=', filter.value.selected_comment_by]);
    }

	getDocList('Comment', {
		fields: ["custom_posting_date", "custom_icon" , "creation" , "reference_doctype", "reference_name", "subject", "content", "comment_by", "modified","comment_email"],
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
	if(pageState.value.order_type=='asc'){
		pageState.value.order_type='desc'
	}
	else{
		pageState.value.order_type='asc'
	}
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
	ref_data.value = dialogRef.value.data;
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

function onPrint() {
	dialog.open(ComIFrameModal, {
		data: {
			doctype: "Business Branch",
			name: window.property_name,
			report_name: gv.getCustomPrintFormat("Document Audit Trail"),
			show_letter_head:true,
			extra_params:[
				{key:'ref_doctype', value:ref_data.value.doctype},
				{key:'ref_docname', value:ref_data.value.docname},
				{key:'filter_key', value:ref_data.value.filter_key},
				{key:'order_by', value:pageState.value.order_by + ' ' + pageState.value.order_type},
			],
		},
		props: {
			header: "Audit Trail Detail for " + ref_data.value.doctype + " - " + ref_data.value.docname,
			style: {
				width: '80vw',
			},
			position: "top",
			modal: true,
			maximizable: true,
			breakpoints:{
                '960px': '80vw',
                '640px': '100vw'
            },
		},
	});
}



</script>