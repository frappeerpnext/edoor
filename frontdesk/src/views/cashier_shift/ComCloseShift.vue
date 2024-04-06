<template>
    <ComDialogContent @close="onClose" :loading="loading" hideButtonOK :hideButtonClose="true">
        <ComOpenStatus statusAddiClass="absolute closeShiftStatus" :status="doc.is_closed == 1 ? 'Closed' : 'Open'" />
        <h1 class="mb-2 font-semibold">Cashier Shift Information</h1>
        <div class="grid justify-between">
            <div class="col-12 xl:col-6 overflow-auto">
                <table>
                    <tbody>
                        <ComStayInfoNoBox label="Cashier Shift #" :value="doc.name" />
                        <ComStayInfoNoBox label="Posting Date" :value="moment(doc.posting_date).format('DD-MM-YYYY')" />
                        <ComStayInfoNoBox label="Shift Name" :value="doc.shift_name" />
                    </tbody>
                </table>
            </div>
            <div class="col-12 xl:col-6">
                <table>
                    <tbody>
                        <ComStayInfoNoBox label="Open Cash Float">
                            <CurrencyFormat currAddClass="font-semibold" :value="doc.total_opening_amount" />
                        </ComStayInfoNoBox>
                        <ComStayInfoNoBox label="Cash Credit">
                            <CurrencyFormat currAddClass="font-semibold" :value="summary?.cash_credit" />
                        </ComStayInfoNoBox>
                        <ComStayInfoNoBox label="Cash Debit">
                            <CurrencyFormat currAddClass="font-semibold" :value="summary?.cash_debit" />
                        </ComStayInfoNoBox>
                    </tbody>
                </table>
            </div>
        </div>

        <h1 class="my-2 font-semibold">Cash Count</h1>

        <div class="grid justify-between">
            <div class="col-12 xl:col-6 overflow-auto">
                <div
                    class="p-3 border-solid border-1 surface-border border-round-md text-center h-full w-full flex justify-content-center align-content-center flex-wrap">
                    <div>
                        <div class="text-lg">Rate Exchange</div>
                        <span v-for="(c, index) in exchangeRates" :key="index" class="text-4xl">
                            <CurrencyFormat currAddClass="font-semibold" :value="1" />({{ c.base_currency }}) =
                            <CurrencyFormat currAddClass="font-semibold" :value="c.exchange_rate" :currency="c" /> ({{
                                c.to_currency }})
                        </span>
                    </div>
                </div>
            </div>
            <div class="col-12 xl:col-6">
                <table class="w-full mb-3">
                    <thead>
                        <tr style='background: rgb(243, 243, 243);'>
                            <th class="w-auto border-1 p-2 font-semibold">Payment Type</th>
                            <th class="w-auto border-1 p-2 font-semibold">Expexted</th>
                            <th class="w-auto border-1 p-2 font-semibold">Actual</th>
                            <th class="w-auto border-1 p-2 font-semibold">Difference</th>
                        </tr>

                    </thead>
                    <tbody>
                        <tr v-for="(p, index) in summary?.expected_cash" :key="index">
                            <td class="w-auto border-1 p-2">{{ p.payment_type }}</td>
                            <td class="w-auto border-1 p-2 text-right">
                                <CurrencyFormat :currency="p" currAddClass="font-semibold" :value="p.expected_amount" />
                            </td>
                            <td class="w-auto border-1 p-2">

                                <InputNumber class="text-end w-full" v-model="p.input_close_amount" :minFractionDigits="0"
                                    :maxFractionDigits="p.precision" mode="currency" :currency="p.currency"
                                    :locale="p.locale" :disabled="p.total_cash_count > 0" />

                            </td>
                            <td class="w-auto border-1 p-2 text-right">
                                <CurrencyFormat :currency="p" currAddClass="font-semibold"
                                    :value="(p.input_close_amount || 0) - p.expected_amount" />
                            </td>
                        </tr>
                        <tr style='background: rgb(243, 243, 243);padding:5px;'>
                            <td class="text-right w-auto border-1 p-2 font-semibold">Total </td>
                            <td class="text-right w-auto border-1 p-2 font-semibold" > <CurrencyFormat :value="totalAmountCash?.expectedAmountTotal" /></td>
                            <td class="text-right w-auto border-1 p-2 font-semibold"> <CurrencyFormat :value="totalAmountCash?.inputAmountTotal" /> </td>
                            <td class="text-right w-auto border-1 p-2 font-semibold"> <CurrencyFormat :value="totalAmountCash?.expectedAmountTotal - totalAmountCash?.inputAmountTotal" /> </td>
                        </tr>
                    </tbody>
                </table>

                <Button @click="onOpenCashCount" label="Cash Count" icon="pi pi-wallet" class="mr-2 conten-btn" />
                <Button @click="onClearCashCount" label="Clear Cash Count" icon="pi pi-eraser" class="conten-btn" />

            </div>
        </div>
        <h1 class="my-2 font-semibold">Other Payment Type</h1>
        <table class="w-full">
            <tr style='background: rgb(243, 243, 243);'>
                <td class="w-auto border-1 p-2 font-semibold">Type</td>
                <td class="w-auto border-1 p-2 font-semibold text-right">Total Debit</td>
                <td class="w-auto border-1 p-2 font-semibold text-right">Total Credit</td>
                <td class="w-auto border-1 p-2 font-semibold text-right">System Close Amount</td>
                <td class="w-auto border-1 p-2 font-semibold text-right">Actual Close Amount</td>
                <td class="w-auto border-1 p-2 font-semibold text-right">Difference Amount</td>
            </tr>
            <tr v-for="(s, index) in otherPayments" :key="index">
                <td class="w-auto border-1 p-2" style='background: rgb(243, 243, 243);'>{{ s.payment_type }}</td>
                <td class="w-auto border-1 p-2 text-right">
                    <CurrencyFormat :value="s.total_debit" />
                </td>
                <td class="w-auto border-1 p-2 text-right">
                    <CurrencyFormat :value="s.total_credit" />
                </td>
                <td class="w-auto border-1 p-2 text-right">
                    <CurrencyFormat :value="s.total" />
                </td>
                <td class="w-auto border-1 p-2 text-right">
                    <ComInputCurrency classCss="w-full" v-model="s.actual_close_amount" />
                </td>
                <td class="w-auto border-1 p-2 text-right">
                    <CurrencyFormat :value="s.actual_close_amount - s.total" />
                </td>
            </tr>
            <tr>
                <td class="font-semibold text-right">Total</td>
                <td class="w-auto p-2 font-semibold text-right">
                    <CurrencyFormat :value="otherPayments?.reduce((n, d) => n + (d.total_debit || 0), 0)" />
                </td>
                <td class="w-auto p-2 font-semibold text-right">
                    <CurrencyFormat :value="otherPayments?.reduce((n, d) => n + (d.total_credit || 0), 0)" />
                </td>
                <td class="w-auto p-2 font-semibold text-right">
                    <CurrencyFormat :value="otherPayments?.reduce((n, d) => n + (d.total || 0), 0)" />
                </td>
                <td class="w-auto p-2 font-semibold text-right">
                    <CurrencyFormat :value="otherPayments?.reduce((n, d) => n + (d.actual_close_amount || 0), 0)" />
                </td>
                <td class="w-auto p-2 font-semibold text-right">
                    <CurrencyFormat
                        :value="otherPayments?.reduce((n, d) => n + ((d.actual_close_amount || 0) - (d.total || 0)), 0)" />
                </td>
            </tr>
        </table>
        <hr>
        <div class="w-full mt-3">
            <label>Note:</label> <br />
            <Textarea v-model="doc.closed_note" rows="4" class="w-full" />
        </div>
        <template #footer-right v-if="doc.is_closed !== 1">
            <div class="relative mt-2">
                <span class="absolute w-full">
                    <Checkbox class="w-full" v-model="doc.is_confirm" :binary="true" />
                </span>
                <span class="pl-5">I have verified that my information above is correct</span>
            </div>
            <Button class="border-none" v-if="doc.is_closed == 0" :disabled="!doc.is_confirm" @click="onCloseShift">Close </Button>
        </template>

    </ComDialogContent>
</template>
<script setup>
import { useToast, ref, inject, getDoc, onUnmounted, onMounted, getApi, computed, useConfirm, createUpdateDoc, useDialog, watch } from "@/plugin"
import ComIFrameModal from "@/components/ComIFrameModal.vue";
import ComCashCount from "@/views/cashier_shift/components/ComCashCount.vue";
const doc = ref({})

const moment = inject("$moment")
const loading = ref(false);
const summary = ref()
const dialogRef = inject("dialogRef")
const cashCountSetting = ref()
const exchangeRates = ref()
const confirm = useConfirm();
const gv = inject(("$gv"))
const toast = useToast()
const mainCurrency = ref(window.setting.currency)
const secondCurrency = ref(window.setting.second_currency)
const dialog = useDialog()
const totalAmountCash = computed(() => {
  return summary?.value?.expected_cash.reduce((totals, currency) => {
    const inputAmount = currency.input_close_amount || 0;
    const amountInUSD = inputAmount / currency.exchange_rate;
    const expectedAmountInUSD = currency.expected_amount / currency.exchange_rate;
    
    return {
      inputAmountTotal: totals.inputAmountTotal + amountInUSD,
      expectedAmountTotal: totals.expectedAmountTotal + expectedAmountInUSD
    };
  }, { inputAmountTotal: 0, expectedAmountTotal: 0 });
});


const totalCashCountAmount = computed(() => {

    let totalCashCount = 0
    summary?.value?.expected_cash.forEach(c => {
        totalCashCount = (totalCashCount || 0) + ((c.input_close_amount || 0) / (c.exchange_rate || 1))
    })

    return totalCashCount


})
const totalMainCashCountAmount = computed(() => {
    return cashCountSetting.value?.filter(r => r.currency == mainCurrency.value.name).reduce((n, d) => n + (d.total_note * d.value || 0) / d.exchange_rate, 0)
})
const totalSecondCashCountAmount = computed(() => {
    return cashCountSetting.value?.filter(r => r.currency == secondCurrency.value.name).reduce((n, d) => n + (d.total_note * d.value || 0), 0)
})

const otherPayments = computed(() => {
    return summary.value?.summary_by_payment_type.filter(r => r.payment_type_group != 'Cash')
})


function onOpenCashCount() {
    dialog.open(ComCashCount, {
        data: {
            cash_count_setting: JSON.parse(JSON.stringify(cashCountSetting.value)),
            summary: JSON.parse(JSON.stringify(summary.value)),
            doc: doc.value,
            exchange_rates: exchangeRates.value
        },
        props: {
            header: "Cash Count",
            style: {
                width: '50vw',
            },
            position: "top",
            modal: true,
            maximizable: true,
            breakpoints:{
                '960px': '50vw',
                '640px': '100vw'
            },
        },
        onClose: (options) => {

            const data = options.data;
            if (data != undefined) {
                summary.value = data.summary
                cashCountSetting.value = data.cash_count_setting
            }
        }
    });
}

function onClearCashCount() {
    confirm.require({
        message: 'Are you sure you want clear  cash count?',
        header: 'Confirmation',
        icon: 'pi pi-exclamation-triangle',
        accept: () => {

            summary.value.expected_cash.forEach(c => {
                c.total_cash_count = 0
            });
            cashCountSetting.value.forEach(x => {
                x.total_note = 0
            })

            toast.add({ severity: 'info', summary: 'Clear Cash Count', detail: 'Clear cash count successfully', life: 3000 });
        },

    });


}

function onCloseShift() {
 
     
 
    doc.value.cash_float.forEach(c => {
        const expected_cash = summary?.value.expected_cash.find(r => r.currency == c.currency)
        if (expected_cash) {
            c.input_system_close_amount = expected_cash.expected_amount
            c.input_close_amount = expected_cash.input_close_amount || 0
            c.input_different_amount = c.input_close_amount - c.input_system_close_amount
        }
    })

    //client validateion

    let saveData = JSON.parse(JSON.stringify(doc.value))

    saveData.total_system_close_amount = summary.value.cash_in_hand


    saveData.total_close_amount = totalCashCountAmount.value

    saveData.total_different_amount = saveData.total_close_amount - saveData.total_system_close_amount

    if (saveData.total_system_close_amount != 0 && saveData.total_close_amount == 0) {
        toast.add({ severity: 'warn', summary: "Close cashier shift", detail: 'Please enter actual cash amount', life: 3000 })
        return

    }
    //validate other paymnent
    const otherPaymentData = otherPayments.value.filter(r => r.total != 0 && r.actual_close_amount == 0)
    if (otherPaymentData.length > 0) {
        toast.add({ severity: 'warn', summary: "Close cashier shift", detail: 'Please enter actual close amount for payment type ' + otherPaymentData[0].payment_type, life: 3000 })
        return
    }

    otherPayments.value.forEach(r => {

        if (doc.value.cash_float.find(x => x.payment_method == r.payment_type)) {
            doc.value.cash_float.find(x => x.payment_method == r.payment_type).input_system_close_amount = r.total,
                doc.value.cash_float.find(x => x.payment_method == r.payment_type).input_close_amount = r.actual_close_amount,
                doc.value.cash_float.find(x => x.payment_method == r.payment_type).input_different_amount = r.actual_close_amount - r.total
        } else {
            saveData.cash_float.push({
                payment_method: r.payment_type,
                currency: mainCurrency.name,
                input_amount: 0,
                exchange_rate: 1,
                input_system_close_amount: r.total,
                input_close_amount: r.actual_close_amount,
                input_different_amount: r.actual_close_amount - r.total
            })
        }

    })

    saveData.cash_count = cashCountSetting.value
    
    saveData.is_run_night_audit = ( window.run_night_audit || 0)

   
    saveData.cash_count.forEach(r => {
        r.total_amount = r.total_note * r.value
    })

  
    confirm.require({
        message: 'Are you sure you can to close this shift?',
        header: 'Confirmation',
        icon: 'pi pi-exclamation-triangle',
        acceptClass: 'border-none crfm-dialog',
        rejectClass: 'hidden',
        acceptIcon: 'pi pi-check-circle',
        acceptLabel: 'Ok',
        accept: () => {
            loading.value = true

            saveData.is_closed = 1

            createUpdateDoc("Cashier Shift", saveData, "Close cashier shift successfully").then(doc => {
                gv.cashier_shift = null

                window.working_day.cashier_shift = null

                localStorage.setItem("edoor_working_day", JSON.stringify(window.working_day))
                
                doc.session_id = window.session_id

                window.socket.emit("UpdateCashierShift", doc);
                loading.value = false
                openPrint()
                dialogRef.value.close(doc);
                window.postMessage("get_workingday","*")

            }).catch(ex => {
                loading.value = false

            })




        },

    });

}


function openPrint() {

    dialog.open(ComIFrameModal, {
        data: {
            "doctype": "Cashier Shift",
            name: doc.value.name,
            report_name: "eDoor Cashier Shift Transaction Summary Report",
            filter_options: ["show_account_code", "group_by_ledger_type", "show_cash_count", "show_cash_float"],
        },
        props: {
            header: "Cashier Shift Report " + doc.value.name,
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

function getSummary() {
    if (doc.value?.name) {
        getApi("utils.get_cashier_shift_summary", {
            name: doc.value?.name,
            property: window.property_name
        }).then((result) => {
            summary.value = result.message
            doc.value.total_system_close_amount = summary.value.cash_in_hand

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

function getCashCountSetting() {
    getApi("utils.get_cash_count_setting",{property:window.property_name}).then(result => {
        cashCountSetting.value = result.message.cash_count_setting
        exchangeRates.value = result.message.exchange_rate_data
    })
}
onMounted(() => {
    getData()
    getCashCountSetting()
    if(window.isMobile){
        let elem = document.querySelectorAll(".p-dialog");
        if (elem){
            elem = elem[elem.length-1]
            elem?.classList.add("p-dialog-maximized"); // adds the maximized class
        }
    }
   

})

</script>
