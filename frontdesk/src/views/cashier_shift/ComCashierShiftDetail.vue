<template>
    <ComDialogContent hideButtonOK :hideButtonClose="true" @onClose="onClose" :isDialog="true" :loading="loading">
        <TabView>
            <TabPanel header="Cashier Shift Information">
                <div class="grid mt-2">
                    <div class="col-6">
                        <div class="bg-slate-200 p-2 font-medium text-center border-left-2">
                            Opening Shift Information <ComOpenStatus :status="doc.is_closed == 1 ? 'Closed' : 'Open'" />
            </div>
                <table>
                    <ComStayInfoNoBox label="Cashier Shift #" v-if="doc.name" :value="doc.name" />
                    <ComStayInfoNoBox label="Posting Date" v-if="doc.name" :value="moment(doc.posting_date).format('DD-MM-YYYY')" />
                    <ComStayInfoNoBox label="Shift Name" v-if="doc.shift_name" :value="doc.shift_name" />
                </table>
                    </div>
                    <div class="col-6">
                        <div class="bg-slate-200 p-2 font-medium text-center border-left-2">
                            Payment Summary
            </div>
                <table>
                    <ComStayInfoNoBox isCurrency="true" label="Open Cash Float" :value="doc.total_opening_amount" />
                    <ComStayInfoNoBox isCurrency="true" label="Cash Credit" :value="summary?.cash_credit" />
                    <ComStayInfoNoBox isCurrency="true" label="Cash Debit" :value="summary?.cash_debit" />
                    <ComStayInfoNoBox isCurrency="true" label="Cash In Hand" :value="summary?.cash_in_hand" />
                </table>
                    </div>
                </div>

                <table style="width: 100%;">
                    <tr>
                        <td>
                            <h1>Opening Shift Information</h1>
                            <div>
                                Cashier Shift #: {{ doc.name }}
                            </div>
                            <div>
                                Status:
                                <ComOpenStatus :status="doc.is_closed == 1 ? 'Closed' : 'Open'" />
                            </div>
                            <div>
                                Posting Date: {{ moment(doc.posting_date).format("DD/MM/YYYY") }}
                            </div>
                            <div>
                                Shift Name: {{ doc.shift_name }}
                            </div>


                            <div>
                                Opened Note: {{ doc.opened_note }}
                            </div>

                            <div>
                                Opened By: {{ doc?.owner?.split("@")[0] }},
                                <ComTimeago :date="doc.creation" />

                            </div>

                            <hr>

                            <div>
                                <!-- put v-if doc.is_closed==1 -->
                                <h1>Close Shift Information</h1>
                                <div>Close Note: {{ doc.closed_note }} </div>
                                <div> Closed By: {{ doc?.modified_by?.split("@")[0] }},
                                    <ComTimeago :date="doc.closed_date" />
                                </div>
                            </div>

                        </td>
                        <td>

                            <div>Open Cash Float:
                                <CurrencyFormat :value="doc.total_opening_amount" />
                            </div>

                            <div>Cash Credit:
                                <CurrencyFormat :value="summary?.cash_credit" />
                            </div>
                            <div>Cash Debit:
                                <CurrencyFormat :value="summary?.cash_debit" />
                            </div>

                            <div>Cash In Hand:
                                <CurrencyFormat :value="summary?.cash_in_hand" />
                            </div>
                            <hr>
                            <div style="background-color: aquamarine;">
                                <h1>Payment Summary</h1>
                                <div v-for="(p, index) in summary?.summary_by_payment_type" :key="index">
                                    {{ p.payment_type }} :
                                    <CurrencyFormat :value="p.total" />
                                </div>
                            </div>
                        </td>
                    </tr>
                </table>
            </TabPanel>
            <TabPanel>
                <template #header>
                    <span class="me-2">Document</span>
                    <Badge :value="totalDocument"></Badge>
                </template>
                <ComDocument v-if="doc" @updateCount="onUpdateFileCount" doctype="Cashier Shift"
                    :doctypes="['Cashier Shift']" :attacheds="[doc?.name]" :docname="doc?.name" />
            </TabPanel>
        </TabView>


        <div class="col-12">
            <ComCommentAndNotice v-if="doc?.name" doctype="Cashier Shift" :docname="doc?.name"
                :reference_doctypes="['Cashier Shift']" :docnames="[doc?.name]" />
        </div>

        <template #footer-left>

            <SplitButton @click="viewFolioSummaryReport" class="spl__btn_cs sp" label="Print" icon="pi pi-print"
                :model="print_menus" />

        </template>
        <template #footer-right>



            <Button @click="onEditCashierShift">Edit</Button>
            <Button v-if="doc.is_closed == 0" @click="onOpenCloseShift">Close Shift</Button>

        </template>
    </ComDialogContent>
</template>
<script setup>
import { ref, getApi, onMounted, inject, getDoc, useDialog, useToast } from "@/plugin"
import OpenShift from "@/views/cashier_shift/OpenShift.vue"
import ComCommentAndNotice from '@/components/form/ComCommentAndNotice.vue';

const toast = useToast()
const dialogRef = inject("dialogRef")
const moment = inject("$moment")


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




//Folio Summary Report
print_menus.value.push({
    label: "Folio Summary Report",
    icon: 'pi pi-print',
    command: () => {


    }
})

//folio detail report
print_menus.value.push({
    label: "Folio Detail Report",
    icon: 'pi pi-print',
    command: () => {
        // dialog.open(ComPrintReservationStay, {
        //     data: {
        //         doctype: "Reservation%20Stay",
        //         reservation_stay: doc.value.reservation_stay,
        //         folio_number: name.value,
        //         //report_name: "eDoor%20Reservation%20Stay%20Folio%20Detail%20Report",
        //         report_name: gv.getCustomPrintFormat("eDoor Reservation Stay Folio Detail Report"),

        //         view: "print"
        //     },
        //     props: {
        //         header: "Folio Summary Report",
        //         style: {
        //             width: '80vw',
        //         },
        //         position:"top",
        //         modal: true,
        //         maximizable: true,
        //         closeOnEscape: false
        //     },
        // });
    }
})



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
            position: 'top'
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
        toast.add({ severity: 'warn', summary: "This shift is an ePOS shift. Please ask ePOS user to close their shift.", detail: '', life: 3000 })
    } else {
        window.postMessage('close_shift', '*')
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



})

</script>