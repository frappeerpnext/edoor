<template>
    <div class="flex-col flex view_sroll_mobile_table" style="height: calc(100vh - 92px);">
        <div>
            <ComHeader colClass="col-6" isRefresh @onRefresh="Refresh()">
                <template #start>
                    <div class="text-2xl"> {{ $t('City Ledger') }} </div>
                </template>
                <template #end>
                    <!-- <SplitButton class="spl__btn_cs sp" @click="onPrint" label="Print" icon="pi pi-print" />  -->
                </template>
            </ComHeader>
            
            <div>
                <ComSummaryofBalance :summary="summary" :start_date="filter.start_date" :end_date="filter.end_date" />
            </div>
        </div>
        <div class="grid">
<div class="col-12 lg:col-9">
    <ComTopDebtorCompany ref="refresh_top_debtor_company" />
</div>
<div class="col-12 lg:col-3 ">
    <ComAgingBalance  ref="refresh_aging_balance"/>
</div>
        </div>
      
    </div>

    <OverlayPanel ref="opShowColumn" style="width:30rem;">
        <ComOverlayPanelContent title="Show / Hide Columns" @onSave="OnSaveColumn" ttl_header="mb-2" titleButtonSave="Save"
            @onCancel="onCloseColumn">
            <template #top>
                <div class="p-input-icon-left mb-3 w-full">
                    <i class="pi pi-search" />
                    <InputText v-model="filter.search_field" :placeholder=" $t('Search') " class="w-full" />
                </div>
            </template>
            <div class="grid">
                <div class="col-6 py-1" v-for="(c, index) in getColumns.filter(r => r.label)" :key="index">
                    <Checkbox v-model="c.selected" :binary="true" :inputId="c.fieldname" />
                    <label :for="c.fieldname">{{ $t(c.label)  }}</label>
                </div>
            </div>
            <template #footer-left>
                <Button class="border-none" icon="pi pi-replay" :label="$t('Reset List') " @click="onResetTable" />
            </template>
        </ComOverlayPanelContent>
    </OverlayPanel>

    <OverlayPanel ref="showAdvanceSearch" style="max-width:70rem">
        <ComOverlayPanelContent title="Advance Filter" @onSave="onClearFilter" titleButtonSave="Clear Filter"
            icon="pi pi-filter-slash" :hideButtonClose="false" @onCancel="onCloseAdvanceSearch">
            <div class="grid">
                <div v-if="isMobile" class="col-12">
                            <div class="p-input-icon-left w-full">
                                <i class="pi pi-search" />
                                <InputText class="w-full" v-model="filter.keyword" :placeholder=" $t('Search') " @input="onSearch" />
                            </div>
                        </div>
                <div class="col-6 md:col-4">
                    <Calendar class="w-full" :selectOtherMonths="true" v-model="filter.start_date" placeholder="Start Date"
                        dateFormat="dd-mm-yy" @date-select="onDateSelect" showIcon />
                </div>
                <div class="col-6 md:col-4">
                    <Calendar class="w-full" :selectOtherMonths="true" v-model="filter.end_date" placeholder="End Date"
                        dateFormat="dd-mm-yy" showIcon @date-select="onDateSelect" />
                </div>
                <div class="col-6 md:col-4">
                    <ComAutoComplete v-model="filter.business_source" class="pb-2 w-full" placeholder="Business Source"
                        doctype="Business Source" @onSelected="onSearch" />
                </div>
                <div class="col-6 md:col-4">
                    <ComAutoComplete v-model="filter.city_ledger_type" class="pb-2 w-full" placeholder="City Ledger Type"
                        doctype="City Ledger Type" @onSelected="onSearch" :filters="['property', '=', property.name]" />
                </div>
                <!-- <Button @click="onSearch">Refresh</Button> -->
            </div>
        </ComOverlayPanelContent>
    </OverlayPanel>
</template>

<script setup>
import { ref, onMounted, onUnmounted, inject, computed, useDialog,getData } from '@/plugin'
import ComIFrameModal from '@/components/ComIFrameModal.vue';

import ComSummaryofBalance from '@/views/city_ledger/components/ComSummaryofBalance.vue' 
import {i18n} from '@/i18n';
import ComTopDebtorCompany from '@/views/city_ledger/components/ComTopDebtorCompany.vue';
import ComAgingBalance from '@/views/city_ledger/components/ComAgingBalance.vue';
const { t: $t } = i18n.global; 
 

const property = JSON.parse(localStorage.getItem("edoor_property"))
const working_day = JSON.parse(localStorage.getItem("edoor_working_day"))
const gv = inject('$gv');
const isMobile = ref(window.isMobile) 
const summary = ref()
const moment = inject("$moment")
const filter = ref({ start_date: moment.utc(working_day.date_working_day).startOf('month').toDate(), 
end_date: moment.utc(working_day.date_working_day).toDate(), guest: "",keyword:"" })
  
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
 
const refresh_aging_balance = ref(null); 
const refresh_top_debtor_company = ref(null); 
const Refresh = debouncer(() => {
    refresh_aging_balance.value.loadData();
    refresh_top_debtor_company.value.loadData();
    loadData();
}, 500);

async function loadData() {
    gv.loading = true
    const filters = JSON.parse(JSON.stringify(filter.value))
    filters.start_date = moment.utc(filter.value.start_date).format("YYYY-MM-DD")
    filters.end_date = moment.utc(filter.value.end_date).format("YYYY-MM-DD")
    filters.property = property.name
    filters.ledger_type="City Ledger"
    const res = await getData("frontdesk.get_ledger_balance", filters);
    
    if(res.data){
        summary.value = res.data
    }
    gv.loading = false

    
}

onMounted(async () => {
    if(window.isMobile){
        let elem = document.querySelectorAll(".p-dialog");
        if (elem){
            elem = elem[elem.length-1]
            elem?.classList.add("p-dialog-maximized"); // adds the maximized class
        }
    }
    window.socket.on("CityLedger", (arg) => {
        if (arg == property.name) {
            setTimeout(async function () {
                await loadData()
            }, 3000)
        }
    })

 
 
    await loadData()
})

onUnmounted(() => {
    window.socket.off("CityLedger");
})

 
</script>