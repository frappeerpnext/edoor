<template>

    <ComFilterInput :option="option" @onSearch="onSearch" v-model:operator="operator" v-model:keyword="selected"
        :operatorOptions="operatorOptions">
        {{ option.label }}
        

        <template v-slot:filter-template>
       
            <template v-if="['=', '>=', '!=', '>', '<', '<='].includes(operator)">
                <InputNumber v-model="selected" @input="onInput"   :minFractionDigits="0" :maxFractionDigits="9" fluid   v-debounce="onSearch" />
            </template>
           
            <template v-else-if="operator == 'Between'">
                <Stack row>
                    <InputNumber v-model="startNumber"    :minFractionDigits="0" :maxFractionDigits="9" fluid     />
                    <InputNumber v-model="endNumber"    :minFractionDigits="0" :maxFractionDigits="9" fluid     />
                </Stack>
                <Stack row>
                    
                        <Button label="Search" @click="onSearchBetween" class="w-full"></Button>
                        
                        <Button label="Clear Filter" class="w-full" @click="onClearSelection"
                            ></Button>
                        


                </Stack>


            </template>
             
        </template>
    </ComFilterInput>
</template>
<script setup>
import { ref } from "@/plugin"
import ComFilterInput from "@/components/document/components/ComFilterInput.vue"
const props = defineProps({
    option: Object
})

const startNumber = ref()
const endNumber = ref()
const emit = defineEmits()
const operator = ref("=")
const selected = ref(0)

 
const operatorOptions = [
    { label: "Equal", value: '=', },
    { label: "Not Equal", value: '!=' },
    { label: "Is", value: 'is' },
    { label: ">", value: '>' },
    { label: "<", value: '<' },
    { label: ">=", value: '>=' },
    { label: "<=", value: '<=' },
    { label: "Between", value: 'Between' }
]


function onInput(event){
    selected.value = event.value
}

function onSearch() {
 
   
            emit("onFilter", [props.option.fieldname, operator.value,selected.value])
       

    
}

function onSearchBetween() {
    alert(123)
    emit("onFilter", [
        [props.option.fieldname, '>=', startNumber.value],
        [props.option.fieldname, '<=', endNumber.value]
    ])
    
}
 
function onClearSelection() {
    
    endNumber.value = null
    startNumber.value = null
    emit("onFilter", [props.option.fieldname, operator.value,null])
}


</script>