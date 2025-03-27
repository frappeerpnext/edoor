<template>
    
    <ComFilterInput :option="option" 
     @onSearch="onSearch"
      v-model:operator="operator" 
       v-model:keyword="keyword"
       :operatorOptions="operatorOptions"
    
       >
       {{ keyword || option.label }}

       </ComFilterInput>
</template>
<script setup>
import {ref} from "@/plugin"
import ComFilterInput from "@/components/document/components/ComFilterInput.vue"
const props = defineProps({
    option:Object
})
const emit = defineEmits()
const operator = ref("like")
const keyword = ref("")
const operatorOptions = [
    {label:"Equal", value:'=',},
    {label:"Not Equal", value:'!='},
    {label:"Contain", value:'like',prefix:'%',sufix:'%'},
    {label:"Not Contain", value:'not like',prefix:'%',sufix:'%'},
    {label:"Start width", value:'like',sufix:'%'},
    {label:"End width", value:'like',prefix:'%'},
    {label:"Is", value:'is'},
]
 
function onSearch(){
    let searchValue = keyword.value;
    const op = operatorOptions.find(r=>r.value==operator.value);
    if(op.prefix){
        searchValue = op.prefix + searchValue;
    }
    
    if(op.sufix){
        searchValue =  searchValue + op.sufix;
    }
    

    emit("onFilter",[props.option.fieldname,operator.value,searchValue] )
}


</script>