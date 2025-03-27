<template>
    <ComFilterInput :option="option" 
        @onSearch="onSearch"
      v-model:operator="operator" 
       v-model:keyword="keyword"
       :operatorOptions="operatorOptions"
       v-model:listData="listData"
       v-model:selected = "selected"
       @onLoadOptionData = "onLoadOptionData"
       @onFilter="onFilter"
       >
      
       <span v-if="selected">{{ selected.value  }}</span>
       <span v-else>
        {{ option.label }}
       </span>
       
    </ComFilterInput>


</template>
<script setup>
import {ref,getData} from "@/plugin"
import ComFilterInput from "@/components/document/components/ComFilterInput.vue"
const props = defineProps({
    option:Object
})
const emit = defineEmits()
const operator = ref("=")
const keyword = ref("")
const operatorOptions = [
    {label:"Equal", value:'=',},
    {label:"Not Equal", value:'!='},
    {label:"In", value:'in'},
    {label:"Not In", value:'not in'},
    {label:"Is", value:'is'},
]
const selected = ref()
const listData = ref([1,2,3])
 
function onSearch(){
   
   
    onLoadOptionData()


}

function onFilter(){
    if(!selected.value){
        emit("onFilter",[props.option.fieldname,operator.value,null] )
    }else {
if(Array.isArray(selected.value)){
        emit("onFilter",[props.option.fieldname,operator.value,selected.value.map(r=>r.value)] )
    }else {
        emit("onFilter",[props.option.fieldname,operator.value,selected.value.value] )
    }
    }

    
    
}

async function onLoadOptionData(){
    const searchParams = {
        doctype: props.option.options,
        txt: keyword.value,
        limit_page_length: 50, 
        };
    const res = await     getData("frappe.desk.search.search_link", searchParams,"") ;
    if(!res.error){
        listData.value = res.data;
    }

    

}

 


</script>