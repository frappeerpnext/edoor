<template>
    <Stack row>
       
        <InputText  v-model="filter.keyword" variant="filled" placeholder="Search" size="small" v-debounce="onSearch"/>
        <template v-for="(f, index) in filters" :key="index">
            <ComFilterInputData v-if="f.fieldtype=='Data'" :option="f"  @onFilter="onFilter"   />
            <ComFilterInputLink v-if="f.fieldtype=='Link'" :option="f"  @onFilter="onFilter"   />
            <ComFilterInputDate v-if="f.fieldtype=='Date'" :option="f"  @onFilter="onFilter"   />
            <ComFilterInputSelect v-if="f.fieldtype=='Select'" :option="f"  @onFilter="onFilter"   />
            <ComFilterInputNumber v-if="['Currency','Int','Float'].includes(f.fieldtype)" :option="f"  @onFilter="onFilter"   />
        </template>
        

    </Stack>
   
</template>
<script setup>
import {ref} from "@/plugin"
import ComFilterInputData from "@/components/document/components/ComFilterInputData.vue"
import ComFilterInputLink from "@/components/document/components/ComFilterInputLink.vue"
import ComFilterInputDate from "@/components/document/components/ComFilterInputDate.vue"
import ComFilterInputSelect from "@/components/document/components/ComFilterInputSelect.vue"
import ComFilterInputNumber from "@/components/document/components/ComFilterInputNumber.vue"
const props = defineProps({
    filters:Object
})
const emit = defineEmits()
const filter = ref({
    keyword : ""
})
function  onSearch(){
    
    emit("onSearch",filter.value);
}

function onFilter(f){
    if((typeof f[0]) =="string"){
        if(f[2]){
        filter.value[f[0]] = f;
      
    }else {
        delete filter.value[f[0]]
    }
    }else {
        filter.value[f[0][0]] = f;
    }
  
    
    emit("onSearch",filter.value);
}

function onRemove(){
    alert("xx")
}

</script>