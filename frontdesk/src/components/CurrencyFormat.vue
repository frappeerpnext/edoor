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

let currency_name = props.currency

if (currency_name == "") {

    currency_name = gv.setting?.default_currency
}
const currencyDefualt = {pos_currency_format : '$ #,###,##0.00', currency_precision: 2}
const currency = gv.setting.currencies ? gv.setting?.currencies.find(r => r.name == currency_name) : currencyDefualt

if (currency) {

    format.value = currency.pos_currency_format
}

const amount = computed(() => {
    let n = (props.value);
    if ((typeof n) == 'number') {
        return   Number(n.toFixed(currency.currency_precision));
    } else {
        return  0
    }
}
)


</script>