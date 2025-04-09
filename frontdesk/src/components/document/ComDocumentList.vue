<template>
    <template v-if="!options.hideHeader">
    <div class="flex w-full gap-2">

        <div v-if="!options.hideSaveView" class="flex align-items-center mb-2">
          
            <i v-if="!isMobile" @click="onShowSummary" class="pi pi-bars text-3xl cursor-pointer"></i>
        </div>

        <div class="w-full">

            <ComHeader isSetting isRefresh @onRefresh="getData" :settingMenus="settingMenus">
                <template #start>
                    <div :class="isMobile ? 'flex justify-content-between w-full' : ''">
                        <div class="text-xl md:text-2xl"> {{ $t(title || doctype) }} {{ (currentView ? ' - ' +
                            currentView.filter_name :"") }} </div>

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
        <template v-if="!options.hidesavefilter">
        <div v-if="showSummary" class="col-2 pr-0 py-0 rounded-xl" style="width: 280px;">
            <div class="bg-white w-full h-full p-3 rounded-xl">
                <h1 class="font-bold">Saved Filter</h1>
                <ComSaveViewList :doctype="doctype" v-model:items="viewList" ref="saveViewList" />

            </div>
        </div>
        </template>
        <div class="col py-0">
            <div class="bg-white p-2 rounded-xl">
                <template v-if="!options.hideFilter">
                <div class="flex justify-content-between mb-2">
                    <div>
                        <ComFilter   :hideSearchField="options.hideSearchField"
                            @onSearch="onSearch" :filters="filterOptions" v-model:filter="tempFilter" />
                    </div>
                    <div>
                     
                        <ComOrderBy :doctype="doctype" @onOrderBy="onOrderBy" />
                    </div>
                </div>
            </template>
                
                <slot name="top-summary"></slot>

                <div id="table-container">

                    <ContextMenu ref="cm" :model="options.contextMenuOptions" />
                    <DataTable v-if="scrollHeight" :value="items" scrollable :scrollHeight="scrollHeight"
                        :loading="loading" tableStyle="min-width: 50rem" @row-dblclick="onRowDoubleClick"
                        v-model:contextMenuSelection="selec" :virtualScrollerOptions="{ itemSize: 46 }"
                        @rowContextmenu="onRowContextMenu" contextMenu>
                        <template v-if="$slots.default">
                            <slot />
                        </template>
                        <template v-else>

                            <Column v-for="(col, index) of columns" :field="col.field" :key="col.field + '_' + index"
                                :headerClass="col.header_class" :bodyClass="col.header_class">
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
                                                <Button class="link_line_action1" @click="onOpenLink(col.action, slotProps.data[col.id_field] || slotProps.data[col.field])" link>
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
          <Column
            v-for="col in columns"
            :key="col.field"
            :footer="getFooter(col)"
          />
        </Row>
      </ColumnGroup>
    </template>

                    </DataTable>
                </div>
                
                <Stack v-if="!options.hidePager">
                    <div class="flex justify-content-between align-items-center mt-3">
                        <div>
                            <SelectButton class="flex footer-limit-page border-1 border-round" v-model="limit"
                                :options="[20, 50, 100, 200, 300, 500]" aria-labelledby="basic" @change="onLimitChanged" />
                        </div>
                        <div class="font-bold">
                            Showing: {{ items.length }} of {{ totalRecord }}
                        </div>
                    </div>
                </Stack>
            </div>
        </div>
    </div>
</template>
<script setup>

import { useDocumentList } from "@/components/document/hooks/useDocumentList"
import ComFilter from "@/components/document/components/ComFilter.vue"
import ComOrderBy from '@/components/ComOrderBy.vue';
import ComSaveViewList from '@/components/document/components/ComSaveViewList.vue';
import { ref, inject, useDialog, computed } from "@/plugin";

import ContextMenu from 'primevue/contextmenu';



const dialog = useDialog()
const showSummary = ref(true)
const edoorReservationDetailSavedFilter = localStorage.getItem("edoor_reservation_detail_saved_filter")
const emit = defineEmits();
const props = defineProps({
    doctype: String,
    title: String,
    router_name: String,
    list_view_setting: String,
    options: {
        type: Object,
        default: {
            limit: 50
        }
    }
})

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
    getData,
    onOpenLink
} = useDocumentList(props, emit, dialog)

defineExpose({
    getData
})
 

const cm = ref();
const onRowContextMenu = (event) => {
    cm.value.show(event.originalEvent);
};

const hasAnyFooter = computed(() => {
    return Array.isArray(columns) ? columns.some(col => col.footer) : false
})

const getFooter = col => {
  if (typeof col.footer === 'function') {
    return col.footer(items.value)
  }
  return col.footer || ''
}



function onShowSummary() {
    showSummary.value = !showSummary.value
    localStorage.setItem("edoor_reservation_detail_saved_filter", showSummary.value ? "1" : "0")
}

if (edoorReservationDetailSavedFilter) {
    showSummary.value = edoorReservationDetailSavedFilter == "1";
}


</script>
<style>
.footer-limit-page .p-button.p-component.submit {
    padding: 10px !important;
    height: 30px !important;
    border: 0;
    border-radius: 0;
}
</style>