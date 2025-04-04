<template>
 
    <ComFilterInput :option="option" 
     @onSearch="onSearch"
      v-model:operator="operator" 
       v-model:keyword="keyword"
       :operatorOptions="operatorOptions"
       v-model:selected="selected"
       :hasFilter="selected!=''"
       >
       {{option.label }}


      
       <template v-slot:filter-template v-if="operator!='is'">
        
            <Listbox 
                v-model="selected"
                :options="options"
                 @change="onSearch"
                 class="w-full md:w-56">
                    <template #option="slotProps">
                        <span>{{ slotProps.option }}</span>
                    </template>
                </Listbox>
        
      </template>

      <template #bottom>
        <Button @click="onClearFilter" :disabled="!selected" label="Clear Filter" severity="warning" class="w-full mt-4" />
       </template>

       </ComFilterInput>
</template>
<script setup>
import {ref,watch} from "@/plugin"
import ComFilterInput from "@/components/document/components/ComFilterInput.vue"
import { computed } from "vue"
const props = defineProps({
    option:Object,
    defaultValue:Object//[key,"operator","value"]
})
const emit = defineEmits()
const operator = ref("=")
const selected = ref("")

watch(() => props.defaultValue, (newVal, oldVal) => {
    if(props.defaultValue){  
    if(newVal){
        operator.value = newVal[1]
        selected.value = newVal[2]
    }
}else {
    selected.value = "";
}
});

const options = computed(()=>{
    return props.option.options.split(/\r?\n/).filter(line => line.trim() !== "");
})

const operatorOptions = [
    {label:"Equal", value:'=',},
    {label:"Not Equal", value:'!='},
    {label:"In", value:'in'},
    {label:"Not In", value:'not in'},
    {label:"Is", value:'is'},
]
 
function onSearch(){
  
    emit("onFilter",[props.option.fieldname,operator.value,selected.value] )
}
function onClearFilter(){
    selected.value = "";
    emit("onFilter",[props.option.fieldname,operator.value,""] )
}



</script>