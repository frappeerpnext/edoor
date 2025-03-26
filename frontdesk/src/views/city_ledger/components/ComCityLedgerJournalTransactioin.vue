<template>
    <div class="py-0 px-1 -mt-2">
           <ComPlaceholder text="No Data"  :is-not-empty="data && data.length > 0">
                <DataTable 
                class="tb-cs-datatable"
                :value="data"
                tableStyle="min-width: 50rem" >
                <Column header="Tran#" style="width:max-content !important;max-width: max-content !important;">
                        <template #body="slotProps">
                            <button  @click="onOpenLink('view_folio_transaction_detail', slotProps.data?.name)"  :class="'link_line_action1 ' + (slotProps.data?.is_auto_post==1?'auto_post':'')">{{slotProps.data?.name }}</button>
                        </template>
                </Column>
                <Column header="Date" style="width:max-content !important;max-width: max-content !important;">
                        <template #body="slotProps">
                            {{ slotProps.data?.posting_date }}
                        </template>
                </Column>
                <Column header="Account" style="width:max-content !important;max-width: max-content !important;">
                        <template #body="slotProps">
                            {{ slotProps.data?.account_code }} - {{ slotProps.data?.account_name }}
                        </template>
                </Column>
                <Column header="Folio#" style="width:max-content !important;max-width: max-content !important;">
                        <template #body="slotProps">
                            <button v-if="slotProps.data?.source_transaction_number"  @click="onOpenLink('view_folio_detail', slotProps.data?.source_transaction_number)"  class="link_line_action1">{{slotProps.data?.source_transaction_number }}</button>
                        </template>
                </Column>
                <Column header="Room" style="width:max-content !important;max-width: max-content !important;">
                        <template #body="slotProps">
                            <span v-if="slotProps.data?.room_type">
                               {{ slotProps.data?.room_type }} / {{ slotProps.data?.room_number }} 
                            </span>
                            
                        </template>
                </Column>
                <Column header="Debit" style="width:max-content !important;max-width: max-content !important;">
                        <template #body="slotProps"> 
                            <span v-if="slotProps.data.type == 'Debit'">
                            <CurrencyFormat  :value="slotProps.data?.amount" />
                            </span>
                        </template>
                </Column>
                <Column header="Credit" style="width:max-content !important;max-width: max-content !important;">
                        <template #body="slotProps"> 
                            <span v-if="slotProps.data.type == 'Credit'">
                                <CurrencyFormat  :value="slotProps.data?.amount" />
                            </span>
                        </template>
                </Column>
                <Column header="Status" style="width:max-content !important;max-width: max-content !important;">
                        <template #body="slotProps"> 
                            <span v-if="slotProps.data.reservation_status"  class="px-2 rounded-lg text-white p-1px border-round-3xl"
                            :style="{ backgroundColor: slotProps.data.reservation_status_color }">
                            
                            {{ slotProps.data.reservation_status}}
                            </span>
                        </template>
                </Column>
                <Column header="By" style="width:max-content !important;max-width: max-content !important;">
                        <template #body="slotProps"> 
                           
                            {{ slotProps.data.owner}}
                        
                        </template>
                </Column>
                <Column header="Modified" style="width:max-content !important;max-width: max-content !important;">
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
        getApi("city_ledger.get_city_Ledger_jounal",{ property: window.property_name }).then((result)=>{
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