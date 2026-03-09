<template>

    <ComFilterInput :option="option" @onSearch="onSearch" v-model:operator="operator" v-model:keyword="selected"
        :operatorOptions="operatorOptions" :hasFilter="selected!=null || startNumber!=null || endNumber!=null">
        {{$t(option.label) }} 
        

        <template v-slot:filter-template>
       
            <template v-if="['=', '>=', '!=', '>', '<', '<='].includes(operator)">
                <InputNumber v-model="selected" @input="onInput"   :minFractionDigits="0" :maxFractionDigits="9" fluid   v-debounce="onSearch" />
                <Button @click="onClearSelection" :disabled="!selected" label="Clear Filter" severity="warning" class="w-full" />
            </template>
           
            <template v-else-if="operator == 'Between'">
                <Stack row>
                    <InputNumber v-model="startNumber"    :minFractionDigits="0" :maxFractionDigits="9" fluid     />
                    <InputNumber v-model="endNumber"    :minFractionDigits="0" :maxFractionDigits="9" fluid     />
                </Stack>
                <Stack row>
                    
                        <Button :label="$t('Search')" @click="onSearchBetween" class="w-full"></Button>
                        
                        <Button :label="$t('Clear Filter')" class="w-full" @click="onClearSelection"  severity="warning"
                            ></Button>
                        


                </Stack>


            </template>
             
        </template>
        <template #bottom>
       
       </template>
    </ComFilterInput>
</template>
<script setup>
import { ref ,watch} from "@/plugin"
import ComFilterInput from "@/components/document/components/ComFilterInput.vue"
const props = defineProps({
    option: Object,
    defaultValue:Object//[key,"operator","value"]
})

const startNumber = ref(null)
const endNumber = ref(null)
const emit = defineEmits()
const operator = ref("=")
const selected = ref(null)
import {i18n} from '@/i18n';
const { t: $t } = i18n.global;
 
const operatorOptions = [
    { label: $t("Equal"), value: '=', },
    { label: $t("Not Equal"), value: '!=' },
    { label: $t("Is"), value: 'is' },
    { label: ">", value: '>' },
    { label: "<", value: '<' },
    { label: ">=", value: '>=' },
    { label: "<=", value: '<=' },
    { label: $t("Between"), value: 'Between' }
]

watch(() => props.defaultValue, (newVal, oldVal) => {
    if(props.defaultValue){ 
    if(newVal){
        if(newVal.length==3){
            operator.value = newVal[1]
            selected.value = newVal[2]
        }else {
            // between search
            operator.value = 'Between'
            startNumber.value = newVal[0][2]
            endNumber.value = newVal[1][2]
        }
        
      
    }
}else {
     selected.value = null
     startNumber.value = null
     endNumber.value = null

}
});


function onInput(event){
    selected.value = event.value
}

function onSearch() {
 if(operator.value!='Between' && operator.value !='is'){
    emit("onFilter", [props.option.fieldname, operator.value,selected.value])
    
 }
   
       

    
}

function onSearchBetween() {
     
    emit("onFilter", [
        [props.option.fieldname, '>=', startNumber.value],
        [props.option.fieldname, '<=', endNumber.value]
    ])
    
}
 
function onClearSelection() {
    selected.value = null
    endNumber.value = null
    startNumber.value = null
    emit("onFilter", [props.option.fieldname, operator.value,null])
}




</script>