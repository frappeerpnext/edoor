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

        <hr class="my-3">


        <div>Expected Cash:
            <CurrencyFormat :value="summary?.cash_in_hand" />
        </div>

        <div>
            Actual Cash ({{ mainCurrency.name }}):
            <ComInputCurrency classCss="w-full" v-model="doc.main_total_close_amount" v-if="totalMainCashCountAmount == 0" />
            <CurrencyFormat :value="totalMainCashCountAmount" />
            <br />
            Actual Cash ({{ secondCurrency.name }}):

             <InputNumber class="text-end w-full w-15rem" v-model="doc.second_total_close_amount"
                                        :minFractionDigits="0" :maxFractionDigits="secondCurrency.precision" mode="currency"
                                        :currency="secondCurrency.name" :locale="secondCurrency.locale" 
                                        v-if="totalSecondCashCountAmount == 0"
            />

            <CurrencyFormat :value="totalSecondCashCountAmount" :currency="secondCurrency"/>
            
            
            
            <br/>
            Total Actual Cash:
            <CurrencyFormat :value="totalCashCountAmount" />

            
            
        </div>
        <div>Difference Amount:
            <CurrencyFormat :value="((totalCashCountAmount>0?totalCashCountAmount:doc?.total_close_amount ) - doc?.total_system_close_amount) || 0" />
        </div>



        <hr>

        <div v-if="cashCountSetting">
            The Exchange Rate is:
            <div v-for="(c, index) in exchangeRates" :key="index">
                <CurrencyFormat :value="1" />( {{ c.base_currency }}) =
                <CurrencyFormat :value="c.exchange_rate" :currency="c" /> ({{ c.to_currency }})
            </div>

            <h1>Cash Count</h1>
            <table>
                <tr>
                    <td>Note Type</td>
                    <td>Total Note</td>
                    <td>Total Amount</td>
                </tr>
                <template v-for="(c, index) in [...new Set(cashCountSetting.map(r => r.currency))] " :key="index">
                    <tr>
                        <td colspan="3">
                            {{ c }}
                        </td>
                    </tr>
                    <tr v-for="(n, index) in cashCountSetting.filter(r => r.currency == c)" :key="index">
                        <td>
                            {{ n.label }}
                        </td>
                        <td>
                            <InputNumber v-model="n.total_note" />
                        </td>
                        <td>
                            <CurrencyFormat :value="n.value * n.total_note" :currency="n" />
                        </td>

                    </tr>
                    <tr>
                        <td>Total</td>
                        <td>{{ cashCountSetting.filter(r => r.currency == c).reduce((n, d) => n + (d.total_note || 0), 0) }}
                        </td>
                        <td>

                            <CurrencyFormat :value=" cashCountSetting?.filter(r=>r.currency==c).reduce((n, d) => n + (d.total_note * d.value || 0), 0)"  :currency="cashCountSetting?.filter(r=>r.currency==c)[0]"/>
                             
                        </td>
                        
                       
                    </tr>


                </template>


            </table>
 
        </div>
        <hr>
      
        <h1>Other Payment Type</h1>
            <table>
                <tr>
                    <td>Type</td>
                    <td>Total Debit</td>
                    <td>Total Credit</td>
                    <td>System Close Amount</td>
                    <td>Actual Close Amount</td>
                    <td>Difference Amount</td>
                </tr>
                <tr v-for="(s, index) in otherPayments" :key="index">
                    <td>{{ s.payment_type }}</td>
                    <td><CurrencyFormat :value="s.total_debit" /></td>
                    <td><CurrencyFormat :value="s.total_credit" /></td>
                    <td><CurrencyFormat :value="s.total" /></td>
                    <td><ComInputCurrency classCss="w-full" v-model="s.actual_close_amount"  /></td>
                    <td><CurrencyFormat :value="s.actual_close_amount - s.total" /></td>
                </tr>
                <tr>
                    <td>Total</td>
                    <td><CurrencyFormat :value="otherPayments?.reduce((n, d) => n + (d.total_debit || 0), 0)" /></td>
                    <td><CurrencyFormat :value="otherPayments?.reduce((n, d) => n + (d.total_credit || 0), 0)" /></td>
                    <td><CurrencyFormat :value="otherPayments?.reduce((n, d) => n + (d.total || 0), 0)" /></td>
                    <td><CurrencyFormat :value="otherPayments?.reduce((n, d) => n + (d.actual_close_amount || 0), 0)" /></td>
                    <td><CurrencyFormat :value="otherPayments?.reduce((n, d) => n +((d.actual_close_amount || 0) - (d.total || 0) ), 0)" /></td>
                </tr>
            </table>
        

            <hr>
            <div class="w-full mt-3">
            <label>Note:</label> <br />
            <Textarea v-model="doc.closed_note" rows="4" class="w-full" />
        </div>
        
        

        <template #footer-right>
            <div class="relative">
            <span class="absolute w-full"><Checkbox class="w-full" v-model="doc.is_confirm" :binary="true" /></span>
            <span class="pl-5">I have verified that my information about is correct</span>
        </div>

            <Button class="border-none" v-if="doc.is_closed == 0" :disabled= "!doc.is_confirm" @click="onCloseShift">Close Shift</Button>
        </template>
    </ComDialogContent>
</template>
<script setup>
import { useToast, ref, inject, getDoc, onMounted, getApi, computed,useConfirm,createUpdateDoc ,useDialog } from "@/plugin"
import ComIFrameModal from "@/components/ComIFrameModal.vue";
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
const totalCashCountAmount = computed(() => {
    let totalCashCount = 0
     
    if(cashCountSetting.value?.filter(r=>r.total_note>0 & r.currency == mainCurrency.value.name).length>0){
       
        totalCashCount = totalMainCashCountAmount.value  
    }else {
        totalCashCount = doc.value.main_total_close_amount || 0
    }
   

    if(cashCountSetting.value?.filter(r=>r.total_note>0 & r.currency == secondCurrency.value.name).length>0){
        const exchange_rate = exchangeRates.value?.find(r=>r.to_currency == secondCurrency.value.name).exchange_rate
       totalCashCount =totalCashCount +  totalSecondCashCountAmount.value   / exchange_rate
    }else {
        

        const exchange_rate = exchangeRates.value?.find(r=>r.to_currency == secondCurrency.value.name).exchange_rate
        
        totalCashCount = totalCashCount + ((doc.value.second_total_close_amount || 0) / exchange_rate)
    }
    return totalCashCount
    
})
const totalMainCashCountAmount = computed(() => {
    return cashCountSetting.value?.filter(r=>r.currency==mainCurrency.value.name).reduce((n, d) => n + (d.total_note * d.value || 0) / d.exchange_rate, 0)
})
const totalSecondCashCountAmount = computed(() => {
    return cashCountSetting.value?.filter(r=>r.currency==secondCurrency.value.name).reduce((n, d) => n + (d.total_note * d.value || 0), 0)
})

const otherPayments = computed(() => {
    return summary.value?.summary_by_payment_type.filter(r=>r.payment_type_group!='Cash')
})

function onCloseShift(){
     
    doc.value.cash_float.forEach(c=>{
        if(c.currency == mainCurrency.value.name){
            c.input_system_close_amount = summary.value?.cash_in_hand
            c.input_close_amount = totalMainCashCountAmount.value>0?totalMainCashCountAmount.value:doc.value.main_total_close_amount
            c.input_different_amount = c.input_close_amount -  c.input_system_close_amount 
        }else if(c.currency==secondCurrency.value.name){
            c.input_system_close_amount = c.input_amount || 0
            c.input_close_amount = totalSecondCashCountAmount.value>0?totalSecondCashCountAmount.value:doc.value.second_total_close_amount
            c.input_close_amount = c.input_close_amount || 0
            c.input_different_amount = c.input_close_amount -  c.input_system_close_amount 

        }
    })

    
    
    //client validateion

    const saveData = JSON.parse(JSON.stringify( doc.value))
    
    saveData.total_system_close_amount = summary.value.cash_in_hand
    
    if(totalCashCountAmount.value>0){
        saveData.total_close_amount = totalCashCountAmount.value
    }
    saveData.total_different_amount = saveData.total_close_amount - saveData.total_system_close_amount

    if (saveData.total_system_close_amount != 0 && saveData.total_close_amount==0){
        toast.add({ severity: 'warn', summary: "Close cashier shift", detail: 'Please enter actual cash amount', life: 3000 })
        return

    }
    //validate other paymnent
    const otherPaymentData = otherPayments.value.filter(r=>r.total!=0 && r.actual_close_amount==0)
    if (otherPaymentData.length>0){
        toast.add({ severity: 'warn', summary: "Close cashier shift", detail: 'Please enter actual close amount for payment type ' + otherPaymentData[0].payment_type, life: 3000 })
        return
    }

    otherPayments.value.forEach(r=>{
        
        if(doc.value.cash_float.find(x=>x.payment_method==r.payment_type)){
            doc.value.cash_float.find(x=>x.payment_method==r.payment_type).input_system_close_amount=r.total,
            doc.value.cash_float.find(x=>x.payment_method==r.payment_type).input_close_amount=r.actual_close_amount,
            doc.value.cash_float.find(x=>x.payment_method==r.payment_type).input_different_amount=r.actual_close_amount - r.total
        }else {
            saveData.cash_float.push({
                payment_method: r.payment_type,
                currency: mainCurrency.name,
                input_amount:0,
                exchange_rate: 1,
                input_system_close_amount: r.total,
                input_close_amount:r.actual_close_amount,
                input_different_amount:r.actual_close_amount - r.total
            })
        }
        
    })

    saveData.cash_count = cashCountSetting.value
    saveData.cash_count.forEach(r=>{
        r.total_amount = r.total_note * r.value
    })

    confirm.require({
        message: 'Are you sure you can to close this shift?',
        header: 'Confirmation',
        icon: 'pi pi-exclamation-triangle',
        accept: () => {
            loading.value = true
            
            saveData.is_closed = 1

            createUpdateDoc("Cashier Shift", saveData, "Close cashier shift successfully").then(doc=>{
                gv.cashier_shift = null

                    window.working_day.cashier_shift = null
                    localStorage.setItem("edoor_working_day",JSON.stringify(window.working_day))
                    doc.session_id = window.session_id

                    window.socket.emit("UpdateCashierShift", doc);
                    loading.value = false
                    openPrint()
                    dialogRef.value.close(doc);
                  
            }).catch(ex=>{
                loading.value = false
                
            })



            
        },
        
    });
   
}


function openPrint(){
 
    dialog.open(ComIFrameModal, {
            data: {
                "doctype": "Cashier Shift",
                name: doc.value.name,
                report_name:  "eDoor Cashier Shift Report",
            },
            props: {
                header: "Cashier Shift Report " + doc.value.name,
                style: {
                    width: '80vw',
                },
                position:"top",
                modal: true,
                maximizable: true,
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
    getApi("utils.get_cash_count_setting").then(result => {
        cashCountSetting.value = result.message.cash_count_setting
        exchangeRates.value = result.message.exchange_rate_data
    })
}
onMounted(() => {
    getData()
    getCashCountSetting()
})
</script>
