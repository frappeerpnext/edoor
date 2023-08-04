<template>
 
    <span>{{ numberFormat(format, amount) }}</span>
</template>
<script setup>

import { inject, defineProps, ref, computed } from '@/plugin';
const numberFormat = inject('$numberFormat')
const gv = inject("$gv")
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
if (gv.setting.currency && gv.setting.currency.pos_currency_format){
    currency.value = gv.setting.currency
}
else{
    currency.value = currencyDefualt

}

format.value = currency.value.pos_currency_format

const amount = computed(() => {
    let n = (props.value);
    if ((typeof n) == 'number') {
        return   Number(n.toFixed(currency.value.precision));
    } else {
        return  0
    }
})
 


</script>