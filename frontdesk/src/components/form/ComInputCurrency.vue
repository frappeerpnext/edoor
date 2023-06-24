<template>
    <div>
        <InputNumber 
            @update:modelValue="onUpdate"
            v-model="value"
            :minFractionDigits="setting.currency.precision"
            mode="currency" 
            :currency="setting.currency.name" 
            :locale="setting.currency.locale"
            :max="9999999999"
            />
    </div>
</template>
<script setup>
import {ref, computed} from 'vue'
const setting = JSON.parse(localStorage.getItem('edoor_setting'))
const emit = defineEmits(['update:modelValue'])
const props = defineProps({
    modelValue: [String, Number]
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