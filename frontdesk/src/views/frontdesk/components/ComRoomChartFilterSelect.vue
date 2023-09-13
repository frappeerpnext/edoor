<template>
    <ComOverlayPanelContent title="Advance Filter" @onSave="onClearFilter" titleButtonSave="Clear Filter" icon="pi pi-filter-slash" :hideButtonClose="false" @onCancel="onOpenAdvanceSearch(false)">
        <div :class="headerClass" v-if="filter">
            <ComSelect class="col-4" width="100%" placeholder="All Room Group" v-model="filter.room_type_group" doctype="Room Type Group" optionLabel="room_type_group" optionValue="name"></ComSelect>
            <ComSelect class="col-4" :filters="[['property', '=', edoor_property.name]]" placeholder="All Room Types" v-model="filter.room_type" doctype="Room Type" :groupFilterValue="filter.room_type_group" groupFilterField="room_type_group" optionLabel="room_type" optionValue="name"></ComSelect>
            <!-- <div :class="bodyClass">
                <span class="p-input-icon-left w-full">
                    <i class="pi pi-filter" />
                    <InputText class="btn-set__h w-full" v-model="room_number" placeholder="All Rooms" v-debounce="onSearchRoom"/>
                </span>
            </div> -->
            <ComSelect class="col-4" :filters="[['property', '=', edoor_property.name]]" placeholder="All Buildings" v-model="filter.building" doctype="Building" optionLabel="building" optionValue="name"></ComSelect>
            <ComSelect class="col-4" :filters="[['property', '=', edoor_property.name]]" placeholder="All Floors" v-model="filter.floor" doctype="Floor" :groupFilterValue="filter.building" groupFilterField="building" optionLabel="floor" optionValue="name"></ComSelect>
            <ComSelect class="col-4" :filters="[['property', '=', edoor_property.name]]" placeholder="All Business Source" v-model="filter.business_source" doctype="Business Source" optionLabel="business_source" optionValue="name"></ComSelect>
        </div>
    </ComOverlayPanelContent>
</template>
<script setup> 
import { watch,ref,inject } from '@/plugin';
const emit = defineEmits(["onFilterResource"])
const edoor_property = JSON.parse(localStorage.getItem('edoor_property'))
const props = defineProps({
    headerClass: String,
    bodyClass: String
})
const { onFilterResource, advanceFilter,onOpenAdvanceSearch,onClearFilter } = inject('advance_filter')
const room_number = ref('')
const filter = ref(JSON.parse(JSON.stringify(advanceFilter.value)))
watch(filter.value, (newValue, oldValue) => {
    onFilterResource(newValue)
}) 
</script>