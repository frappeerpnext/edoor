<template>
 
    <ComFilterInput :option="option" 
     @onSearch="onSearch"
      v-model:operator="operator" 
       v-model:keyword="keyword"
       :operatorOptions="operatorOptions"
       v-model:selected="selected"
       :hasFilter="selected!=''"
       
       >
       {{$t(option.label) }}


      
       <template v-slot:filter-template v-if="operator!='is'">
        
            <Listbox 
                v-model="selected"
                :options="options"
                optionLabel="label"
                optionValue="value"
                 @change="onSearch"
                 class="w-full md:w-56">
                    <template #option="slotProps">
                        <span>{{ slotProps.option.label }}</span>
                    </template>
                </Listbox>
        
      </template>

      <template #bottom>
        <Button @click="onClearFilter" :disabled="!selected" :label="$t('Clear Filter')" severity="warning" class="w-full mt-4" />
       </template>

       </ComFilterInput>
</template>
<script setup>
import {ref,watch} from "@/plugin"
import ComFilterInput from "@/components/document/components/ComFilterInput.vue"
import { computed, onMounted } from "vue"
const props = defineProps({
    option:Object,
    defaultValue:Object//[key,"operator","value"]
})
const emit = defineEmits()
const operator = ref("=")
const selected = ref("")
import {i18n} from '@/i18n';
const { t: $t } = i18n.global;
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
 if((typeof props.option.options) =="string"){
    return props.option.options.split(/\r?\n/).filter(line => line.trim() !== "").map(r=>{
        return {
            label:r,
            value:r
        }
    });
 }else {
    return props.option.options
 }
    
})

const operatorOptions = [
    {label:$t("Equal"), value:'=',},
    {label:$t("Not Equal"), value:'!='},
    {label:$t("In"), value:'in'},
    {label:$t("Not In"), value:'not in'},
    {label:$t("Is"), value:'is'},
]
 
function onSearch(){
  
    emit("onFilter",[props.option.fieldname,operator.value,selected.value] )
}
function onClearFilter(){
    selected.value = "";
    emit("onFilter",[props.option.fieldname,operator.value,""] )
}


onMounted(()=>{
    if(props.defaultValue){
        operator.value = props.defaultValue[1]
        selected.value = props.defaultValue[2]
    }
})



</script>