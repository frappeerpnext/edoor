<template>
    <ComDialogContent :hideButtonOK="true" @onClose="onClose" :hideIcon="false" :loading="loading">
        <div v-if="doc">
            <ComFolioAction :folio="doc" />
            <table class="mb-4">
                <tr>
                    <th class="py-2 mt-1 border-1 bg-slate-200 font-medium text-start ps-3" colspan="2">
                        Reservation
                        <span class="ms-2 px-2 rounded-lg me-2 text-white p-1px"
                            :style="{ backgroundColor: doc.reservation_status_color }">{{ doc.reservation_status }}</span>
                    </th>
                </tr>
                <ComStayInfoNoBox label="Guest">
                    <span @click="onViewCustomerDetail(doc.guest)" class="-ml-2 text-right link_line_action1">
                        {{ doc.guest }} - {{ doc.guest_name }}
                    </span>
                </ComStayInfoNoBox>
                <ComStayInfoNoBox label="Business Source">
                    <span class="font-semibold text-right">
                        {{ doc.business_source }}
                    </span>
                </ComStayInfoNoBox>
                <ComStayInfoNoBox label="reservation">
                    <span @click="onViewReservationDetail(doc.reservation)" class="-ml-2 text-right link_line_action1">
                        {{ doc.reservation }}
                    </span>
                </ComStayInfoNoBox>
                <ComStayInfoNoBox label="Reservation Stay">
                    <span @click="onViewReservationStayDetail(doc.reservation_stay)"
                        class="-ml-2 text-right link_line_action1">
                        {{ doc.reservation_stay }}
                    </span>
                </ComStayInfoNoBox>
                <ComStayInfoNoBox label="Room">
                    <span class="font-semibold text-right">
                        {{ doc.rooms + '/' + doc.room_types_alias }}
                    </span>
                </ComStayInfoNoBox>
            </table>

            <div class="col-12 p-0">
                <div
                    class="line-height-1 -mt-2 text-right flex p-0 flex-col justify-center gap-2 w-full text-sm white-space-nowrap overflow-hidden text-overflow-ellipsis">
                    <div >
                        <span class="italic">Created by: </span>
                        <span class="text-500 font-italic"> 
                            {{ doc?.owner?.split("@")[0] }}
                            <ComTimeago :date="doc?.owner?.creation" />

                        </span>
                    </div>
                    <div>
                        <span class="italic ms-2"> Last Modified: </span>
                        <span class="text-500 font-italic"> 
                            {{ doc?.modified_by?.split("@")[0] }}
                            <ComTimeago :date="doc?.modified_by?.modified" />

                        </span>
                    </div>
                </div>
                <hr class="mt-3 mb-2">
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
        <template #footer-left>
            <Button class="border-none" @click="onAuditTrail" label="Audit Trail" icon="pi pi-history" />
        </template>
    </ComDialogContent>
</template>
<script setup>

import { ref, onMounted, inject, getDoc, useDialog } from '@/plugin'
import ComFolioTransactionCreditDebitStyle from "@/views/reservation/components/folios/ComFolioTransactionCreditDebitStyle.vue"
import ComFolioTransactionSimpleStyle from "@/views/reservation/components/folios/ComFolioTransactionSimpleStyle.vue"
import ComFolioAction from "@/views/reservation/components/folios/ComFolioAction.vue"
import ComAuditTrail from '@/components/layout/components/ComAuditTrail.vue';
const dialog = useDialog()
const showCreditDebitStyle = ref(window.setting.folio_transaction_style_credit_debit)
const gv = inject('$gv');
const name = ref()
const doc = ref()

const dialogRef = inject("dialogRef");


const loading = ref(false)



function onOk() {
    dialogRef.value.close(dov.value)

}
function onAuditTrail() {
    const dialogRef = dialog.open(ComAuditTrail, {
        data: {
            doctype: 'Reservation Folio',
            docname: doc?.value.name,
            referenceTypes: [{ doctype: 'Reservation Folio', label: 'Reservation Folio' },
            { doctype: 'Folio Transaction', label: 'Folio Transaction' },
            ],
            docnames: [doc?.value.name],
        },

        props: {
            header: 'Audit Trail for Folio Detail',
            style: {
                width: '75vw',
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
        onClose: (options) => {
            // Handle dialog closure here
        },
    });
}
function getData() {
    loading.value = true
    getDoc("Reservation Folio", name.value).then(r => {
        doc.value = r
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