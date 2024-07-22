<template>
    <ComDialogContent hideButtonOK :hideButtonClose="true" @onClose="onClose" :isDialog="true" :loading="loading">
        <TabView>
            <TabPanel header="Cashier Shift Information">
                <Message v-if="!doc.is_edoor_shift">
                    {{$t('This shift is an ePOS shift. Please ask ePOS user to close their shift.')}}
                    </Message>
                <div class="grid mt-2">
                    <div class="col">
                        <ComReservationStayPanel  title="Shift Information">
                            <template #content>
                                <div class="shift_status">
                                    <div class="flex align-items-center">
                                    <ComOpenStatus :status="doc.is_closed == 1 ? $t('Closed') : $t('Open')" />
                                   
                                    <span  v-if="doc.is_edoor_shift" class="ms-2 border-round-lg py-1 line-height-2 px-3 text-white font-medium bg-blue-700 me-1"> {{ $t('eDoor') }} </span>
                                   <span v-else class="ms-3 border-round-lg line-height-2 py-1 px-3 text-white font-medium bg-red-400 me-1"> {{ $t('ePOS') }} </span>
                                   
                                    
                                    </div>
                                </div>
                                <div class="grid">
                                <div :class="!doc.is_edoor_shift ? 'col-6' : 'col-12' ">
                                <div class="bg-slate-200 p-2 font-medium text-center border-left-2">
                                    {{ $t('Opening Shift') }}
                                    
                                </div>
                                <table>
                                    <ComStayInfoNoBox label="Cashier Shift #" v-if="doc.name" :value="doc.name" />
                                    <ComStayInfoNoBox label="Posting Date" v-if="doc.name"
                                        :value="moment(doc.posting_date).format('DD-MM-YYYY')" />
                                    <ComStayInfoNoBox label="Shift Name" v-if="doc.shift_name" :value="doc.shift_name" />
                                    <ComStayInfoNoBox label="Opened By"  >
                                        <div class="white-space-nowrap font-semibold text-right -ml-2">
                                             {{ doc?.owner?.split("@")[0] }} - 
                                <ComTimeago :date="doc.creation" />  
                                        </div>
                                      
                                    </ComStayInfoNoBox>
                                </table>
                                <div class="w-full h-10rem mb-4 mt-2">
                                    <label> {{ $t('Opening Note') }} </label>
                                    <div class="w-full p-3 h-10rem rounded-lg whitespace-pre-wrap break-words bg-slate-200"
                                        v-html="doc.opened_note">
                                    </div>
                                </div>
                            </div>
                            <div :class="!doc.is_edoor_shift ? 'col-6' : 'col-12' ">
                                <template v-if="doc.is_closed">
                                    <div :class="!doc.is_edoor_shift ? '' : 'mt-2' ">
                                    <div :class="!doc.is_edoor_shift ? '' : 'mt-4' " class="bg-slate-200 p-2 font-medium text-center border-left-2">
                                        {{ $t('Closing Shift') }}  
                                    </div>
                                    <table>
                                        <ComStayInfoNoBox label="Closing Date"
                                            :value="moment(doc.closed_date).format('DD-MM-YYYY')" />
                                            <ComStayInfoNoBox label="Closed By"  >
                                        <div class="white-space-nowrap font-semibold text-right -ml-2">
                                            {{ doc?.modified_by?.split("@")[0] }} - 
                                    <ComTimeago :date="doc.closed_date" /> 
                                        </div>
                                      
                                    </ComStayInfoNoBox>
                                        </table>
                                    <div class="w-full h-10rem mb-4 mt-2">
                                        <label> {{ $t('Closing Note') }} </label>
                                        <div class="w-full p-3 h-10rem rounded-lg whitespace-pre-wrap break-words bg-slate-200"
                                            v-html="doc.closed_note">
                                        </div>
                                    </div>
                                </div>
                                </template>
</div>
</div>
                            </template>
                        </ComReservationStayPanel>
                        <div v-if="!isMobile" class="mt-3">
                            <ComReservationStayPanel class="bg-white">
                                <template #content>
                                    <ComCommentAndNotice v-if="doc?.name" doctype="Cashier Shift" :docname="doc?.name"
                                        :filters="['custom_cashier_shift','=', doc?.name]" />
                                </template>
                            </ComReservationStayPanel>
                        </div>


                    </div>
                    <div v-if="doc.is_edoor_shift" class="col-12 md:col-6">
                        <ComReservationStayPanel  title="Payment Information">
                            <template #content>
                                <div class="flex w-full gap-3">
                                    <div class="bg-white flex flex-column rounded-lg grow p-2 shadow-charge-total border">
                                        <span class="text-500 uppercase text-sm text-end"> {{ $t('Open Cash Float') }} </span><span
                                            class="text-xl line-height-2 font-semibold text-end">
                                            <span>
                                                <CurrencyFormat :value="doc.total_opening_amount" />
                                            </span></span>
                                    </div>
                                    <div class="bg-white flex flex-column rounded-lg grow p-2 shadow-charge-total border">
                                        <span class="text-500 uppercase text-sm text-end"> {{ $t('Cash Debit') }} </span><span
                                            class="text-xl line-height-2 font-semibold text-end">
                                            <span>
                                                <CurrencyFormat :value="summary?.cash_debit" />
                                            </span></span></div>
                                    <div class="bg-white flex flex-column rounded-lg grow p-2 shadow-charge-total border">
                                        <span class="text-500 uppercase text-sm text-end"> {{ $t('Cash Credit') }} </span><span
                                            class="text-xl line-height-2 font-semibold text-end">
                                            <span>
                                                <CurrencyFormat :value="summary?.cash_credit" />
                                            </span></span>
                                    </div>

                                    <div
                                        class="bg-green-50 border-green-edoor flex flex-column rounded-lg grow p-2 shadow-charge-total border">
                                        <span class="text-500 uppercase text-sm text-end"> {{ $t('Cash In Hand') }} </span><span
                                            class="text-xl line-height-2 font-semibold text-end">
                                            <span>
                                                <CurrencyFormat :value="summary?.cash_in_hand" />
                                            </span></span>
                                    </div>
                                </div>
                                <div class="bg-slate-200 p-2 mt-3 font-medium text-center border-left-2">
                                    {{ $t('Payment Transaction Summary') }} 
                                </div>
                                <table class="w-full border-1 bg-white">
                                    <ComPlaceholder text="No Payment Transaction"  :is-not-empty="summary?.payment_transaction_summary.length > 0">
                                    <tr class="bg-white">
                                        <td class="w-auto border-1 p-2"> {{ $t('Account Code') }}  </td>
                                        <td class="w-auto border-1 p-2 text-right"> {{ $t('Debit') }} </td>
                                        <td class="w-auto border-1 p-2 text-right" > {{ $t('Credit') }}  </td>
                                        <td class="w-auto border-1 p-2 text-right"> {{ $t('Total') }}  </td>
                                    </tr>
                                   
                                    <tr class="bg-white" v-for="(p, index) in summary?.payment_transaction_summary" :key="index">
                                        <td class="border-1 p-2"> {{ p.account_code }}  - {{ p.account_name }} </td>
                                        <td class="border-1 p-2 text-right">
                                            <CurrencyFormat :value="p.total_debit" />
                                        </td>
                                        <td class="border-1 p-2 text-right">
                                            <CurrencyFormat :value="p.total_credit" />
                                        </td>
                                        <td class="border-1 p-2 text-right">
                                            <CurrencyFormat :value="p.total_credit - p.total_debit" />
                                        </td>
                                    </tr>
                                    

                                    <tr class="total-cash-count bg-white">
                                        <td class="border-1 p-2"> {{ $t('Total') }} </td>
                                        <td class="border-1 p-2 text-right">
                                            <CurrencyFormat :value="summary?.payment_transaction_summary?.reduce((n, d) => n + (d.total_debit || 0), 0)"/>
                                        </td>
                                        
                                        <td class="border-1 p-2 text-right">
                                            <CurrencyFormat :value="summary?.payment_transaction_summary?.reduce((n, d) => n + (d.total_credit || 0), 0)"/>
                                        </td>
                                        
                                        <td class="border-1 p-2 text-right">
                                            <CurrencyFormat :value="summary?.payment_transaction_summary?.reduce((n, d) => n + ((d.total_credit || 0 ) - (d.total_debit || 0)), 0)"/>
                                        </td>



                                    </tr>
                                </ComPlaceholder>
                                </table>

                                <div v-if="doc.is_closed">
                                
                                <div class="bg-slate-200 p-2 mt-3 font-medium text-center border-left-2">
                                  {{ $t('Closing Summary') }}  
                                </div>
                                <div class="w-full overflow-auto">
                                <table class="w-full" >
                                    <tr class="bg-white">
                                        <td class="w-auto border-1 p-2 white-space-nowrap"> {{ $t('Payment Type') }}  </td>
                                        <td class="w-auto border-1 p-2 text-right"> {{ $t('Opening') }} </td>
                                        <td class="w-auto border-1 p-2 text-right"> {{ $t('Expected') }} </td>
                                        <td class="w-auto border-1 p-2 text-right"> {{ $t('Actual') }}  </td>
                                        <td class="w-auto border-1 p-2 text-right"> {{ $t('Difference') }} </td>
                                    </tr>
                                    <tr class="bg-white" v-for="(p, index) in doc.cash_float" :key="index">
                                        <td class="border-1 p-2"> {{  $t(p.payment_method)  }}</td>
                                        <td class="border-1 p-2 text-right">
                                            <CurrencyFormat :value="p.input_amount" :currency="{precision:p.currency_precision, pos_currency_format:p.pos_currency_format}" />
                                        </td>
                                        <td class="border-1 p-2 text-right">
                                            <CurrencyFormat :value="p.input_system_close_amount" :currency="{precision:p.currency_precision, pos_:p.pos_currency_format}"/>
                                        </td>
                                        <td class="border-1 p-2 text-right">
                                            <CurrencyFormat :value="p.input_close_amount" :currency="{precision:p.currency_precision, pos_currency_format:p.pos_currency_format}"/>
                                        </td>
                                        
                                        <td class="border-1 p-2 text-right">
                                            <CurrencyFormat :value="p.input_different_amount" :currency="{precision:p.currency_precision, pos_currency_format:p.pos_currency_format}"/>
                                        </td>

                                    </tr>
                                    <tr  class="total-cash-count bg-white">
                                        <td class="border-1 p-2"> {{ $t('Total') }} </td>
                                        <td class="border-1 p-2 text-right">
                                            <CurrencyFormat :value="doc.cash_float?.reduce((n, d) => n + (d.opening_amount || 0), 0)"/>
                                        </td>
                                        
                                        <td class="border-1 p-2 text-right">
                                            <CurrencyFormat :value="doc.cash_float?.reduce((n, d) => n + (d.system_close_amount || 0), 0)"/>
                                        </td>
                                        <td class="border-1 p-2 text-right">
                                            <CurrencyFormat :value="doc.cash_float?.reduce((n, d) => n + (d.close_amount || 0), 0)"/>
                                        </td>
                                        <td class="border-1 p-2 text-right">
                                            <CurrencyFormat :value="doc.cash_float?.reduce((n, d) => n + (d.different_amount || 0), 0)"/>
                                        </td>
                                        
                                    </tr>

                                </table>
                                </div>
                            </div>
                            </template>
                        </ComReservationStayPanel>
                        <div class="mt-3"></div>
                        <ComReservationStayPanel v-if="(doc?.cash_count?.length > 0) && doc.is_closed" title="Cash Count">
                            <template #content>


                                <table class="w-full">
 <tr class="border-1 p-1 bg-white" >
                                            <td class="w-auto  p-2"> {{ $t('Note Type') }}  </td>
                                            <td class="w-auto  p-2 text-center"> {{ $t('Total Note') }}  </td>
                                            <td class="w-auto p-2 text-right"> {{ $t('Total Amount') }} </td>
                                        </tr>
                                    <template v-for="(c, index) in [...new Set(doc?.cash_count?.map(r => r.currency))]"
                                        :key="index">
                                        <tr>
                                            <td colspan="3" class="p-2 font-bold" >{{c}}</td>
                                        </tr>
                                            
                                       
                                        <tr  v-for="(p, index) in doc?.cash_count?.filter(r => r.currency == c)" 
                                            :key="index">
                                            <td class="border-y-1 py-2 pl-6">
                                                {{ $t(p.label) }}
                                            </td>
                                            <td class="border-y-1 text-center p-2 ">
                                                {{ p.total_note }}
                                            </td>
                                            <td class="border-y-1 text-right p-2">
                                                <CurrencyFormat :value="p.total_amount" :currency="{precision:p.currency_precision, pos_currency_format:p.pos_currency_format}" />
                                            </td>
                                        </tr>
                                        <tr class="total-cash-count" >
                                            <td class="p-2">  {{ $t(c + ' Total') }}  </td>
                                            <td class="text-center p-2"> {{ doc?.cash_count?.filter(r => r.currency ==
                                                c).reduce((n, d) => n + (d.total_note || 0), 0) }} </td>
                                            <td class="text-end p-2 ">
                                                <CurrencyFormat
                                                    :value="doc?.cash_count?.filter(r => r.currency == c).reduce((n, d) => n + (d.total_amount || 0), 0)"
                                                    :currency="{precision:doc?.cash_count?.filter(r => r.currency == c)[0].currency_precision, pos_currency_format:doc?.cash_count?.filter(r => r.currency == c)[0].pos_currency_format}  " />
                                            </td>
                                        </tr>

                                    </template>
                                    <tr class=" total-cash-count">
                                        <td  class="w-auto  p-2 "> {{ $t('Grand Total') }} </td>
                                        <td class="p-2 w-auto text-center">
                                            {{ doc?.cash_count?.reduce((n, d) => n + (d.total_note || 0), 0) }}
                                        </td>
                                        <td class="p-2 w-auto text-end">
                                            <CurrencyFormat :value="doc?.cash_count?.reduce((n, d) => n + (d.total_base_currency_amount || 0), 0)" />
                                        </td>
                                    </tr>
                                </table>
                            </template>

                        </ComReservationStayPanel>
                    </div>
<div>
    <div v-if="isMobile" class="mt-3">
                            <ComReservationStayPanel class="bg-white">
                                <template #content>
                                    <ComCommentAndNotice v-if="doc?.name" doctype="Cashier Shift" :docname="doc?.name"
                                        :filters="['custom_cashier_shift','=', doc?.name]" />
                                </template>
                            </ComReservationStayPanel>
                        </div>
</div>
                </div>

            </TabPanel>
            <TabPanel>
                <template #header>
                    <span class="me-2"> {{ $t('Document') }} </span>
                    <Badge :value="totalDocument"></Badge>
                </template>
                <div class="min-h-dialog">
                <ComDocument v-if="doc" @updateCount="onUpdateFileCount" doctype="Cashier Shift"
                    :doctypes="['Cashier Shift']" :attacheds="[doc?.name]" :docname="doc?.name" />
                </div>
            </TabPanel>
        </TabView>

        <template v-if="doc.is_edoor_shift" #footer-left>

            <SplitButton @click="onPrintFolioTransactionSummary('eDoor Cashier Shift Transaction Summary Report')"
                 label="Print" icon="pi pi-print" :model="print_menus" />
            <Button class="border-none" @click="onAuditTrail" :label=" $t('Audit Trail') " icon="pi pi-history" />
        </template>
        <template  #footer-right>
            <Button class="border-none" v-if="doc.is_closed == 0 && doc.is_edoor_shift==1" @click="onEditCashierShift"> {{ $t('Edit') }} </Button>
            <Button class="border-none" v-if="doc.is_closed == 0 && doc.is_edoor_shift==1" @click="onOpenCloseShift"> {{ $t('Close Shift') }} </Button>
            <Button class="border-none" v-else-if="doc.is_closed == 0 && doc.is_edoor_shift==0" @click="onOpenCloseShift"> {{ $t('Close') }} </Button>
        </template>
    </ComDialogContent>
</template>
<script setup>
import { ref, getApi, onMounted, inject, getDoc, useDialog, useToast, computed } from "@/plugin"
import OpenShift from "@/views/cashier_shift/OpenShift.vue"
import ComCommentAndNotice from '@/components/form/ComCommentAndNotice.vue';
import ComReservationStayPanel from '@/views/reservation/components/ComReservationStayPanel.vue';
import ComIFrameModal from "@/components/ComIFrameModal.vue";
import ComAuditTrail from '@/components/layout/components/ComAuditTrail.vue';
import ComCloseShift from '@/views/cashier_shift/ComCloseShift.vue';
import {i18n} from '@/i18n';
const { t: $t } = i18n.global;
const toast = useToast()
const dialogRef = inject("dialogRef")
const moment = inject("$moment")
const mainCurrency = ref(window.setting.currency) 
const isMobile = ref(window.isMobile)
const doc = ref({})
const dialog = useDialog();
const loading = ref(false)
const print_menus = ref([])
const gv = inject("$gv")
const totalDocument = ref(0)
const summary = ref()


function onUpdateFileCount(n) {
    totalDocument.value = n
}


//Cashier Summary Transaction
print_menus.value.push({
    label: "Cashier Shift Transaction Summary",
    icon: 'pi pi-print',
    command: () => {
        onPrintFolioTransactionSummary("eDoor Cashier Shift Transaction Summary Report")

    }
})



print_menus.value.push({
    label: "Cashier Shift Transaction Detail",
    icon: 'pi pi-print',
    command: () => {
        onPrintFolioTransactionSummary("eDoor Cashier Shift Transaction Detail Report", "Cashier Shift Transaction Detail - " + doc.value.name)

    }
})

print_menus.value.push({
    label: "Cashier Shift Audit Trail Report",
    icon: 'pi pi-print',
    command: () => {
        dialog.open(ComIFrameModal, {
            data: {
                "doctype": "Cashier%20Shift",
                name: doc.value.name,
                report_name: "eDoor Cashier Shift Audit Trail",
            },
            props: {
                header: "Cashier Shift Audit Trail - " + doc.value.name,
                style: {
                    width: '80vw',
                },
                position: "top",
                modal: true,
                maximizable: true,
                breakpoints:{
                '960px': '80vw',
                '640px': '100vw'
            },
            },
        });

    }
})

function onPrintFolioTransactionSummary(format_name = 'eDoor Cashier Shift Transaction Summary Report', title = "") {
    dialog.open(ComIFrameModal, {
        data: {
            "doctype": "Cashier%20Shift",
            name: doc.value.name,
            report_name: format_name,
            filter_options: ["show_account_code", "group_by_ledger_type", "show_cash_count", "show_cash_float", "select_user","show_package_breakdown"],
        },
        props: {
            header: title == "" ? "Cashier Shift Transaction Summary - " + doc.value.name : title,
            style: {
                width: '80vw',
            },
            position: "top",
            modal: true,
            maximizable: true,
            breakpoints:{
                '960px': '80vw',
                '640px': '100vw'
            },
        },
    });
}


function onEditCashierShift() {

    dialog.open(OpenShift, {
        data: {
            name: window.working_day.cashier_shift.name
        },
        props: {
            header: 'Open Shift',
            style: {
                width: '40vw',
            },
            modal: true,
            maximizable: true,
            closeOnEscape: false,
            position: 'top',
            breakpoints:{
                '960px': '40vw',
                '640px': '100vw'
            },
        },
        onClose: (options) => {

            const data = options.data;
            if (data != undefined) {
                getData()
            }
        }

    });
}
function onOpenCloseShift() {

    if (doc.value.is_edoor_shift == 0) {
        dialogRef.value.close()
    } else {
        dialog.open(ComCloseShift, {
        data:{
            name: doc.value.name,
            is_run_night_audit: dialogRef.value.data?.is_run_night_audit || 0

        },
        props: {
            header:"Close Shift",
            style: {
                width: '80vw',
            },
            position:"top",
            modal: true,
            maximizable: true,
            closeOnEscape: false,
            breakpoints:{
                '960px': '80vw',
                '640px': '100vw'
            },
        },
        onClose: (options) => {
            if(options.data){
                getData()
            }
        },
       
    });
    }
}
function getSummary() {
    if (doc.value?.name) {
        getApi("utils.get_cashier_shift_summary", {
            name: doc.value?.name,
            property: window.property_name
        }).then((result) => {
            summary.value = result.message


        })
    }
}
function getData() {
    loading.value = true
    getDoc("Cashier Shift", dialogRef.value.data.name).then((result) => {
        doc.value = result
        getSummary()
        loading.value = false

    }).catch(err => {
        loading.value = false

    })
}

onMounted(() => {
    getData()

    if(window.isMobile){
        let elem = document.querySelectorAll(".p-dialog");
        if (elem){
            elem = elem[elem.length-1]
            elem?.classList.add("p-dialog-maximized"); // adds the maximized class
        }
    }

})

function onAuditTrail() {
    const dialogRef = dialog.open(ComAuditTrail, {
        data: {
            doctype: 'Cashier Shift',
            docname: doc?.value.name,
            referenceTypes:[
            { doctype: 'Cashier Shift', label: 'Cashier Shift' },
                { doctype: 'Reservation', label: 'Reservation' },
                { doctype: 'Reservation Stay', label: 'Reservation stay' },
                { doctype: 'Reservation Room Rate', label: 'Room Rate' },
                { doctype: 'Customer', label: 'Guest' },
                { doctype: 'Reservation Folio', label: 'Reservation Folio' },
                { doctype: 'Desk Folio', label: 'Desk Folio' },
                { doctype: 'City Ledger', label: 'City Ledger' },
                { doctype: 'Deposit Ledger', label: 'Deposit Ledger' },
                { doctype: 'Payable Ledger', label: 'Payable Ledger' },
                { doctype: 'Folio Transaction', label: 'Folio Transaction' }
            ],
            filter_key:'custom_cashier_shift'
        },

        props: {
            header: 'Audit Trail for Cashier Shift Detail',
            style: {
                width: '75vw',
            },
            modal: true,
            maximizable: true,
            closeOnEscape: false,
            position: 'top',
            breakpoints:{
                '960px': '75vw',
                '640px': '100vw'
            },
        },
        onClose: (options) => {
            // Handle dialog closure here
        },
    });
}

</script>