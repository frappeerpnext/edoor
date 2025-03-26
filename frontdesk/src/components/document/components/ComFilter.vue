<template>
    <Stack row>
        <InputText  v-model="filter.keyword" variant="filled" placeholder="Search" size="small" v-debounce="onSearch"/>
       
        <ComFilterInputData :option="{label:'Reservation',fieldname:'reservation'}"  @onFilter="onFilter"   />

    </Stack>
   
</template>
<script setup>
import {ref} from "@/plugin"
import ComFilterInputData from "@/components/document/components/ComFilterInputData.vue"
const emit = defineEmits()
const filter = ref({
    keyword : ""
})
function  onSearch(){
    
    emit("onSearch",filter.value);
}

function onFilter(f){
    if(f[2]){
        filter.value[f[0]] = f;
      
    }else {
        delete filter.value[f[0]]
    }
    
    emit("onSearch",filter.value);
}

function onRemove(){
    alert("xx")
}

</script>