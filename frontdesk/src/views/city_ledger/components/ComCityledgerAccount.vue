<template>
    <div class="py-0 px-1 -mt-2">
           <ComPlaceholder text="No Data"  :is-not-empty="data && data.length > 0">
            
                <DataTable 
                class="tb-cs-datatable"
                :value="data"
                tableStyle="min-width: 50rem" >
                <Column header="City Ledger Code" style="width:max-content !important;max-width: max-content !important;">
                        <template #body="slotProps">
                            <button  @click="onOpenLink('view_city_ledger_detail', slotProps.data?.name)"  :class="'link_line_action1 ' + (slotProps.data?.is_auto_post==1?'auto_post':'')">{{slotProps.data?.name }}</button>
                        </template>
                </Column>
                <Column header="City Ledger Name" style="width:max-content !important;max-width: max-content !important;">
                        <template #body="slotProps">
                            {{ slotProps.data?.city_ledger_name }}
                        </template>
                </Column>
                <Column header="City Ledger Type" style="width:max-content !important;max-width: max-content !important;">
                        <template #body="slotProps">
                            {{ slotProps.data?.city_ledger_type }}
                        </template>
                </Column>
                <Column header="Business Source" style="width:max-content !important;max-width: max-content !important;">
                        <template #body="slotProps">
                            <button v-if="slotProps.data?.business_source"  @click="onOpenLink('view_city_ledger_detail', slotProps.data?.name)"  class="link_line_action1">{{slotProps.data?.business_source }}</button>
                        </template>
                </Column>
                <Column header="Total Debit" style="width:max-content !important;max-width: max-content !important;">
                        <template #body="slotProps">
                            <span v-if="slotProps.data?.total_debit">
                                <CurrencyFormat  :value="slotProps.data?.total_debit" />
                            </span>
                            
                        </template>
                </Column>
                <Column header="Total Credit" style="width:max-content !important;max-width: max-content !important;">
                        <template #body="slotProps">
                            <span v-if="slotProps.data?.total_credit">
                                <CurrencyFormat  :value="slotProps.data?.total_credit" />
                            </span>
                            
                        </template>
                </Column>
                <Column header="Balance" style="width:max-content !important;max-width: max-content !important;">
                        <template #body="slotProps">
                            <span >
                                <CurrencyFormat  :value="slotProps.data?.balance || 0.00" />
                            </span>
                            
                        </template>
                </Column>
               

                </DataTable>
            </ComPlaceholder>
    </div>
</template>
<script setup>
 import { ref, onMounted, inject,onUnmounted , getApi , defineExpose } from "@/plugin"
 const data = ref()
 function loadData() {
        getApi("city_ledger.get_city_ledger_account",{ property: window.property_name }).then((result)=>{
            data.value = result.message;
    })
    }
    function onOpenLink(view, name) {
    window.postMessage(view + "|" + name , '*')
}
defineExpose({
 loadData
});
    onMounted(() => {
    loadData()
 
});    
</script>