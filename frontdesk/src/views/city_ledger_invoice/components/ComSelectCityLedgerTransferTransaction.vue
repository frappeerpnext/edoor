<template>
    <ComDialogContent titleButtonOK="Save Selection" @onOK="onSaveSelection" hideButtonClose :hideIcon="false">
        <Grid>
            <Col>
            <Card class="m-0 p-0" :pt="{'body': { class: 'py-0' }}">
                <template #content>
<div>
    <table>
    <tr>
        <th class="py-2 mt-1 border-1 bg-slate-200 font-medium text-start ps-3" colspan="2">
            <b>
               City Ledger Detail - {{ doc?.status }}    
            </b>
                 </th>
    </tr>
     <ComStayInfoNoBox label="City Ledger">
        <strong class="link_line_action1 -ml-3" @click="onOpenLink('view_city_ledger_detail', doc.name)" >  
                          {{ doc?.name }} - {{ doc?.city_ledger_name }}
        </strong> 
    </ComStayInfoNoBox>   
    <ComStayInfoNoBox label="City Ledger Type" :value="doc?.city_ledger_type" />
    <ComStayInfoNoBox label="Contact Name" :value="doc?.contact_name" />
    <ComStayInfoNoBox label="Phone number" :value="doc?.phone_number" />
    <ComStayInfoNoBox label="Email" :value="doc?.email_address" />
    </table>
    
</div>
                </template>
            </Card>
            </Col>
            <Col>
            <Card class="m-0 p-0" :pt="{'body': { class: 'py-0' }}">
                <template #content>
                     <table >
                        <tbody>
                            <tr>
                                <th class="py-2 mt-1 border-1 bg-slate-200 font-medium text-start ps-3" colspan="2">
                                    {{ $t('City Ledger Invoice Information') }} - 
                                    <ComStatus :status="inv_value?.status" /> 
                                    <ComStatus :status="inv_value?.payment_status" /> 

                                </th>
                            </tr>
                            
                            <ComStayInfoNoBox label="Invoice #" :value="inv_value?.name" />
                            <ComStayInfoNoBox label="Reference #" :value="inv_value?.reference_number" />
                            <ComStayInfoNoBox label="City Ledger">
                                <Stack :row="true">
                                    <span   @click=""   v-tippy="'Click to view city ledger detail'" class="link_line_action1" style="margin-left: -10px;">{{ inv_value?.city_ledger }}</span> 
                                    <span v-tippy="'City Ledger Name'"> {{ inv_value?.city_ledger_name }},</span>
                                    <span v-tippy="'Contact Name'" v-if="inv_value?.contact_name"> {{ inv_value?.contact_name }},</span>
                                    <span v-tippy="'Phone Number'" v-if="inv_value?.phone_number"> {{ inv_value?.phone_number }}</span>
                                    
                                </Stack>
                                 
                            </ComStayInfoNoBox>
                            <ComStayInfoNoBox label="Posting Date">
                                <span class="font-semibold text-right -ms-3">
                                   
                                </span>
                            </ComStayInfoNoBox>
                        </tbody>
                    </table> 
                </template>
            </Card>
        </Col>
        </Grid>

        <Panel header="City Ledger Transactions" class="mt-4">
            <ComSelectFolioTransactionList :city_ledger="city_ledger" v-model:selectedData="selectedTransactions"/>
        </Panel>
    </ComDialogContent>




</template>
<script setup>
import { ref, inject, useDialog, onMounted, getDocument , postData } from '@/plugin'
import ComSelectFolioTransactionList from '@/views/city_ledger_invoice/components/ComSelectFolioTransactionList.vue';
const selectedTransactions = ref([])
const gv= inject("$gv")
const dialogRef = inject("dialogRef")
const doc = ref()
const inv_value = ref()
const loading = ref(true)
import {i18n} from '@/i18n';
const { t: $t } = i18n.global;
const dialog = useDialog()
const city_ledger = ref()
const city_ledger_invoice = ref()
function onOpenLink(view, name) {
    window.postMessage(view + "|" + name , '*')
}

async function onSaveSelection(){
    
    if(selectedTransactions.value.length == 0){
        gv.toast('warn', 'Please select city ledger transaction')
        return;
    }
    else{
        const res = await postData("city_ledger_invoice.add_city_ledger_transaction_invoice", {
        city_ledger_invoice:dialogRef.value.data.name,
        data:selectedTransactions.value.map(t => t.name)
    }, "", true, "edoor.edoor.doctype.city_ledger_invoice.");
    if(res.data){
   
        dialogRef.value.close(res.data)
        window.postMessage({ action: "CityLedgerInvoiceDetail" }, "*")
    }
    }
}


onMounted(async () => {
    city_ledger.value = dialogRef.value.data.city_ledger
    const res = await getDocument("City Ledger", city_ledger.value)
    if (!res.error) {
        doc.value = res.data
    }
    city_ledger_invoice.value = dialogRef.value.data.name
    const inv_data = await getDocument("City Ledger Invoice",city_ledger_invoice.value)
    if (!inv_data.error) {
        inv_value.value = inv_data.data
    }
    loading.value = false;

});
</script>