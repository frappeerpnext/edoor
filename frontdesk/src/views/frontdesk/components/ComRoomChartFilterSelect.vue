<template lang="">
    <div>
        <div class="flex flex-wrap gap-2">
            <div>
                <slot name="date"></slot>
            </div>
            <div>
                <ComSelect placeholder="All Room Group" v-model="filter.room_type_group" doctype="Room Type Group" optionLabel="room_type_group" optionValue="name"></ComSelect>
            </div>
            <div>
                <ComSelect placeholder="All Room Types" v-model="filter.room_type" doctype="Room Type" :groupFilterValue="filter.room_type_group" groupFilterField="room_type_group" optionLabel="room_type" optionValue="name"></ComSelect>
            </div>
            <div>
                <ComSelect placeholder="All Rooms" isFilter v-model="filter.room_number" doctype="Room" :groupFilterValue="filter.room_type" groupFilterField="room_type_id" optionLabel="room_number" optionValue="name"></ComSelect>
            </div>
            <div>
                <ComSelect placeholder="All Buildings" v-model="filter.building" doctype="Building" optionLabel="building" optionValue="name"></ComSelect>
            </div>
            <div>
                <ComSelect placeholder="All Floors" v-model="filter.floor" doctype="Floor" :groupFilterValue="filter.building" groupFilterField="building" optionLabel="floor" optionValue="name"></ComSelect>
            </div>
            <div>
                <span class="p-input-icon-left">
                    <i class="pi pi-search" />
                    <InputText class="btn-set__h" v-model="keyword" placeholder="Guest Name" v-debounce="onSearch"/>
                </span>
            </div>
        </div>
    </div>
</template>
<script setup> 
import { reactive,watch,ref } from 'vue';
const emit = defineEmits(["onFilterResource","onSearch"])
const keyword = ref("")
const filter = reactive({
    room_type: "",
    room_number: "",
    room_type_group: "",
    building: "",
    floor: ""
})
watch(filter, (newValue, oldValue) => {
    emit("onFilterResource",newValue)
})
function onSearch(key){
    emit("onSearch", key)
}
</script>
<style lang="">
    
</style>