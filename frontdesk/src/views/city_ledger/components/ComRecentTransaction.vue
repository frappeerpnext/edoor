<template>

    <div>
        <span class="text-xl">{{$t('Reccently Transactions')}}</span>
        <div class="mt-2">
 
        <TabView @tab-change="onTabChange" >
                <TabPanel  :header="$t('Journal Transactions')">
                    <ComCityLedgerJournalTransactioin/>    
                </TabPanel>
                <TabPanel :header="$t('City Ledger Accounts')">
                    <template  v-if="isTabLoaded('city_ledger_accounts')" >
                    <ComCityledgerAccount  /> 
                    </template>
                </TabPanel>
                <TabPanel   :header="$t('City Ledger Invoices')">
                    <ComCityLedgerLedgerInvoice v-if="isTabLoaded('city_ledger_invoices')"  />
                </TabPanel>
        </TabView>        
        </div>
    </div>
 
    </template>
    <script setup>
        import { ref,  inject  } from "@/plugin"  
 
    import ComCityLedgerJournalTransactioin from "@/views/city_ledger/components/ComCityLedgerJournalTransactioin.vue";
    import ComCityledgerAccount from "@/views/city_ledger/components/ComCityledgerAccount.vue";
    import ComCityLedgerLedgerInvoice from "@/views/city_ledger/components/ComCityLedgerLedgerInvoice.vue";
    const tabs =ref( [
        {index:0,tab_name:"journal_transactions",loaded:true,},
        {index:1,tab_name:"city_ledger_accounts",loaded:false,},
        {index:2,tab_name:"city_ledger_invoices",loaded:false,},
    ])
    
    function isTabLoaded(tab_name){
        return tabs.value.find(r=>r.tab_name==tab_name)?.loaded || false;
    }
    
    function onTabChange(event) {
        tabs.value.find(r=>r.index==event.index).loaded  =true
      
    }
 
        
 
    </script>