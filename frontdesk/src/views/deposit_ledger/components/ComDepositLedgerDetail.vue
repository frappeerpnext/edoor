<template>
    <ComDialogContent :hideButtonOK="true" @onClose="onClose" style="min-height:70vh;" :hideIcon="false" :loading="loading">
        <TabView>
            <TabPanel header="Deposit Ledger Information">
                <div v-if="doc" class="mt-2">
                    <ComDepositLedgerAction :folio="doc" :newDoc="newDoc" @onClose="onClose" />

                    <div class="grid">
                        <div class="col">
                            <table class="mb-4">
                                <tr>
                                    <th class="py-2 mt-1 border-1 bg-slate-200 font-medium text-start ps-3" colspan="2">
                                        Deposit Ledger
                                    </th>
                                </tr>
                                <ComStayInfoNoBox label="Posting Date">
                                    {{ moment(doc.posting_date).format("DD-MM-YYYY") }}
                                </ComStayInfoNoBox>
                                <ComStayInfoNoBox label="Guest">
                                    <span @click="onViewCustomerDetail(doc.guest)"
                                        class="-ml-2 text-right link_line_action1">
                                        {{ doc.guest }} - {{ doc.guest_name }}
                                    </span>
                                </ComStayInfoNoBox>
                                <ComStayInfoNoBox label="Room">
                                    <span class="font-semibold text-right">
                                        {{ doc.room_number }} <span v-if="doc.room_number">({{ doc.room_type }})</span>
                                    </span>
                                </ComStayInfoNoBox>
                                <ComStayInfoNoBox label="Note">
                                    <span class="font-semibold text-right">
                                        {{ doc.note }}
                                    </span>
                                </ComStayInfoNoBox>
                            </table>
                        </div>
                        <div class="col">
                            <div class="flex mb-2 mt-2 gap-2 text-right">

                                <div
                                    class="col p-2 bg-gray-edoor-10 rounded-lg shadow-charge-total border border-gray-edoor-100">
                                    <div class="text-500 uppercase text-sm">Total Debit</div>
                                    <div class="text-xl line-height-2 font-semibold">
                                        <CurrencyFormat :value="doc?.total_debit" isCurrency></CurrencyFormat>
                                    </div>
                                </div>
                                <div
                                    class="col p-2 bg-gray-edoor-10 rounded-lg shadow-charge-total border border-gray-edoor-100 h-full">
                                    <div class="text-500 uppercase text-sm">Total Credit</div>
                                    <div class="text-xl line-height-2 font-semibold">
                                        <CurrencyFormat :value="doc?.total_credit" isCurrency></CurrencyFormat>
                                    </div>
                                </div>
                                <div class="col p-2 bg-green-50 rounded-lg shadow-charge-total border border-green-edoor">
                                    <div class="text-500 uppercase text-sm">Balance</div>


                                    <div class="text-xl line-height-2 font-semibold">
                                        <CurrencyFormat :value="doc?.balance" isCurrency></CurrencyFormat>
                                    </div>
                                </div>
                            </div>
                        </div>

                    </div>


                    <div class="col-12 p-0">
                        <div
                            class="line-height-1 -mt-2 text-right flex p-0 flex-col justify-center gap-2 w-full text-sm white-space-nowrap overflow-hidden text-overflow-ellipsis">
                            <div>
                                <span class="italic">Created by: </span>
                                <span class="text-500 font-italic">
                                    {{ doc?.owner?.split("@")[0] }}
                                    <ComTimeago :date="doc?.creation" />

                                </span>
                            </div>
                            <div>
                                <span class="italic ms-2"> Last Modified: </span>
                                <span class="text-500 font-italic">
                                    {{ doc?.modified_by?.split("@")[0] }}
                                    <ComTimeago :date="doc?.modified" />

                                </span>
                            </div>
                        </div>
                        <hr class="mt-3 mb-2">
                    </div>
                    <div class="py-2 mt-1 border-1 bg-slate-200 font-medium text-start ps-3 w-full">
                        <div class="flex gap-2 align-items-center">
                            Deposit Ledger Detail - {{ doc.name }}
                            <ComOpenStatus :status="doc.status" />
                            <div v-tippy="'Master Folio'" v-if="doc.is_master"
                                class="flex justify-center items-center p-2 rounded-lg text-white p-1px bg-purple-100 ">
                                <ComIcon style="height: 12px;" icon="iconCrown" />
                            </div>
                        </div>
                    </div>
                    <ComFolioTransactionCreditDebitStyle v-if="showCreditDebitStyle" :folio="doc" doctype="Deposit Ledger"
                        :showCheckbox="false" />
                    <ComFolioTransactionSimpleStyle v-else :folio="doc" doctype="Deposit Ledger" :showCheckbox="false" />



                </div>

            </TabPanel>
            <TabPanel>
                <template #header>
                    <span class="me-2">Document</span>
                    <Badge :value="totalDocument"></Badge>
                </template>
                <ComDocument v-if="doc" @updateCount="onUpdateFileCount" doctype="Deposit Ledger"
                    :doctypes="['Deposit Ledger', 'Folio Transaction']" :attacheds="relatedIds" :docname="doc?.name" />
            </TabPanel>
        </TabView>

        <div class="col-12">
            <ComCommentAndNotice v-if="doc" doctype="Deposit Ledger" :docname="name"
                :filters="['custom_folio_number', '=', doc.name]" />
        </div>
        <template #footer-left>
            <Button class="border-none" @click="onAuditTrail" label="Audit Trail" icon="pi pi-history" />
        </template>
    </ComDialogContent>
</template>
<script setup>

import { ref, onMounted, inject, getApi, useDialog, computed, onUnmounted } from '@/plugin'
import ComFolioTransactionCreditDebitStyle from "@/views/reservation/components/folios/ComFolioTransactionCreditDebitStyle.vue"
import ComFolioTransactionSimpleStyle from "@/views/reservation/components/folios/ComFolioTransactionSimpleStyle.vue"
import ComDepositLedgerAction from "@/views/deposit_ledger/components/ComDepositLedgerAction.vue"
import ComAuditTrail from '@/components/layout/components/ComAuditTrail.vue';
import ComCommentAndNotice from '@/components/form/ComCommentAndNotice.vue';


const dialog = useDialog()
const showCreditDebitStyle = ref(window.setting.folio_transaction_style_credit_debit)
const moment = inject("$moment")
const name = ref()
const doc = ref()
const relatedIds = ref()


const totalDocument = ref(0)



const dialogRef = inject("dialogRef");

const newDoc = computed(() => {
    return {
        transaction_type: "Deposit Ledger",
        transaction_number: doc.value?.name,
        property: window.property_name
    }
})

const loading = ref(false)

function onUpdateFileCount(n) {
    totalDocument.value = n
}

function onOk() {
    dialogRef.value.close(dov.value)

}

function onViewCustomerDetail(g) {
    window.postMessage("view_guest_detail|" + g)
}
function onAuditTrail() {
    const dialogRef = dialog.open(ComAuditTrail, {
        data: {
            doctype: 'Deposit Ledger',
            docname: doc?.value.name,
            referenceTypes: [{ doctype: 'Deposit Ledger', label: 'Deposit Ledger' },
            { doctype: 'Folio Transaction', label: 'Folio Transaction' },
            ],
            filter_key: 'custom_folio_number'
        },

        props: {
            header: 'Audit Trail for Deposit Ledger Detail',
            style: {
                width: '80vw',
            },
            modal: true,
            maximizable: true,
            closeOnEscape: false,
            position: 'top',
        },
        onClose: (options) => {
            // Handle dialog closure here
        },
    });
}
function getData() {
    loading.value = true
    getApi("utils.get_deposit_ledger_detail", {
        name: name.value
    }).then(r => {
        doc.value = r.message.deposit_ledger
        relatedIds.value = r.message.related_ids
        loading.value = false
    }).catch(err => {
        if (err.httpStatus == 404) {
            dialogRef.value.close()
        }
        loading.value = false
    })
}
const onClose = () => {
    dialogRef.value.close();
}

const actionRefreshData = async function (e) {
    if (e.isTrusted && typeof (e.data) != 'string') {
        if(e.data.action=="ComDepositLedgerDetail"){
            setTimeout(()=>{
                getData()
            },1000*3)
            
        }
    };
}

onMounted(() => {
    name.value = dialogRef.value.data.name;
    getData()
    window.addEventListener('message', actionRefreshData, false)
})

onUnmounted(() => {
    window.removeEventListener('message', actionRefreshData, false)
})



</script>
<style lang="">
    
</style>