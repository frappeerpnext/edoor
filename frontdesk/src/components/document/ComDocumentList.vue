<template>
    <div class="flex w-full gap-2">
        <div class="flex align-items-center mb-2">
            <i v-if="!isMobile" @click="onShowSummary" class="pi pi-bars text-3xl cursor-pointer"></i>
        </div>
    
        <div class="w-full">
         
            <ComHeader isSetting isRefresh @onRefresh="getData"
                :settingMenus="settingMenus"
            >
                <template #start>
                    <div :class="isMobile ? 'flex justify-content-between w-full' : ''">
                        <div class="text-xl md:text-2xl"> {{ $t(title || doctype) }} {{ (currentView?' - '+ currentView.filter_name :"") }} </div>
                        
                    </div>
                </template>
                <template #end>

                    <slot name="action-button"></slot>
                </template>
                
            </ComHeader>
        </div>
    </div>

<div class="grid gap-2">
    <div v-if="showSummary" class="col-2 p-0 rounded-xl" style="width: 280px;">
        <div class="bg-white w-full h-full p-3 rounded-xl">
            <h1 class="font-bold">Saved Filter</h1>
            <ComSaveViewList :doctype="doctype" v-model:items="viewList" ref="saveViewList"/>
        
        </div>
    </div>
    <div class="col p-0">
        <div class="bg-white p-2 rounded-xl">
            <div class="flex justify-content-between mb-2">
                <div>
                  
                    <ComFilter v-if="!options.hideFilter" :hideSearchField="options.hideSearchField" @onSearch="onSearch" :filters="filterOptions"  v-model:filter="tempFilter" />
                </div>
                <div>
                    <ComOrderBy :doctype="doctype" @onOrderBy="onOrderBy" />
                </div>
            </div>
                <div id="table-container">
                     
                    <ContextMenu ref="cm" :model="options.contextMenuOptions"  />
                    <DataTable v-if="scrollHeight" :value="items" scrollable :scrollHeight="scrollHeight" :loading="loading"
                        tableStyle="min-width: 50rem" 
                        @row-dblclick="onRowDoubleClick"
                         v-model:contextMenuSelection="selec"
                        :virtualScrollerOptions="{ itemSize: 46 }"
                          @rowContextmenu="onRowContextMenu"
                        contextMenu 
                        >


                        <Column v-for="(col, index) of columns" :field="col.field" :key="col.field + '_' + index"
                            :headerClass="col.header_class" :bodyClass="col.header_class"
                        >
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
                                    <template v-if="col.fieldtype=='Date'">
                                        {{moment(slotProps.data[col.field]).format("DD-MM-YYYY") }}
                                    </template>
                                    <!-- currency column -->
                                    <template v-else-if="col.fieldtype == 'Currency'">
                                    
                                        <CurrencyFormat  :value="slotProps.data[col.field]" />
                                    </template>
                                    <!-- owner and moified by we separete @ sign -->
                                    <template v-else-if="col.field == 'owner' || col.field == 'modified_by'">
                                            <span>{{ slotProps.data[col.field].split("@")[0] }}</span>
                                    </template>
                                    
                                    <!-- time ago field for creation and last modified -->
                                    <template v-else-if="col.fieldtype =='Datetime'">
                            
                                    
                                        <ComTimeago :date="slotProps.data[col.field]" />
                                    </template>



                                    <span v-else> {{ slotProps.data[col.field] }}</span>

                                </slot>
                            </template>


                        </Column>

                    </DataTable>
                </div>
                <Stack>
                    <div class="flex justify-content-between align-items-center mt-3">
                        <div>
                            <SelectButton class="flex footer-limit-page border-1 border-round" v-model="limit" :options="[20,50,100,200,300,500]"
                                aria-labelledby="basic" @change="onLimitChanged" />
                        </div>
                        <div class="font-bold">
                            Showing: {{items.length}} of {{ totalRecord }}
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
import { ref,inject,useDialog } from "@/plugin";

import ContextMenu from 'primevue/contextmenu';



const dialog = useDialog()
const showSummary = ref(true)
const edoorReservationDetailSavedFilter = localStorage.getItem("edoor_reservation_detail_saved_filter")
const emit = defineEmits();
const props = defineProps({
    doctype: String,
    router_name:String,
    list_view_setting:String,
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
    getData
} = useDocumentList(props,emit,dialog)
const cm = ref();

const onRowContextMenu = (event) => {
    
        cm.value.show(event.originalEvent);
  
   
};


function onShowSummary() {
    showSummary.value = !showSummary.value
    localStorage.setItem("edoor_reservation_detail_saved_filter", showSummary.value ? "1" : "0")
}

if (edoorReservationDetailSavedFilter) {
    showSummary.value = edoorReservationDetailSavedFilter == "1";
}


</script>
<style >
    .footer-limit-page .p-button.p-component.submit{
        padding:10px !important;
        height: 30px !important;
        border:0;
        border-radius:0;
    }
</style>