<template>
    <div class="flex-col flex" style="height: calc(100vh - 92px);">
        <div class="">
            <ComHeader isRefresh @onRefresh="Refresh()">
                <template #start>
                    <div class="flex justify-between">
                    <div class="text-2xl">Note list</div>
                    <Button v-if="isMobile" label="Add Note" severity="warning" outlined icon="pi pi-plus" @click="onAddNote('')" />
                    </div>
                </template>
                <template #end>
                    <Button v-if="!isMobile" label="Add Note" severity="warning" outlined icon="pi pi-plus" @click="onAddNote('')" />
                </template>
            </ComHeader>
           
            <div class="mb-3 flex justify-between">
                <div v-if="!isMobile" class="flex gap-2">
                    <div class="col-6 p-0">
                        <div class="p-input-icon-left w-full">
                            <i class="pi pi-search" />
                            <InputText v-model="filter.keyword" class="w-full" placeholder="Search" @input="onSearch" />
                        </div>
                    </div>
                    <div class="col-6 p-0">
                        <div class="flex relative ">
                            <Calendar :selectOtherMonths="true" class="w-full" inputClass="pl-6" hideOnRangeSelection dateFormat="dd-mm-yy"
                                v-model="filter.date_range" selectionMode="range" :manualInput="false" @date-select="onDateSelect"
                                placeholder="Select Date Range" :disabled="!filter.search_by_date" showIcon />
                            <div class="check-box-filter">
                                <Checkbox v-model="filter.search_by_date" :binary="true" @change="onChecked" />
                            </div>
                        </div>
                    </div>
                </div>
                <div v-else class="flex gap-2 col">
                <Button icon="pi pi-sliders-h" class="content_btn_b" @click="advanceSearch" />
                <div v-if="gv.isNotEmpty(filter, 'search_date_type')">
                    <Button class="content_btn_b" :label="isMobile ? 'Clear' : 'Clear Filter' " icon="pi pi-filter-slash" @click="onClearFilter" />
                </div>
            </div>
                <div class="flex justify-end col">
                    <ComOrderBy doctype="Comment" @onOrderBy="onOrderBy" />
                </div>
            </div>
            
        </div>
        <div class="overflow-auto h-full mb-3">
            <ComPlaceholder text="No Data" :loading="loading" :is-not-empty="notes.length > 0">
                <div class="grid-cs-note">
                    <div v-for="(i, index) in notes" :key="index" :style="{ order: index }"
                         class="item-cs-note border-1 rounded-lg bg-white py-3 px-5 shadow-md note-content-box relative">
                        <div class="flex flex-col">
                            <div class="line-height-1 w-full flex justify-between ">
                                <div class="my-auto">
                                    <div v-if="i.reference_doctype">
						<span class="text-lg" >
							{{ i.reference_doctype }}
						</span>
						-
						<div @click="onViewDetail(i)" class="text-lg inline link_line_action  border-none p-0 w-auto" >
							 {{ i.reference_name }}
						</div>
						</div>
                        <div v-else>
							<span class="text-lg" >
								General Note
						</span>
                        </div>
                        
                                </div>
                                <div class="flex absolute right-3 gap-2">
                                    <Button :class="i.custom_is_pin ? '' : 'hidden'" class="w-2rem h-2rem px-1 pb-1 pt-0 btn-in-note "
                                        text rounded @click="onPin(i)">
                                        <ComIcon v-tippy ="'Unpin Note'" v-if="i.is_pin" icon="pushPined"
                                            style="height:20px;"></ComIcon>
                                        <ComIcon v-tippy ="'Pin Note'" v-else icon="pushPin" style="height:20px;">
                                        </ComIcon>
                                    </Button>
                                </div>
                            </div>
                            <div class="text-500 text-sm"> 
                                Note Date: {{ gv.dateFormat(i.custom_note_date) }} </div>
                        </div>
                        {{ i.room}}
                        {{ i.guest_name }}
                        <div v-if="i.content"
                            class="mt-3 mb-6 whitespace-pre-wrap break-words overflow-auto pb-5 line-height-2">
                            {{ i.content }}
                        </div>

                        <div class="flex flex-col font-italic  line-height-2 absolute bottom-2 modifiad-note-cs"
                            style="font-size: 10px;">
                            <div>
                                Noted by <span class=" text-500 "> {{ i.comment_by }} - <ComTimeago :date="i.creation"></ComTimeago></span>
                            </div>
                            <div v-if="i.modified">
                                Last Modified by : <span class=" text-500 ">{{ i.modified_by.split("@")[0] }} -
                                    <ComTimeago :date="i.modified" /></span>
                            </div>
                            <div class="absolute right-2">
                                <div class="flex">
                                    <Button class="w-2rem h-2rem flex justify-center items-center " text rounded outlined
                                        label="Edit" @click="onEdit(i.name)">
                                        <i class="pi pi-pencil text-blue-500"></i>
                                    </Button>
                                    <Button class="w-2rem h-2rem flex justify-center items-center " @click="onDelete(i.name)"
                                        text rounded outlined aria-label="Delete">
                                        <i class="pi pi-trash text-red-500"></i>
                                    </Button>
                                </div>
                            </div>
                        </div>

                        <div>
                        </div>
                    </div>
                </div>
            </ComPlaceholder>
        </div>
        <div>
            <Paginator v-model:first="pageState.activePage" :rows="pageState.rows" :totalRecords="pageState.totalRecords"
                :rowsPerPageOptions="[20, 30, 40, 50]" @page="pageChange">
                <template #start="slotProps">
                    <strong>Total Records: <span class="ttl-column_re">{{ pageState.totalRecords }}</span></strong>
                </template>
            
            </Paginator>
        </div>
    </div>
    <OverlayPanel ref="showAdvanceSearch" style="max-width:50rem">
        <ComOverlayPanelContent title="Advance Filter" @onSave="onClearFilter" titleButtonSave="Clear Filter"
            icon="pi pi-filter-slash" :hideButtonClose="false" @onCancel="onCloseAdvanceSearch">
            <div class="grid mt-3">
                <div class="col-12">
                        <div class="p-input-icon-left w-full">
                            <i class="pi pi-search" />
                            <InputText v-model="filter.keyword" class="w-full" placeholder="Search" @input="onSearch" />
                        </div>
                    </div>
                    <div class="col-12">
                        <div class="flex relative ">
                            <Calendar :selectOtherMonths="true" class="w-full" inputClass="pl-6" hideOnRangeSelection dateFormat="dd-mm-yy"
                                v-model="filter.date_range" selectionMode="range" :manualInput="false" @date-select="onDateSelect"
                                placeholder="Select Date Range" :disabled="!filter.search_by_date" showIcon />
                            <div class="check-box-filter">
                                <Checkbox v-model="filter.search_by_date" :binary="true" @change="onChecked" />
                            </div>
                        </div>
                    </div>
                </div>
        </ComOverlayPanelContent>
    </OverlayPanel>
</template>
<script setup>
import { ref, inject, onMounted, updateDoc, useDialog, getDocList, getCount, useConfirm, deleteDoc } from '@/plugin';

import ComAddNote from './ComAddNote.vue';
import Paginator from 'primevue/paginator';
import ComOrderBy from '@/components/ComOrderBy.vue';
import ComFolioTransactionDetail from '@/views/reservation/components/reservation_stay_folio/ComFolioTransactionDetail.vue';

const confirm = useConfirm()
const notes = ref([]);
const dialog = useDialog()
const loading = ref(false);
const showAdvanceSearch = ref()
const gv = inject('$gv');
const moment = inject("$moment")
const isMobile = ref(window.isMobile) 
const filter = ref({})
const property = JSON.parse(localStorage.getItem("edoor_property"))

function onViewDetail(d){
    window.postMessage("view_" + d.reference_doctype.toLowerCase().replaceAll(" ","_") + "_detail|" + d.reference_name ,"*")
}

const Refresh = debouncer(() => {
    onLoadData()
}, 500);
const advanceSearch = (event) => {
    showAdvanceSearch.value.toggle(event);
}
const onClearFilter = () => {
    filter.value = {}
    onLoadData()
    showAdvanceSearch.value.hide()
}
const onCloseAdvanceSearch = () => {
    showAdvanceSearch.value.hide()
}
function onEdit(name) {
    const dialogRef = dialog.open(ComAddNote, {
        data: {
            name: name
        },
        props: {
            header: (name ? "Edit" : 'Add') + " Note",
            style: {
                width: '60vw',
            },
            modal: true,
            maximizable: true,
            closeOnEscape: false,
            position: 'top',
            breakpoints:{
                '960px': '60vw',
                '640px': '100vw'
            },
        },
        onClose: (options) => {
            const data = options.data;
            if (data) {
                onLoadData()
                // // update bage total notes
                getTotalNote()
            }
        }
    });
}

const pageState = ref({ order_by: "modified", order_type: "desc", page: 0, rows: 20, totalRecords: 0, activePage: 0 })

function onPin(i) {
    i.custom_is_pin = !i.custom_is_pin
    updateDoc('Comment', i.name, i).then((r) => {
        onLoadData()
    })
}

function onDateSelect() {
    if (filter.value.date_range && filter.value.date_range[1]) {
        onLoadData()
    }
}
function onChecked() {
    if (!filter.value.search_by_date) {
        filter.value.date_range = null
        onLoadData()
    } else {
        onDateSelect()
    }
}

function pageChange(page) {
    pageState.value.page = page.page
    pageState.value.rows = page.rows
    onLoadData()
}

function onLoadData() {

    loading.value = true
    gv.loading = true
   	let filters = [
		["custom_property", "=", window.property_name],
		["custom_is_audit_trail", "=",1],
		["custom_is_note", "=",1],
		["comment_type","=","Comment"]
	]
	filters.push(["custom_note_date",">=", working_day.date_working_day])

    if (filter.value.keyword) {
        filters.push(["custom_keyword", "like", '%' + filter.value.keyword + '%'])
    }

    if (filter.value.date_range && filter.value.search_by_date) {
        filters.push(['custom_note_date', 'between', [moment(filter.value.date_range[0]).format("YYYY-MM-DD"), moment(filter.value.date_range[1]).format("YYYY-MM-DD")]])
    }


    getDocList('Comment', {
        fields:  ["name","creation",  "custom_keyword", "custom_is_pin", "modified_by" , "custom_note_date", "custom_posting_date", "reference_doctype", "reference_name", "content", "owner","comment_by", "modified","comment_type","custom_icon",'custom_is_note'],
        filters: filters,
        orderBy: {
            field: pageState.value.order_by,
            order: pageState.value.order_type,
        },
        limit_start: ((pageState.value?.page || 0) * (pageState.value?.rows || 20)),
        limit: pageState.value?.rows || 20,



    }).then((docs) => {
        notes.value = docs;
        loading.value = false
        gv.loading = false
    }).catch(() => {
        gv.loading = false
        loading.value = false
    })
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
    onLoadData()

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

function onDelete(name) {
    confirm.require({
        message: 'Are you sure you want to delete reservation note?',
        header: 'Confirmation',
        icon: 'pi pi-exclamation-triangle',
        acceptClass: 'border-none crfm-dialog',
        rejectClass: 'hidden',
        acceptIcon: 'pi pi-check-circle',
        acceptLabel: 'Ok',
        accept: () => {
            loading.value = true
            deleteDoc('Comment', name)
                .then(() => {
                    onLoadData()

                }).catch((err) => {
                    loading.value = false
                })
        },
    });
}


const onSearch = debouncer(() => {
    onLoadData()
}, 500);

onMounted(() => {
    if(window.isMobile){
        let elem = document.querySelectorAll(".p-dialog");
        if (elem){
            elem = elem[elem.length-1]
            elem?.classList.add("p-dialog-maximized"); // adds the maximized class
        }
    }
    onLoadData()
})

function onAddNote(name) {
    const dialogRef = dialog.open(ComAddNote, {
        data: {
            name: name
        },
        props: {
            header: (name ? "Edit" : 'Add') + " Note",
            style: {
                width: '60vw',
            }, 
            modal: true,
            maximizable: true,
            closeOnEscape: false,
            position: 'top',
            breakpoints:{
                '960px': '60vw',
                '640px': '100vw'
            },
        },
        onClose: (options) => {
            const data = options.data;
            if (data) {
                onLoadData()
                dialogRef.value.close()
                // update bage total notes
                getTotalNote()
            }
        }
    });

}

const items = ref([]);
let grid = null;
let rowHeight = 0;
let rowGap = 0;

function resizeGridItem(item) {
    rowHeight = parseInt(window.getComputedStyle(grid).getPropertyValue('grid-auto-rows'));
    rowGap = parseInt(window.getComputedStyle(grid).getPropertyValue('grid-row-gap'));
    const contentHeight = item.querySelector('.content').getBoundingClientRect().height;
    const rowSpan = Math.ceil((contentHeight + rowGap) / (rowHeight + rowGap));
    item.style.gridRowEnd = `span ${rowSpan}`;
}

function resizeAllGridItems() {
    items.value.forEach((item) => resizeGridItem(item));
}


</script>