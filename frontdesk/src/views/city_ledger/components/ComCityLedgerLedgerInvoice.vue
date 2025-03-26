<template>
    <div class="py-0 px-1 -mt-2">
           <ComPlaceholder text="No Data"  :is-not-empty="data && data.length > 0">
                <DataTable 
                class="tb-cs-datatable"
                :value="data"
                tableStyle="min-width: 50rem" >
                <Column header="INV#" style="width:max-content !important;max-width: max-content !important;">
                        <template #body="slotProps">
                            <button  @click="onOpenLink('view_city_invoice_detail', slotProps.data?.name)"  :class="'link_line_action1 ' + (slotProps.data?.is_auto_post==1?'auto_post':'')">{{slotProps.data?.name }}</button>
                        </template>
                </Column>
                <Column header="City Ledger" style="width:max-content !important;max-width: max-content !important;">
                        <template #body="slotProps">
                            <button  @click="onOpenLink('view_city_ledger_detail', slotProps.data?.city_ledger)"  :class="'link_line_action1 ' + (slotProps.data?.is_auto_post==1?'auto_post':'')">
                                {{ slotProps.data?.city_ledger }} - 
                                {{slotProps.data?.city_ledger_name }}</button>
                        </template>
                </Column>
                <Column headerStyle="text-align: right;" bodyClass="text-right" header="Total Debit" style="width:max-content !important;max-width: max-content !important;">
                        <template #body="slotProps">
                            <CurrencyFormat  :value="slotProps.data?.total_debit" />
                        </template>
                </Column>
                <Column headerStyle="text-align: right;" bodyClass="text-right" header="Total Credit" style="width:max-content !important;max-width: max-content !important;">
                        <template #body="slotProps">
                            <CurrencyFormat  :value="slotProps.data?.total_credit" />
                        </template>
                </Column>
                <Column headerStyle="text-align: right;"  bodyClass="text-right" header="Balance" style="width:max-content !important;max-width: max-content !important;">
                        <template #body="slotProps">
                            <CurrencyFormat  :value="slotProps.data?.balance || 0.00" />
                        </template>
                </Column>
                <Column bodyClass="text-center" headerClass="text-center"  header="Payment Status" style="width:max-content !important;max-width: max-content !important;">
                        <template #body="slotProps">
                            {{ slotProps.data?.payment_status }}
                        </template>
                </Column>
                <Column header="Status" style="width:max-content !important;max-width: max-content !important;">
                        <template #body="slotProps"> 
                            <span v-if="slotProps.data.status"  class="px-2 rounded-lg text-white p-1px border-round-3xl"
                            :style="{ backgroundColor: slotProps.data.status == 'Open' ? '#8BFE9B' : '#6F6E6E' }">
                            
                            {{ slotProps.data.status}}
                            </span>
                        </template>
                </Column>
                <Column  header="By" style="width:max-content !important;max-width: max-content !important;">
                        <template #body="slotProps">
                            {{ slotProps.data?.owner }}
                        </template>
                </Column>
                <Column   header="modified" style="width:max-content !important;max-width: max-content !important;">
                        <template #body="slotProps">
                            <ComTimeago  :date='slotProps.data?.modified' />
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
        getApi("city_ledger.get_city_ledger_invoice",{ property: window.property_name }).then((result)=>{
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