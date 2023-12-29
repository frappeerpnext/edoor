<template>
    <ComDialogContent :hideButtonClose="true" @onOK="onSave">

        <div v-if="cashCountSetting">
 
            <div class="flex w-full gap-3">
                <div class="bg-white flex flex-column rounded-lg grow p-2 shadow-charge-total border">
                    <span class="text-500 uppercase text-sm text-end">Open Cash Float</span><span
                        class="text-xl line-height-2 font-semibold text-end">
                        <span>
                            
                            <CurrencyFormat :value="doc.total_opening_amount" />
                        </span></span>
                </div>
                <div class="bg-white flex flex-column rounded-lg grow p-2 shadow-charge-total border">
                    <span class="text-500 uppercase text-sm text-end">Cash Debit</span><span
                        class="text-xl line-height-2 font-semibold text-end">
                        <span>
                            <CurrencyFormat :value="summary.cash_debit" />
                        </span></span></div>
                <div class="bg-white flex flex-column rounded-lg grow p-2 shadow-charge-total border">
                    <span class="text-500 uppercase text-sm text-end">Cash Credit</span><span
                        class="text-xl line-height-2 font-semibold text-end">
                        <span>
                            <CurrencyFormat :value="summary.cash_credit" />
                        </span></span>
                </div>
                <div
                    class="bg-green-50 border-green-edoor flex flex-column rounded-lg grow p-2 shadow-charge-total border">
                    <span class="text-500 uppercase text-sm text-end">Cash In Hand</span><span
                        class="text-xl line-height-2 font-semibold text-end">
                        <span>
                            <CurrencyFormat :value="summary.cash_in_hand" />
                        </span></span>
                </div>
                <div class="bg-white flex flex-column rounded-lg grow p-2 shadow-charge-total border">
                    <span class="text-500 uppercase text-sm text-end">Actual Cash</span><span
                        class="text-xl line-height-2 font-semibold text-end">
                        <span>
                            <CurrencyFormat :value="totalCashCountAmount" />
                        </span></span>
                </div>

                <div class="bg-red flex flex-column rounded-lg grow p-2 shadow-charge-total border">
                    <span class="text-500 uppercase text-sm text-end">Difference</span><span
                        class="text-xl line-height-2 font-semibold text-end">
                        <span>
                            <CurrencyFormat :value="((totalCashCountAmount > 0 ? totalCashCountAmount : doc?.total_close_amount) - doc?.total_system_close_amount) || 0" />
                        </span></span>
                </div>
            </div>
            <table class="w-full mt-4">

                <tr>
                    <td class="w-auto border-1 p-2 font-semibold">Note Type</td>
                    <td class="w-auto border-1 p-2 font-semibold">Total Note</td>
                    <td class="w-auto border-1 p-2 font-semibold text-right">Total Amount</td>
                </tr> 
                <template v-for="(c, index) in summary.expected_cash" :key="index">
                    <tr>
                        <td colspan="3" style='background: rgb(243, 243, 243);' class="w-auto border-1 p-2 font-semibold">
                            CASH {{ c.currency }}
                        </td>
                    </tr>
                    <tr v-for="(n, index) in cashCountSetting.filter(r => r.currency == c.currency)" :key="index">
                        <td class="w-auto border-1 p-2" style='background: rgb(243, 243, 243);'>
                            {{ n.label }}
                        </td>
                        <td class="w-auto border-1 p-2">
                            <InputNumber class="w-full" v-model="n.total_note" @input="onInputCashCount" />
                        </td>
                        <td class="w-auto border-1 p-2 font-semibold text-right">
                            <CurrencyFormat :value="n.value * n.total_note" :currency="n" />
                        </td>

                    </tr>
                    <tr>
                        <td class="w-auto border-1 p-2"><strong>Total</strong></td>
                        <td class="w-auto border-1 p-2 font-semibold">
                            <strong>
                            {{ cashCountSetting.filter(r => r.currency ==
                            c.currency).reduce((n, d) => n + (d.total_note || 0), 0) }}
                            </strong>
                        </td>
                        <td class="w-auto border-1 p-2 font-semibold text-right">
                            <strong>
                            <CurrencyFormat
                                :value="cashCountSetting?.filter(r => r.currency == c.currency).reduce((n, d) => n + (d.total_note * d.value || 0), 0)"
                                :currency="cashCountSetting?.filter(r => r.currency == c.currency)[0]" />
                            </strong>

                        </td>
                    </tr>
                </template>

            </table>
        </div>
    </ComDialogContent>
</template>
<script setup>
import { ref, onMounted, inject, computed, useDialog } from "@/plugin"
const cashCountSetting = ref()
const summary = ref()
const doc = ref()
const exchangeRates = ref()

const dialogRef = inject("dialogRef")
const mainCurrency = ref(window.setting.currency)
const secondCurrency = ref(window.setting.second_currency)


const dialog = useDialog();

const totalCashCountAmount = computed(() => {
    let totalCashCount = 0

    if (cashCountSetting.value?.filter(r => r.total_note > 0 & r.currency == mainCurrency.value.name).length > 0) {

        totalCashCount = totalMainCashCountAmount.value
    } else {
        totalCashCount = doc.value.main_total_close_amount || 0
    }


    if (cashCountSetting.value?.filter(r => r.total_note > 0 & r.currency == secondCurrency.value.name).length > 0) {
        const exchange_rate = exchangeRates.value?.find(r => r.to_currency == secondCurrency.value.name).exchange_rate
        totalCashCount = totalCashCount + totalSecondCashCountAmount.value / exchange_rate
    } else {


        const exchange_rate = exchangeRates.value?.find(r => r.to_currency == secondCurrency.value.name).exchange_rate

        totalCashCount = totalCashCount + ((doc.value.second_total_close_amount || 0) / exchange_rate)
    }
    return totalCashCount

})
const totalMainCashCountAmount = computed(() => {
    return cashCountSetting.value?.filter(r => r.currency == mainCurrency.value.name).reduce((n, d) => n + (d.total_note * d.value || 0) / d.exchange_rate, 0)
})
const totalSecondCashCountAmount = computed(() => {
    return cashCountSetting.value?.filter(r => r.currency == secondCurrency.value.name).reduce((n, d) => n + (d.total_note * d.value || 0), 0)
})



function onSave(){
    summary.value.expected_cash.forEach(c  => {
        c.input_close_amount = cashCountSetting.value.filter(r => r.currency == c.currency).reduce((n, d) => n + (d.total_note * d.value || 0), 0)
        c.total_cash_count =      c.input_close_amount
    });

    dialogRef.value.close({
        summary:summary.value,
        cash_count_setting:cashCountSetting.value
    })
}

onMounted(() => {

    cashCountSetting.value = dialogRef.value.data.cash_count_setting
    summary.value = dialogRef.value.data.summary
    doc.value = dialogRef.value.data.doc
    exchangeRates.value = dialogRef.value.data.exchange_rates
})


</script>