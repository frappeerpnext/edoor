<template>
    <ComOverlayPanelContent :title="$t('Advance Filter')" @onSave="onClearFilter" :titleButtonSave="$t('Clear Filter')" icon="pi pi-filter-slash" :hideButtonClose="false" @onCancel="onOpenAdvanceSearch(false)">
        <div :class="headerClass" v-if="filter">
            
                <ComSelect :class="bodyClass" width="100%" :placeholder="$t('All Room Group')" v-model="filter.room_type_group" doctype="Room Type Group" optionLabel="room_type_group" optionValue="name"></ComSelect>
          
            
            <ComSelect :class="bodyClass" :filters="[['property', '=', edoor_property.name]]" :placeholder="$t('All Room Types')" v-model="filter.room_type" doctype="Room Type" :groupFilterValue="filter.room_type_group" groupFilterField="room_type_group" optionLabel="room_type" optionValue="name"></ComSelect>
            
            <ComSelect :class="bodyClass" :filters="[['property', '=', edoor_property.name]]" :placeholder="$t('All Buildings')" v-model="filter.building" doctype="Building" optionLabel="building" optionValue="name"></ComSelect>
            <ComSelect :class="bodyClass" :filters="[['property', '=', edoor_property.name]]" :placeholder="$t('All Floors')" v-model="filter.floor" doctype="Floor" :groupFilterValue="filter.building" groupFilterField="building" optionLabel="floor" optionValue="name"></ComSelect>
            <div :class="bodyClass">
                <ComAutoComplete isFull :filters="[['property', '=', edoor_property.name]]" :placeholder="$t('All Business Source')" v-model="filter.business_source" doctype="Business Source" optionLabel="business_source" optionValue="name"/>
            </div>
        </div>
    </ComOverlayPanelContent>
</template>
<script setup> 
import { watch,ref,inject } from '@/plugin';
const emit = defineEmits(["onFilterResource"])
const edoor_property = JSON.parse(localStorage.getItem('edoor_property'))
import {i18n} from '@/i18n';
const { t: $t } = i18n.global;
const props = defineProps({
    headerClass: String,
    bodyClass: String
})

const { onFilterResource, advanceFilter,onOpenAdvanceSearch,onClearFilter } = inject('advance_filter')
const filter = ref(JSON.parse(JSON.stringify(advanceFilter.value)))

watch(filter.value, (newValue, oldValue) => {
    onFilterResource(newValue)
}) 
</script>