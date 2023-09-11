<template>
    <div class="flex gap-2">
        <div class="p-0 w-15rem">
            <div class="p-input-icon-left w-full">
                <i class="pi pi-search" />
                <InputText class="w-full" v-model="hk.filter.keyword" placeholder="Search" @input="onSearch" />
            </div>
        </div>
        <div class="w-auto max-w-25rem">
            <ComSelect :filters="[['property', '=', hk.property.name]]" class="linelight-edor height-of-filter flex" :isMultipleSelect="true" 
                        isFilter
                        groupFilterField="room_type_group"
                        :groupFilterValue="hk.filter.selected_room_type_group"  
                        v-model="hk.filter.selected_room_type" 
                        optionLabel="room_type"
                        optionValue="name" 
                        @onSelected="onSearch" 
                        placeholder="Room Type" 
                        doctype="Room Type"
                        ></ComSelect>
        </div>
        <div class="w-15rem">
            <ComSelect :filters="[['property', '=', hk.property.name]]" class="linelight-edor w-auto flex height-of-filter" :isMultipleSelect="true" isFilter v-model="hk.filter.selected_housekeeping_status"
                placeholder="Housekeeping Status" doctype="Housekeeping Status" @onSelected="onSearch" />
        </div>
        <div class="">
            <div class="flex gap-2">
                <Button icon="pi pi-sliders-h" class="content_btn_b" @click="advanceFilter"/> 
                <div v-if="gv.isNotEmpty(hk.filter)">
                    <Button class="content_btn_b white-space-nowrap" label="Clear Filter" icon="pi pi-filter-slash" @click="onClearFilter"/>
                </div>
            </div>
        </div>
    </div>
    <OverlayPanel ref="showAdvanceSearch" style="max-width:70rem">
    <ComOverlayPanelContent title="Advance Filter" @onSave="onClearFilter" titleButtonSave="Clear Filter" icon="pi pi-filter-slash" :hideButtonClose="false" @onCancel="onCloseAdvanceSearch">
        <div class="grid">
            <div class="col-4">
                <ComSelect  :filters="[['property', '=', hk.property.name]]" v-model="hk.filter.selected_building" @onSelected="onSearch" placeholder="Building" doctype="Building" />
            </div>
            <div class="col-4">
                <ComSelect v-model="hk.filter.selected_floor" @onSelected="onSearch" placeholder="Floor" doctype="Floor" />
            </div>
            <div class="col-4">
                <ComSelect  :filters="[['property', '=', hk.property.name]]" v-model="hk.filter.selected_room_type_group" @onSelected="onSearch" placeholder="Room Type Group" doctype="Room Type Group" />
            </div>
            <div class="col-4">
                <ComSelect  :filters="[['property', '=', hk.property.name]]" isFilter v-model="hk.filter.selected_housekeeper" placeholder="Housekeeper" doctype="Housekeeper"
                    @onSelected="onSearch" />
            </div> 
        </div>        
    </ComOverlayPanelContent>
    </OverlayPanel>
</template>
<script setup>
import { ref,inject } from '@/plugin';
const showAdvanceSearch = ref()
const hk = inject("$housekeeping")
const gv = inject("$gv")

const filter = ref({})
const onSearch = debouncer(() => {
    hk.loadData();
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

const advanceFilter = (event) => {
    showAdvanceSearch.value.toggle(event);
}
const onClearFilter = () => {
    hk.filter = {};
    hk.loadData();
    showAdvanceSearch.value.hide()
}
const onCloseAdvanceSearch = () => {
    showAdvanceSearch.value.hide()
}



</script>
<style scoped>
.linelight-edor{
    line-height: 1.2rem;
}
</style>