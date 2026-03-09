<template>
    <ComDialogContent titleButtonOK="Save" @onOK="onSaveSelection" hideButtonClose :hideIcon="false">
        <Message v-if="hasAutoPost"> {{ $t('Transfer items can only be made to the same city ledger.') }} </Message>
   <div>
    <span>Target Transfer City Ledger Invoice</span>
<ComAutoComplete v-model="newCityledger" :placeholder="''"
                                         doctype="City Ledger Invoice"
                                         :filters="filterCityledger"
                                        class="auto__Com_Cus w-full"  />
                                        <ComReservationStayPanel class="h-full mt-3" title="Item Transferring">
                    <template #content>
                        <DataTable :rowClass="rowClass" class="p-datatable-sm mt-2" :value="data.selections"
                            tableStyle="">
                            <Column field="name" header="Folio Number"></Column>
                            <Column field="account_name" header="Account"></Column>
                            <Column header="Amount">
                                <template #body="{ data }">
                                    <CurrencyFormat :value="data.total_amount" />
                                </template>
                            </Column>
                        </DataTable>
                    </template>
                </ComReservationStayPanel>                                    
   </div>
   
</ComDialogContent>                                       
                                        </template>
<script setup>
import { ref, inject, useDialog, useConfirm ,postData, useToast } from '@/plugin'
import ComReservationStayPanel from '@/views/reservation/components/ComReservationStayPanel.vue';
const dialogRef = inject("dialogRef");
const dialog = useDialog()
const data = dialogRef.value.data
const newCityledger = ref()
const filterCityledger = ref()
const gv= inject("$gv")
const toast = useToast();

const hasAutoPost = dialogRef.value?.data?.selections?.some(
    item => item.is_auto_post === 1
);

if (hasAutoPost) {
    filterCityledger.value = {
        city_ledger: ['in', dialogRef.value.data.city_ledger]
    };
}




async function onSaveSelection(){
    if(!newCityledger.value){
        gv.toast('warn', 'Please select city ledger Invoice')
        return;
    }
    if(data.selections.length == 0){
        gv.toast('warn', 'Please select city ledger transaction')
        return;
    }
    else{
        const res = await postData("city_ledger_invoice.add_city_ledger_transaction_invoice", {
        city_ledger_invoice:newCityledger.value,
        old_city_ledger_invoice:data.name,
        data:data.selections.map(t => t.name)
    }, "", true, "edoor.edoor.doctype.city_ledger_invoice.");
    if(res.data){
   
        dialogRef.value.close(res.data)
        window.postMessage({ action: "CityLedgerInvoiceDetail" }, "*")
    }
    }
}
</script>