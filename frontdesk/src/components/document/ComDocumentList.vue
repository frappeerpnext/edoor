<template>
    <template v-if="!options.hideHeader">
        <div class="flex w-full gap-2">
            <div v-if="!options.hideSaveView && doctype" class="flex align-items-center mb-2">
                <i v-if="!isMobile" @click="onShowSummary" class="pi pi-bars text-3xl cursor-pointer"></i>
            </div>
            <div class="w-full">
                <ComHeader isSetting isRefresh @onRefresh="loadData" :settingMenus="settingMenus">
                    <template #start>
                        <div :class="isMobile ? 'flex justify-content-between w-full' : ''">
                            
                            <div v-if="doctype" class="text-xl md:text-2xl"> {{ $t(title || doctype) }} {{ (currentView ? ' - ' +
                                currentView.filter_name : "") }} </div>
                            <div v-else class="text-xl md:text-2xl"> {{ $t(title) }}</div>

                        </div>
                    </template>
                    <template #end>

                        <slot name="action-button"></slot>
                    </template>

                </ComHeader>
            </div>
        </div>
    </template>
    <div class="grid gap-2">
        <template v-if="!options.hideSaveView && doctype">
            <div v-if="showSummary" class="col-2 pr-0 py-0 rounded-xl" style="width: 280px;">
                <div :class="wrapClass" class="w-full h-full p-3 rounded-xl border-1">
                    <h1 class="font-bold">Saved Filter</h1>  
                    <ComSaveViewList :doctype="doctype" :list_view_setting="list_view_setting" v-model:items="viewList" ref="saveViewList" /> 
                </div>
            </div>
        </template>
        <div class="col py-0 pl-0">
            <div :class="wrapClass" class="border-1 p-2 rounded-xl">
                <template v-if="!options.hideFilter">
                    <div class="flex justify-content-between mb-2">
                        <div>
                            <ComFilter :hideSearchField="options.hideSearchField" @onSearch="onFilter"
                                :filters="filterOptions" v-model:filter="tempFilter" />
                        </div>
                        <div v-if="doctype">
                            <ComOrderBy :doctype="doctype" @onOrderBy="onOrderBy" />
                        </div>
                    </div>
                </template>

                <slot name="top-summary"></slot>

                <div id="table-container">

                    <ContextMenu ref="cm" :model="contextMenuOptions" @before-show="onBeforeShow">
                        <template #item="{ item, props }">
                            <li v-if="item.is_header" style="border-radius: 10px 10px 0px 0px;margin-top: -5px;"
                                class="px-3 py-2 font-bold text-sm text-gray bg-blue-400 border-b">
                                <div class="flex justify-between items-center">

                                    <component :is="item.header_component" :data="selectedRow" />
                                </div>
                            </li>
                            <a v-else v-ripple class="flex items-center" v-bind="props.action">
                                <span :class="item.icon" />
                                <span class="ml-2">{{ item.label }}</span>

                                <Badge v-if="item.badge" class="ml-auto" :value="item.badge" />
                                <span v-if="item.shortcut"
                                    class="ml-auto border border-surface rounded bg-emphasis text-muted-color text-xs p-1">
                                    {{ item.shortcut }}
                                </span>
                                <i v-if="item.items" class="pi pi-angle-right ml-auto"></i>
                            </a>
                        </template>

                    </ContextMenu>
                    <DataTable v-if="scrollHeight" :value="items" scrollable :scrollHeight="scrollHeight"
                        :loading="loading" tableStyle="min-width: 50rem" @row-dblclick="onRowDoubleClick"
                        v-model:contextMenuSelection="selectedRow" :virtualScrollerOptions="{ itemSize: 46 }"
                        @rowContextmenu="onRowContextMenu" contextMenu
                        :showGridlines="showGridlines" 
                        
                        >
                        <template #empty> 
                            No Record Found
                        </template>
                        <template v-if="$slots.default">
                            <slot />
                        </template>
                        <template v-else>

                            <Column v-for="(col, index) of columns" :field="col.field" :key="col.field + '_' + index"
                     
                                :headerClass="col.custom_class? col.custom_class:col.header_class" 
                                :bodyClass="col.custom_class? col.custom_class:col.header_class">
                                <!-- Header slot for custom header content -->
                                <template #header="headerProps">
                                    <slot :name="'header_' + col.field" :column="col" :index="index">
                                        <span>{{ col.header }}</span>
                                    </slot>
                                </template>

                                <!-- Body slot for cell content -->
                                <template #body="slotProps">
                                    <slot :name="col.field" :item="slotProps.data" :index="col.field + '_' + index">
                                        <!-- date column -->
                                        <template v-if="col.fieldtype == 'Date'">
                                            {{ moment(slotProps.data[col.field]).format("DD-MM-YYYY") }}
                                        </template>
                                        <!-- currency column -->
                                        <template v-else-if="col.fieldtype == 'Currency'">

                                            <CurrencyFormat :value="slotProps.data[col.field]" />
                                        </template>
                                        <!-- owner and moified by we separete @ sign -->
                                        <template v-else-if="col.field == 'owner' || col.field == 'modified_by'">
                                            <span>{{ slotProps.data[col.field].split("@")[0] }}</span>
                                        </template>
                                        <!-- time ago field for creation and last modified -->
                                        <template v-else-if="col.fieldtype == 'Datetime'">
                                            <ComTimeago :date="slotProps.data[col.field]" />
                                        </template>
                                        <template v-else>
                                            <template v-if="col.action && slotProps.data[col.field]">
                                                <Button class="link_line_action1"
                                                    @click="onOpenLink(col.action, slotProps.data[col.id_field] || slotProps.data[col.field])"
                                                    link>
                                                    {{ slotProps.data[col.field] }}
                                                </Button>
                                            </template>
                                            <span v-else> {{ slotProps.data[col.field] }}</span>
                                        </template>
                                    </slot>
                                </template>
                            </Column>
                        </template>

                        <template v-if="hasAnyFooter">
                            <ColumnGroup type="footer">
                                <Row>
                                    <Column v-for="col in columns" :key="col.field" :footer="getFooter(col)" />
                                </Row>
                            </ColumnGroup>
                        </template>

                    </DataTable>
                </div>

                <Stack v-if="!options.hidePager && doctype">
                    <div class="flex justify-content-between align-items-center mt-3">
                        <div>
                            <SelectButton class="flex footer-limit-page border-1 border-round" v-model="limit"
                                :options="[20, 50, 100, 200, 300, 500]" aria-labelledby="basic"
                                @change="onLimitChanged" />
                        </div>
                        <div class="font-bold">
                            Showing: {{ items.length }} of {{ totalRecord }}
                        </div>
                    </div>
                </Stack>
            </div>
        </div>
    </div>

    <div>xxx</div>
</template>
<script setup>

import { useDocumentList } from "@/components/document/hooks/useDocumentList"
import ComFilter from "@/components/document/components/ComFilter.vue"
import ComOrderBy from '@/components/ComOrderBy.vue';
import ComSaveViewList from '@/components/document/components/ComSaveViewList.vue';
import { ref, inject, useDialog, computed, onMounted,watch } from "@/plugin";

import ContextMenu from 'primevue/contextmenu';



const dialog = useDialog()
const showSummary = ref(true)
const edoorReservationDetailSavedFilter = localStorage.getItem("edoor_reservation_detail_saved_filter")
const emit = defineEmits();
const props = defineProps({
    doctype: String,
    apiUrl:String,
    title: {
        type:String,
        default:""
    },
    router_name: String,
    list_view_setting: String,
    options: {
        type: Object,
        default: {
            limit: 50
        }
    },
    wrapClass:{
        type: String,
        default: "bg-white"
    },
    showGridlines:Boolean
})
const filter = defineModel("filter")
const moment = inject("$moment")
const selectedRow = defineModel("selectedRow")
const { items, scrollHeight, onSearch, loading, columns,
    filterOptions,
    onOrderBy,
    settingMenus,
    tempFilter,
    totalRecord,
    limit,
    viewList,
    onLimitChanged,
    currentView,
    saveViewList,
    onRowDoubleClick,
    loadData,
    onOpenLink,
    contextMenuOptions,
    addContextMenu
} = useDocumentList(props, emit, dialog)


defineExpose({
    loadData,
    addContextMenu
})

const cm = ref();
const onRowContextMenu = (event) => {
    cm.value.show(event.originalEvent);
};


function  onFilter(f){
    filter.value = f
    onSearch(f);
    emit("onFilter",f)
}

const hasAnyFooter = computed(() => {
    return Array.isArray(columns) ? columns.some(col => col.footer) : false
})

const getFooter = col => {
    if (typeof col.footer === 'function') {
        return col.footer(items.value)
    }
    return col.footer || ''
}

watch(
  () => props.options.columns,
  async (newCols, oldCols) => {
    if(JSON.stringify(newCols) !== JSON.stringify(oldCols)){
        columns.value = props.options.columns
    }
   
  },
  { deep: true }
);

 


function onShowSummary() {
    showSummary.value = !showSummary.value
    localStorage.setItem("edoor_reservation_detail_saved_filter", showSummary.value ? "1" : "0")
}

if (edoorReservationDetailSavedFilter) {
    showSummary.value = edoorReservationDetailSavedFilter == "1";
}

function onBeforeShow() {
    emit("onBeforeContextMenuShow")
}

</script>
<style>
.footer-limit-page .p-button.p-component.submit {
    padding: 10px !important;
    height: 30px !important;
    border: 0;
    border-radius: 0;
}

.p-contextmenu {
    width: 350px;
    background: #c7def2;
    border-radius: 10px;
}
</style>