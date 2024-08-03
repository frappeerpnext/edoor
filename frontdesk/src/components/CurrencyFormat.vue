<template>
    <template v-if="hideWrapper">
        {{ NumberFormat(currency.pos_currency_format,   isNaN(amount)?0:amount) }}
    </template>
    <span v-else :class="currAddClass?currAddClass:''">{{ NumberFormat(currency.pos_currency_format,   isNaN(amount)?0:amount) }}</span>
    
</template>
<script setup>

import {   defineProps, ref, computed } from '@/plugin';
import NumberFormat from 'number-format.js'
 
const setting = JSON.parse(  localStorage.getItem("edoor_setting"))
const props = defineProps({
    value: Number,
    currency: Object,
    currAddClass:String,
    hideWrapper:Boolean
})

 
 
const currency = ref(props.currency)
 
if (!currency.value){
        currency.value = setting.currency
}
  
const amount = computed(() => {
    let n = (props.value);
    if ((typeof n) == 'number') {
        return   rounder(n,currency.value.precision)

    } else {
        return  0
    }
})

function rounder(num, decimalPlaces) {
  
  return Math.round(num * Math.pow(10, decimalPlaces)) / Math.pow(10, decimalPlaces );

}


</script>