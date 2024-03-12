<template>
    <div class="flex gap-2">
        <template v-if="!isMobile">
        <div >
            <Calendar :selectOtherMonths="true" class="w-full" v-model="hk.filter.selected_date" @date-select="onSearch" dateFormat="dd-mm-yy" showButtonBar showIcon panelClass="no-btn-clear"/>
        </div>
        <div class="p-0 w-15rem">
            <div class="p-input-icon-left w-full">
                <i class="pi pi-search" />
                <InputText class="w-full" v-model="hk.filter.keyword" :placeholder="$t('Search')" @input="onSearch" />
            </div>
        </div>
        <div class="w-30rem">
            <ComSelect maxWidth="30rem" width="30rem" :filters="[['property', '=', hk.property.name]]" class="linelight-edor w-auto flex height-of-filter" :isMultipleSelect="true" 
                isFilter 
                v-model="hk.filter.selected_housekeeping_status"
                placeholder="Housekeeping Status" 
                doctype="Housekeeping Status" 
                @onSelected="onSearch"
                :maxSelectLabel="10"
                />
        </div>
    </template>
        <div class="">
            <div class="flex gap-2">
                <Button icon="pi pi-sliders-h" class="content_btn_b" @click="advanceFilter"/> 
                <div v-if="isFilter">
                    <Button class="content_btn_b white-space-nowrap" :label="isMobile ? $t('Clear') : $t('Clear Filter') " icon="pi pi-filter-slash" @click="onClearFilter"/>
                </div>
            </div>
        </div>
    </div>
    <OverlayPanel ref="showAdvanceSearch" >
    <ComOverlayPanelContent title="Advance Filter" @onSave="onClearFilter" titleButtonSave="Clear Filter" icon="pi pi-filter-slash" :hideButtonClose="false" @onCancel="onCloseAdvanceSearch">
        <div class="grid">
            <template v-if="isMobile">
        <div class="col-12" >
            <Calendar :selectOtherMonths="true" class="w-full" v-model="hk.filter.selected_date" @date-select="onSearch" dateFormat="dd-mm-yy" showButtonBar showIcon panelClass="no-btn-clear"/>
        </div>
        <div class="col-12">
            <div class="p-input-icon-left w-full">
                <i class="pi pi-search" />
                <InputText class="w-full" v-model="hk.filter.keyword" :placeholder="$t('Search')" @input="onSearch" />
            </div>
        </div>
        <div class="col-12">
            <ComSelect maxWidth="30rem" width="30rem" :filters="[['property', '=', hk.property.name]]" class="linelight-edor w-auto flex height-of-filter" :isMultipleSelect="true" 
                isFilter 
                v-model="hk.filter.selected_housekeeping_status"
                placeholder="Housekeeping Status" 
                doctype="Housekeeping Status" 
                @onSelected="onSearch"
                :maxSelectLabel="10"
                />
        </div>
    </template>
            <div class="col-6 md:col-4">
                <ComSelect  :filters="[['property', '=', hk.property.name]]" v-model="hk.filter.selected_building" @onSelected="onSearch" placeholder="Building" doctype="Building" />
            </div>
            <div class="col-6 md:col-4">
                <ComSelect v-model="hk.filter.selected_floor" @onSelected="onSearch" placeholder="Floor" doctype="Floor" :filters="[['property', '=', hk.property.name]]" />
            </div>
            <div class="col-6 md:col-4">
                <ComSelect  :filters="[['property', '=', hk.property.name]]" v-model="hk.filter.selected_room_type_group" @onSelected="onSearch" placeholder="Room Type Group" doctype="Room Type Group" />
            </div>
            <div class="col-6 md:col-4">
                <ComSelect  :filters="[['property', '=', hk.property.name]]" isFilter v-model="hk.filter.selected_housekeeper" placeholder="Housekeeper" doctype="Housekeeper"
                    @onSelected="onSearch" />
            </div> 
            <div class="w-auto min-w-30rem col-8">
            <ComSelect :maxSelectedLabels="10"  maxWidth="31.2rem" width="31.6rem" mClass="
             text-overflow-ellipsis" :filters="[['property', '=', hk.property.name]]" class="linelight-edor height-of-filter flex max-w-25rem" :isMultipleSelect="true" 
                isFilter
                groupFilterField="room_type_group"
                :groupFilterValue="hk.filter.selected_room_type_group"  
                v-model="hk.filter.selected_room_type" 
                optionLabel="room_type"
                optionValue="name" 
                @onSelected="onSearch" 
                placeholder="Room Type" 
                doctype="Room Type"
                :maxSelectLabel="10">
            </ComSelect>
            
        </div>
        </div>        
    </ComOverlayPanelContent>
    </OverlayPanel>
</template>
<script setup>
import { ref,inject,onMounted,computed } from '@/plugin';
const showAdvanceSearch = ref()
const hk = inject("$housekeeping")
const gv = inject("$gv")
const isMobile = ref(window.isMobile) 
const moment = inject("$moment")
const working_date = JSON.parse(localStorage.getItem("edoor_working_day"))
import {i18n} from '@/i18n';
const { t: $t } = i18n.global;
const onSearch = debouncer(() => {
    hk.loadData();
}, 500);
const isFilter = computed(() => {
    if (moment(working_day.date_working_day).format('yyyy-MM-DD') != moment(hk.filter.selected_date).format('yyyy-MM-DD')) {
        return true
    }
    else {
        return gv.isNotEmpty(hk.filter, 'selected_date')
    }
})
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
const advanceFilter = (event) => {
    showAdvanceSearch.value.toggle(event);
}

const onClearFilter = () => {
    hk.filter = {
        selected_date: moment(working_date.date_working_day).toDate()
    };
    hk.loadData();
    showAdvanceSearch.value.hide()
}

const onCloseAdvanceSearch = () => {
    showAdvanceSearch.value.hide()
}
onMounted(() => {
    hk.filter.selected_date = moment(working_date.date_working_day).toDate()
})
</script>
<style scoped>
.linelight-edor{
    line-height: 1.2rem;
}
</style>