<template>
    <ComDialogContent @onOK="onSave" titleButtonOK="Ok" :loading="isSaving" hideButtonClose>
        <div class="grid">
            <div class="w-full">
                <table class="w-full">
                    <ComStayInfoNoBox label="Current Tax Invoice" value="#Inv" />
                <ComStayInfoNoBox label="Next Tax Invoice" value="#Inv" /> 
                </table>
                <div class="text-center shadow-1 p-3 mt-3 border-round-xl">
                        <div class="text-2xl">Rate Exchange</div>
                        <span v-for="(c, index) in exchangeRates" :key="index" class="text-2xl">
                            <CurrencyFormat currAddClass="font-semibold" :value="1" />({{ c.base_currency }}) =
                            <CurrencyFormat currAddClass="font-semibold" :value="c.exchange_rate" :currency="c" /> ({{
                                c.to_currency }})
                        </span>
                    </div>
            </div>
        </div>
    </ComDialogContent>
</template>
<script setup>
import { inject, ref, onMounted,createUpdateDoc,getDoc ,getApi} from "@/plugin"
import {i18n} from '@/i18n';
const { t: $t } = i18n.global; 
const dialogRef = inject("dialogRef");
const isSaving = ref(false)
const exchangeRates = ref()
function onSave() {
  
}
 function getCashCountSetting() {
    getApi("utils.get_cash_count_setting").then(result => {
        exchangeRates.value = result.message.exchange_rate_data
    })
}

onMounted(() => {
    getCashCountSetting()
});


</script>