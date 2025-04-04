<template>
    <ComDialogContent hideButtonOK :hideIcon="false" :loading="loading">
        <div v-if="doc" class="mt-2">
    
            <ComCityLedgerInvoiceAction :folio="doc" :newDoc="newDoc" @onClose="onClose" />

            <div class="grid" style="margin-top: 10px;">
                <div class="col">
                    <table >
                        <tbody>
                            <tr>
                                <th class="py-2 mt-1 border-1 bg-slate-200 font-medium text-start ps-3" colspan="2">
                                    {{ $t('City Ledger Invoice Information') }} - 
                                    <span v-if="doc.status"  class="px-2 rounded-lg text-white p-1px border-round-3xl"
                            :style="{ backgroundColor: doc.status == 'Open' ? '#8BFE9B' : '#6F6E6E' }">
                            
                            {{ doc.status}}
                            </span>
                            <span 
                            v-if="doc.status"  
                            class="px-2 rounded-lg text-white p-1px border-round-3xl ms-2"
                            :style="{ 
                            backgroundColor: 
                            doc.payment_status === 'Unpaid' ? '#FF0000' :    // Red
                            doc.payment_status === 'Partially Paid' ? '#FFFF00' :  // Yellow
                            doc.payment_status === 'Paid' ? '#008000' : '#6F6E6E'  // Default Grey
                            }"
                            >
                            {{ doc.payment_status }}
                            </span>

                                </th>
                            </tr>
                            
                            <ComStayInfoNoBox label="INV#" :value="doc?.name" />
                            <ComStayInfoNoBox label="Refernce #" :value="doc?.reference_number" />
                            <ComStayInfoNoBox label="City Ledger">
                                <Stack :row="true">
                                    <span   @click="OnViewCityLedgerDetail"   v-tippy="'Click to view city ledger detail'" class="link_line_action1" style="margin-left: -10px;">{{ doc?.city_ledger }}</span> 
                                    <span v-tippy="'City Ledger Name'"> {{ doc?.city_ledger_name }},</span>
                                    <span v-tippy="'Contact Name'" v-if="doc?.contact_name"> {{ doc?.contact_name }},</span>
                                    <span v-tippy="'Phone Number'" v-if="doc?.phone_number"> {{ doc?.phone_number }}</span>
                                    
                                </Stack>
                                 
                            </ComStayInfoNoBox>
                            <ComStayInfoNoBox label="Posting Date">
                                <span class="font-semibold text-right -ms-3">
                                    {{ moment.utc(doc?.posting_date).format("DD-MM-YYYY") }}
                                </span>
                            </ComStayInfoNoBox>
                            <ComStayInfoNoBox label="Payment Status" :value="doc?.payment_status" />
                            <ComStayInfoNoBox label="By">
                                <span @click="" class="-ms-3 text-right">
                                    {{ doc?.owner }},
                                    <ComTimeago :date="doc?.creation" />
                                </span>
                            </ComStayInfoNoBox>
                            <ComStayInfoNoBox label="Modified">
                                <span class="font-semibold text-right -ms-3">
                                    {{ doc?.modified_by }} ,
                                    <ComTimeago :date="doc?.modified" />
                                </span>
                            </ComStayInfoNoBox>
                        </tbody>
                    </table>
                </div>
                <div class="col">
                    <div class="col">
                        <div class="flex mb-2 mt-2 gap-2 text-right">
                            <div
                                class="col p-2 bg-gray-edoor-10 rounded-lg shadow-charge-total border border-gray-edoor-100">
                                <div class="text-500 uppercase text-sm"> {{ $t('Total Debit') }} </div>
                                <div class="text-xl line-height-2 font-bold">
                                    <CurrencyFormat :value="doc?.total_debit" isCurrency></CurrencyFormat>
                                </div>
                            </div>
                            <div
                                class="col p-2 bg-gray-edoor-10 rounded-lg shadow-charge-total border border-gray-edoor-100 h-full">
                                <div class="text-500 uppercase text-sm"> {{ $t('Total Credit') }} </div>
                                <div class="text-xl line-height-2 font-semibold">
                                    <CurrencyFormat :value="doc?.total_credit" isCurrency></CurrencyFormat>
                                </div>
                            </div>
                            <div class="col p-2 bg-green-50 rounded-lg shadow-charge-total border border-green-edoor">
                                <div class="text-500 uppercase text-sm"> {{ $t('Balance') }} </div>


                                <div class="text-xl line-height-2 font-semibold">
                                    <CurrencyFormat :value="(doc?.balance)" isCurrency></CurrencyFormat>
                                </div>
                            </div>
                        </div>

                    </div>

                    <div>
                          <div v-for="(item, index) in balance_doc" :key="index" class="flex mt-2 gap-2">
                    <ComBoxStayInformation  :title="item?.account_group_name || 'Undefine'" :value="item?.total_amount || 0"
                        isCurrency valueClass="col-6 text-right bg-gray-edoor-10 font-semibold"
                        titleClass="col font-semibold">
                    </ComBoxStayInformation>
                </div>
                    </div>
                </div>

            </div>
            <div v-if="doc.note">
               <b>Note</b>
           <div class="border-1 border-round-lg shadow-sm px-3 py-2 mb-2"> 
{{ doc.note }}
           </div>  
            </div>
            <Stack>
                <ComCityledgerInvoiceTransactionsAction :data="doc" v-model:selections="selectedfolioTransactions"  />
                <ComFolioTransactionCreditDebitStyle v-model:selectedfolioTransactions="selectedfolioTransactions"  :cityLedgerInvoice="name" v-if="doc?.name" :folio="doc"
                    :transaction_number="doc?.city_ledger"  doctype="City Ledger" :showCheckbox="true">
                    <template  #description="{ item, index }">
                        <div v-if="item.reservation">
                        <div >
                        Guest: {{ item.guest_name }} -
                        <span :style="{ color: item.reservation_status_color }">
                          {{item.reservation_status}}  
                        </span>
                        <div>
                            RS: <span v-if="item.reservation" @click="onOpenLink('view_reservation_detail', item.reservation)" class="text-blue-300 cursor-pointer w-auto"> {{ item.reservation }} </span>    
                            | 
                            ST: <span v-if="item.reservation" @click="onOpenLink('view_reservation_stay_detail', item.reservation_stay)" class="text-blue-300 cursor-pointer w-auto"> {{ item.reservation_stay }} </span>
                        </div></div>
                        </div>
                    </template>
                    <template  #posting_date="{ item, index }">                       
                    </template>
                    <template #room="{ item, index }" >
                        <div>
                    {{ item.room_type }}        
                        </div>
                    </template>
                    <template  #name="{ item, index }">
                    </template>
                </ComFolioTransactionCreditDebitStyle>
            </Stack>


        </div>
    </ComDialogContent>
</template>
<script setup>
import { ref, inject, useDialog, onMounted,   getDocument , getApi,onUnmounted , getDoc } from '@/plugin'
import ComCityLedgerInvoiceAction from '@/views/city_ledger_invoice/components/ComCityLedgerInvoiceAction.vue';
import ComFolioTransactionCreditDebitStyle from "@/views/reservation/components/folios/ComFolioTransactionCreditDebitStyle.vue"
import {i18n} from '@/i18n';
import ComBoxStayInformation from '@/views/reservation/components/ComBoxStayInformation.vue';
import ComCityledgerInvoiceTransactionsAction from './ComCityledgerInvoiceTransactionsAction.vue';
import {useApp} from "@/hooks/useApp"
const {isCityLedgerInvoiceDetailOpen} = useApp()


const dialogRef = inject("dialogRef")
const loading = ref(true)
const balance_doc = ref()
const dialog = useDialog()
const moment = inject("$moment")
const name = ref("")
const doc = ref({})
const show_detail = ref(false)
const property = JSON.parse(localStorage.getItem("edoor_property"))
const { t: $t } = i18n.global;
const newDoc = ref()
const selectedfolioTransactions = ref([])
function onOpenLink(view, name) {
    window.postMessage(view + "|" + name , '*')
}


function OnViewCityLedgerDetail(){
  
    window.postMessage("view_city_ledger_detail|" + doc.value.city_ledger,"*");
}
async function loadData(){
    isCityLedgerInvoiceDetailOpen.value = true
    getApi("city_ledger.get_balance_city_ledger_transaction",{ property: window.property_name , city_ledger_invoice : dialogRef.value.data.name }).then((result)=>{
        balance_doc.value = result.message;
    })
    name.value = dialogRef.value.data.name;
    loading.value = true
    const res = await getDocument('City Ledger Invoice', dialogRef.value.data.name)
    if (!res.error) {
        doc.value = res.data;
        newDoc.value = {
                property:window.property_name,
                transaction_number:doc.value.city_ledger,
                transaction_type:"City Ledger",
                city_ledger_invoice: doc.value.name

            }
    }
    loading.value = false
}
const actionRefreshData = async function (e) {
    if (e.isTrusted && typeof (e.data) != 'string') {
        if(e.data.action=="CityLedgerInvoiceDetail"){
            setTimeout(()=>{
                loadData(false)
            },1000)
            
        }
    };
}

onMounted(async () => {
   
    loadData()
    window.addEventListener('message', actionRefreshData, false); 
});
onUnmounted(()=>{
    isCityLedgerInvoiceDetailOpen.value = false
})
</script>