<template>
 
    <span>{{ NumberFormat(format,   isNaN(amount)?0:amount) }}</span>
</template>
<script setup>

import {   defineProps, ref, computed } from '@/plugin';
import NumberFormat from 'number-format.js'
 
const setting = JSON.parse(  localStorage.getItem("edoor_setting"))
const props = defineProps({
    value: Number,
    currency: {
        type: String,
        default: ""
    }
})



const format = ref("#,###,##0.00##")
 

const currencyDefualt = {pos_currency_format : '$ #,###,##0.00', precision: 2}
const currency = ref()
if ( setting.currency && setting.currency.pos_currency_format){
    currency.value = setting.currency
}
else{
    currency.value = currencyDefualt

}

format.value = currency.value.pos_currency_format

const amount = computed(() => {
    let n = (props.value);
    if ((typeof n) == 'number') {
        return    Number(Math.round(n + 'e' + currency.value.precision) + 'e-' + currency.value.precision).toFixed(currency.value.precision);

    } else {
        return  0
    }
})



</script>