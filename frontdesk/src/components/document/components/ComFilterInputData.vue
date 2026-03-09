<template>
    
    <ComFilterInput :option="option" 
     @onSearch="onSearch"
      v-model:operator="operator" 
       v-model:keyword="keyword"
       :operatorOptions="operatorOptions"
       :hasFilter="keyword!=''"
        v-model:selected ="selected"
       >
       {{ $t(option.label) }}

       <template #bottom>
        <Button @click="onClearFilter" :disabled="!keyword" :label='$t("Clear Filter")' severity="warning" class="w-full mt-4" />
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
import {i18n} from '@/i18n';
const { t: $t } = i18n.global;
const operatorOptions = [
    {label:$t("Equal"), value:'=',},
    {label:$t("Not Equal"), value:'!='},
    {label:$t("Contain"), value:'like',prefix:'%',sufix:'%'},
    {label:$t("Not Contain"), value:'not like',prefix:'%',sufix:'%'},
    {label:$t("Start width"), value:'like',sufix:'%'},
    {label:$t("End width"), value:'like',prefix:'%'},
    {label:$t("Is"), value:'is'},
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