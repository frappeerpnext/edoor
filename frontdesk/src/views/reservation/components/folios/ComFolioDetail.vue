<template>
    <ComDialogContent :hideButtonOK="true" @onClose="onClose" :hideIcon="false" :loading="loading">
        <TabView>
            <TabPanel header="Deposit Ledger Information">
                <div v-if="doc" class="mt-2">
                    <ComFolioAction @onRefresh="onRefresh" :folio="doc"
                        :accountGroups="accountGroups?.filter(r => r.show_in_guest_folio == 1)"
                        :accountCodeFilter="{ is_guest_folio_account: 1 }" />
                    <div class="grid">
                        <div class="col">
                            <table class="mb-4">
                                <tr>
                                    <th class="py-2 mt-1 border-1 bg-slate-200 font-medium text-start ps-3" colspan="2">
                                        Reservation #
                                        <span class="ms-2 px-2 rounded-lg me-2 text-white p-1px"
                                            :style="{ backgroundColor: doc.reservation_status_color }">{{
                                                doc.reservation_status
                                            }}</span>
                                    </th>
                                </tr>
                                <ComStayInfoNoBox label="Guest">
                                    <span @click="onViewCustomerDetail(doc.guest)"
                                        class="-ml-2 text-right link_line_action1">
                                        {{ doc.guest }} - {{ doc.guest_name }}
                                    </span>
                                </ComStayInfoNoBox>
                                <ComStayInfoNoBox label="Source">
                                    <span class="font-semibold text-right">
                                        {{ doc.business_source }}
                                    </span>
                                </ComStayInfoNoBox>
                                <ComStayInfoNoBox label="Reservation #">
                                    <span @click="onViewReservationDetail(doc.reservation)"
                                        class="-ml-2 text-right link_line_action1">
                                        {{ doc.reservation }}
                                    </span>
                                </ComStayInfoNoBox>
                                <ComStayInfoNoBox label="Res Stay #">
                                    <span @click="onViewReservationStayDetail(doc.reservation_stay)"
                                        class="-ml-2 text-right link_line_action1">
                                        {{ doc.reservation_stay }}
                                    </span>
                                </ComStayInfoNoBox>
                                <ComStayInfoNoBox label="Room(s)">
                                    <span class="font-semibold text-right">
                                        {{ doc.rooms + '/' + doc.room_types_alias }}
                                    </span>
                                </ComStayInfoNoBox>

                            </table>
                        </div>
                        <div class="col">
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
                                    <div
                                        class="col p-2 bg-green-50 rounded-lg shadow-charge-total border border-green-edoor">
                                        <div class="text-500 uppercase text-sm">Balance</div>


                                        <div class="text-xl line-height-2 font-semibold">
                                            <CurrencyFormat :value="(doc?.total_debit - doc?.total_credit)" isCurrency></CurrencyFormat>
                                        </div>
                                    </div>
                                </div>

                            </div>
                        </div>
                    </div>


                    <div class="py-2 mt-1 border-1 bg-slate-200 font-medium text-start ps-3 w-full">
                        <div class="flex gap-2 align-items-center">
                            Folio Detail - {{ doc.name }} <span class="ms-2 px-2 rounded-lg  text-white p-1px"
                                :class="doc.status == 'Open' ? 'bg-green-500' : 'surface-500'">{{ doc.status }}</span>
                            <div v-tippy="'Master Folio'" v-if="doc.is_master"
                                class="flex justify-center items-center p-2  rounded-lg text-white p-1px bg-purple-100 ">
                                <ComIcon style="height: 12px;" icon="iconCrown" />
                            </div>
                        </div>
                    </div>
                    <ComFolioTransactionCreditDebitStyle v-if="showCreditDebitStyle" :folio="doc" />
                    <ComFolioTransactionSimpleStyle v-else :folio="doc" />
                </div>
            </TabPanel>
            <TabPanel>
                <template #header>
                    <span class="me-2">Document</span>
                    <Badge :value="totalDocument"></Badge>
                </template>
                <ComDocument v-if="doc" @updateCount="onUpdateFileCount" doctype="Reservation Folio"
                    :doctypes="['Reservation Folio', 'Folio Transaction']" :attacheds="relatedIds" :docname="doc?.name" />
            </TabPanel>
        </TabView>

        <div class="col-12">
            <ComCommentAndNotice v-if="doc" doctype="Reservation Folio" :docname="name"
                :filters="['custom_folio_number', '=', doc.name]" />
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
        <template #footer-left>
            <Button class="border-none" @click="onAuditTrail" label="Audit Trail" icon="pi pi-history" />
        </template>

    </ComDialogContent>
</template>
<script setup>

import { ref, onMounted, inject, getApi, useDialog } from '@/plugin'
import ComFolioTransactionCreditDebitStyle from "@/views/reservation/components/folios/ComFolioTransactionCreditDebitStyle.vue"
import ComFolioTransactionSimpleStyle from "@/views/reservation/components/folios/ComFolioTransactionSimpleStyle.vue"
import ComFolioAction from "@/views/reservation/components/folios/ComFolioAction.vue"
import ComAuditTrail from '@/components/layout/components/ComAuditTrail.vue';
import ComCommentAndNotice from '@/components/form/ComCommentAndNotice.vue';

const dialog = useDialog()
const showCreditDebitStyle = ref(window.setting.folio_transaction_style_credit_debit)

const name = ref()
const doc = ref()
const accountGroups = ref(window.setting.account_group)

const dialogRef = inject("dialogRef");


const loading = ref(false)
const relatedIds = ref()
const totalDocument = ref(0)

function onRefresh() {
    getData()
}

function onUpdateFileCount(n) {
    totalDocument.value = n
}

function onOk() {
    dialogRef.value.close(dov.value)

}
function onAuditTrail() {
    const dialogRef = dialog.open(ComAuditTrail, {
        data: {
            doctype: 'Reservation Folio',
            docname: doc?.value.name,
            referenceTypes: [
                { doctype: 'Reservation Folio', label: 'Reservation Folio' },
                { doctype: 'Folio Transaction', label: 'Folio Transaction' },
            ],
            filter_key: "custom_folio_number"
        },

        props: {
            header: 'Audit Trail for Folio Detail',
            style: {
                width: '80vw',
            },
            breakpoints: {
                '960px': '100vw',
                '640px': '100vw',
            },
            modal: true,
            maximizable: true,
            closeOnEscape: false,
            position: 'top',
        },

    });
}
function getData() {
    loading.value = true
    getApi("utils.get_reservation_folio_detail", {
        name: name.value
    }).then(r => {
        doc.value = r.message.reservation_folio
        relatedIds.value = r.message.related_ids
        loading.value = false
    }).catch(err => {
        loading.value = false
    })
}

const onClose = () => {
    dialogRef.value.close();
}

function onViewCustomerDetail(name) {
    window.postMessage('view_guest_detail|' + name, '*')
}

function onViewReservationStayDetail(rs) {
    window.postMessage('view_reservation_stay_detail|' + rs, '*')
}

function onViewReservationDetail(rs) {
    window.postMessage('view_reservation_detail|' + rs, '*')
}

onMounted(() => {
    name.value = dialogRef.value.data.name;
    getData()

})


</script>
<style lang="">
    
</style>