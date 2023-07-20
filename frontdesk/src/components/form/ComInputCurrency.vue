<template>
    <div>
    
        <InputNumber 
            inputClass="w-full"
            class="w-full"
            :class="[`text-${align}`, classCss]"
            @update:modelValue="onUpdate"
            v-model="value"
            :minFractionDigits="setting.currency.precision"
            mode="currency" 
            :currency="setting.currency.name" 
            :locale="setting.currency.locale"
            :max="9999999999"
            :disabled="disabled"
      
            />
    </div>
</template>
<script setup>
import {ref, computed} from 'vue'
const setting = JSON.parse(localStorage.getItem('edoor_setting'))
const emit = defineEmits(['update:modelValue'])
const props = defineProps({
    modelValue: [String, Number],

    align: {
        type: String,
        defualt: "right"
    },
    disabled :Boolean,
    classCss: String,
   
})
let value = computed({
    get(){
        return props.modelValue
    },
    set(newValue){
        return newValue
    }
})

function onUpdate($event){
    emit('update:modelValue', $event)
}
</script>