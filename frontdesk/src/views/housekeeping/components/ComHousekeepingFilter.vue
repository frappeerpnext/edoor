<template>
<div>
    <ComSelect  :filters="[['property', '=', hk.property.name]]" v-model="hk.filter.selected_building" @onSelected="onSearch" placeholder="Building" doctype="Building" />
</div>
<div>
    <ComSelect v-model="hk.filter.selected_floor" @onSelected="onSearch" placeholder="Floor" doctype="Floor" />
</div>
<div>
    <ComSelect  :filters="[['property', '=', hk.property.name]]" v-model="hk.filter.selected_room_type_group" @onSelected="onSearch" placeholder="Room Type Group" doctype="Room Type Group" />
</div>
<div>
    <ComSelect :filters="[['property', '=', hk.property.name]]" class="linelight-edor" :isMultipleSelect="true" 
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
<div>
    <ComSelect  :filters="[['property', '=', hk.property.name]]" class="linelight-edor" :isMultipleSelect="true" isFilter v-model="hk.filter.selected_housekeeping_status"
        placeholder="Housekeeping Status" doctype="Housekeeping Status" @onSelected="onSearch" />
</div>
<div>
    <ComSelect  :filters="[['property', '=', hk.property.name]]" isFilter v-model="hk.filter.selected_housekeeper" placeholder="Housekeeper" doctype="Housekeeper"
        @onSelected="onSearch" />
</div>  
    
</template>
<script setup>
import { ref,inject } from '@/plugin';

const hk = inject("$housekeeping")

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

 



</script>
<style scoped>
.linelight-edor{
    line-height: 1.2rem;
}
</style>