<template>

    <span :class="currAddClass?currAddClass:''">{{ NumberFormat(currency.pos_currency_format,   isNaN(amount)?0:amount) }}</span>
</template>
<script setup>

import {   defineProps, ref, computed } from '@/plugin';
import NumberFormat from 'number-format.js'
 
const setting = JSON.parse(  localStorage.getItem("edoor_setting"))
const props = defineProps({
    value: Number,
    currency: Object,
    currAddClass:String
})

 
 
const currency = ref(props.currency)
 
if (!currency.value){
        currency.value = setting.currency
}
  
const amount = computed(() => {
    let n = (props.value);
    if ((typeof n) == 'number') {
        return    Number(Math.round(n + 'e' + currency.value.precision) + 'e-' + currency.value.precision).toFixed(currency.value.precision);

    } else {
        return  0
    }
})



</script>