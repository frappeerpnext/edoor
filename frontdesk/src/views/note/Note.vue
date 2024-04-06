<template>
    <div class="flex-col flex" style="height: calc(100vh - 92px);">
        <div class="">
            <ComHeader isRefresh @onRefresh="Refresh()">
                <template #start>
                    <div class="flex justify-between">
                    <div class="text-2xl">{{$t('Note list')}} </div>
                    <Button v-if="isMobile" :label="$t('Add Note')" severity="warning" outlined icon="pi pi-plus" @click="onAddNote('')" />
                    </div>
                </template>
                <template #end>
                    <Button v-if="!isMobile" :label="$t('Add Note')" severity="warning" outlined icon="pi pi-plus" @click="onAddNote('')" />
                    <Button :label="btnLabel" severity="warning" outlined :icon="btnIcon" @click="onChangeViewType" />
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
                    <Button class="content_btn_b" :label="isMobile ? $t('Clear') : $t('Clear Filter') " icon="pi pi-filter-slash" @click="onClearFilter" />
                </div>
            </div>
                <div class="flex justify-end col">
                    <ComOrderBy doctype="Comment" @onOrderBy="onOrderBy" />
                </div>
            </div>
            
        </div> 
        <ComNoteTableView  :notes="notes" v-if="viewType=='table'" />
        <ComNoteCardView :notes="notes" @onViewDetail="onViewDetail" @onEdit="onEdit" @onPin="onPin" v-else/>
        <div>
            <Paginator v-model:first="pageState.activePage" :rows="pageState.rows" :totalRecords="pageState.totalRecords"
                :rowsPerPageOptions="[20, 30, 40, 50]" @page="pageChange">
                <template #start="slotProps">
                    <strong> {{ $t('Total Records') }} : <span class="ttl-column_re">{{ pageState.totalRecords }}</span></strong>
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
import ComNoteTableView from '@/views/note/ComNoteTableView.vue';
import ComNoteCardView from '@/views/note/ComNoteCardView.vue';
import {i18n} from '@/i18n';
const { t: $t } = i18n.global;

const confirm = useConfirm()
const notes = ref([]);
const dialog = useDialog()
const loading = ref(false);
const showAdvanceSearch = ref()
const gv = inject('$gv');
const moment = inject("$moment")
const isMobile = ref(window.isMobile) 
const filter = ref({})
const btnLabel = ref()
const btnIcon = ref()
const property = JSON.parse(localStorage.getItem("edoor_property"))

function onViewDetail(d){
    window.postMessage("view_" + d.reference_doctype.toLowerCase().replaceAll(" ","_") + "_detail|" + d.reference_name ,"*")
}

const viewType=ref(localStorage.getItem("note_view_type")) || "card"

const Refresh = debouncer(() => {
    onLoadData()
}, 500);
const advanceSearch = (event) => {
    showAdvanceSearch.value.toggle(event);
}

function onChangeViewType(){
    const view_type = localStorage.getItem("note_view_type") || "card"
    viewType.value = view_type=="card"?"table":"card"
    localStorage.setItem("note_view_type",viewType.value) 
    switchBtn()
}

const switchBtn = () => {
    if (viewType.value == "card"){
        btnLabel.value = "View as Table"
        btnIcon.value = "pi pi-table"
    }
    else{
        btnLabel.value = "View as Card"
        btnIcon.value = "pi pi-id-card"
    } 
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
    switchBtn()
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