<template>
    
    <div class="flex-col flex view_sroll_mobile_table" >
        <div>
            <ComHeader colClass="col-6" isRefresh @onRefresh="Refresh()">
                <template #start>
                    <div class="text-2xl"> {{ $t('City Ledger') }} </div>
                </template>
                <template #end>
                    <SplitButton class="spl__btn_cs sp" @click="onPrint" label="Print" icon="pi pi-print" /> 
                </template>
            </ComHeader>
            
            <div>
                <ComLedgerBalanceKPI ledgerType="City Ledger" :startDate="filter.start_date" :endDate="filter.end_date" />
            </div>
        </div>
        <div class="grid">
<div class="col-12 lg:col-9">
    <ComTopDebtorCompany ref="refresh_top_debtor_company" />
    <ComRecentTransaction />
</div>
<div class="col-12 lg:col-3 bg-white border-round-lg">
    <ComAgingBalance  ref="refresh_aging_balance"/>
    <ComPendingCityLedgerInvoice />
    
</div>
        </div>
      
    </div>
 
</template>
 

<script setup>
import { ref, onMounted, onUnmounted, inject } from '@/plugin'


import ComLedgerBalanceKPI from '@/components/ComLedgerBalanceKPI.vue' 

import {i18n} from '@/i18n';
import ComTopDebtorCompany from '@/views/city_ledger/components/ComTopDebtorCompany.vue';
import ComAgingBalance from '@/views/city_ledger/components/ComAgingBalance.vue';
import ComRecentTransaction from '@/views/city_ledger/components/ComRecentTransaction.vue';
import ComPendingCityLedgerInvoice from '@/views/city_ledger/components/ComPendingCityLedgerInvoice.vue';
const { t: $t } = i18n.global; 
 


const gv = inject('$gv');
const isMobile = ref(window.isMobile) 
 
const filter = ref({ start_date:window.current_working_date, 
end_date: window.current_working_date, guest: "",keyword:"" })
  
function debouncer(fn, delay) {
    var timeoutID = null;
    return function () {
        clearTimeout(timeoutID);
        var args = arguments;
        var that = this;
        timeoutID = setTimeout(function () {
            fn.apply(that, args);
        }, delay);
    };
}
 
const refresh_aging_balance = ref(null); 
const refresh_top_debtor_company = ref(null); 
const Refresh = debouncer(() => {
    refresh_aging_balance.value.loadData();
    refresh_top_debtor_company.value.loadData();

}, 500);



onMounted(async () => {
    if(window.isMobile){
        let elem = document.querySelectorAll(".p-dialog");
        if (elem){
            elem = elem[elem.length-1]
            elem?.classList.add("p-dialog-maximized"); // adds the maximized class
        }
    }
    

 

})

onUnmounted(() => {
    window.socket.off("CityLedger");
})

 
</script> 
  