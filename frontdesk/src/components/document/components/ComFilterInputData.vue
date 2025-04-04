<template>
    
    <ComFilterInput :option="option" 
     @onSearch="onSearch"
      v-model:operator="operator" 
       v-model:keyword="keyword"
       :operatorOptions="operatorOptions"
       :hasFilter="keyword!=''"
        v-model:selected ="selected"
       >
       {{option.label }}

       <template #bottom>
        <Button @click="onClearFilter" :disabled="!keyword" label="Clear Filter" severity="warning" class="w-full mt-4" />
       </template>
    </ComFilterInput>

</template>
<script setup>
import {ref,watch} from "@/plugin"
import ComFilterInput from "@/components/document/components/ComFilterInput.vue"
const props = defineProps({
    option:Object,
    defaultValue:Object//[key,"operator","value"]
})
const emit = defineEmits()
const operator = ref("like")
const keyword = ref("")
const selected = ref("")
const operatorOptions = [
    {label:"Equal", value:'=',},
    {label:"Not Equal", value:'!='},
    {label:"Contain", value:'like',prefix:'%',sufix:'%'},
    {label:"Not Contain", value:'not like',prefix:'%',sufix:'%'},
    {label:"Start width", value:'like',sufix:'%'},
    {label:"End width", value:'like',prefix:'%'},
    {label:"Is", value:'is'},
]
 

watch(() => props.defaultValue, (newVal, oldVal) => {
    if(props.defaultValue){ 
    if(newVal){
        operator.value = newVal[1]
        keyword.value = newVal[2].replaceAll("%","")
        selected.value = keyword.value ;

    }
}else {
     keyword.value = "";
    selected.value = ""
}
});

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


function onClearFilter(){
    keyword.value = "";
    selected.value = ""
    emit("onFilter",[props.option.fieldname,operator.value,""] )
}


</script>