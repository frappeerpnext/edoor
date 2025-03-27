<template>
    
    <ComFilterInput :option="option" 
     @onSearch="onSearch"
      v-model:operator="operator" 
       v-model:keyword="keyword"
       :operatorOptions="operatorOptions"
       >
       {{option.label }}

      
       <template v-slot:filter-template>
        
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
       </ComFilterInput>
</template>
<script setup>
import {ref} from "@/plugin"
import ComFilterInput from "@/components/document/components/ComFilterInput.vue"
import { computed } from "vue"
const props = defineProps({
    option:Object
})
const emit = defineEmits()
const operator = ref("=")
const selected = ref("")
 
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


</script>