<template>
    
    <ComDialogContent @onOK="onSave" :loading="isSaving" hideButtonClose>
        <div class="grid justify-between override-input-text-width">
            <div class="col">
                <div class="grid">
                    <div class="col-6">
                            <label for="ref">Ref. No</label>
                            <InputText id="ref" class="w-full" type="text" v-model="doc.reference_number" />
                    </div>
                    <div class="col-6">
                    <label for="posting_date">Posting Date</label>
                        <Calendar inputId="posting_date" v-model="doc.posting_date" :minDate="min_date"
                            :maxDate="moment(working_day?.date_working_day).toDate()" class="w-full" dateFormat="dd-mm-yy" showIcon
                            showButtonBar />
                    </div>
                    <div class="col-6">
                        <label for="account_code">Account Code</label>
                        <ComAutoComplete v-model="doc.account_code" placeholder="Select Account Code" doctype="Account Code"
                            class="auto__Com_Cus w-full" @onSelected="onSelectAccountCode"
                            :filters="{ 'account_group': account_group }" />
                        
                    </div>
                    <div class="col-6">
                    <label for="input_amount">Amount</label>
                    <ComInputCurrency classCss="w-full" v-model="doc.input_amount"/>
                    </div>
                    <div v-if="doc.account_name" class="col-12 -mt-2">
                        <div class="bg-green-100 border-l-4 border-green-400 p-2">
                            {{ doc.account_name }}
                        </div>
                    </div>
                    <!-- Quantity -->
                    <div v-if="account_code.allow_enter_quantity && doc?.account_code" class="col-6">
                        <label for="quantity">Quantity</label>
                        <InputNumber class="w-full" v-model="doc.quantity" />
                    </div>
                    <!-- /Quantity -->
                    <!-- Discount -->
                    <div v-if="account_code.allow_discount && doc?.account_code" class="col-12" >
                        <div class="grid gap-0">
                            <div class="col-12 md:col-6 lg:col-4">
                                <label for="dis_type">Discount Type</label>
                                <div class="w-full">
                                <ComSelect class="w-full min-w-full" id="dis_type" v-model="doc.discount_type"
                                    :options="['Percent', 'Amount']" :clear="false" />
                                </div>
                            </div>
                            <div class="col-12 md:col-6 lg:col-4">
                                <label for="minmaxfraction">Discount</label>
                                <div class="w-full">
                                <InputNumber inputClass="w-full" v-model="doc.discount" inputId="minmaxfraction"
                                    :minFractionDigits="2" :maxFractionDigits="10" />
                                </div>
                            </div>
                            <div class="col-12 md:col-6 lg:col-4">
                                <label for="minmaxfraction">Total Discount</label>
                                <div class="w-full">
                                <div class="w-full rounded-lg max-h-3rem h-edoor-35 leading-8 bg-gray-edoor-10 justify-end flex items-center px-3">
                                    <CurrencyFormat :value="discount_amount"/>
                                </div>    
                                </div>
                            </div>
                        </div>
                    </div>
                    <!-- /Discount -->
                <!-- City Ledger -->
                    <div v-if="doc.require_city_ledger_account == 1 && doc?.account_code" class="col-12">
                        <div class="grid">
                            <div class="col-12">
                                <label>City Ledger Name</label>
                                <ComAutoComplete v-model="doc.city_ledger" placeholder="Select City Ledger Name" doctype="City Ledger"
                                class="auto__Com_Cus w-full" @onSelected="onSelectCityLedger" />
                            </div>
                            <div v-if="doc.city_ledger_name" class="col-12 -mt-2">
                                <div class="bg-green-100 border-l-4 border-green-400 p-2">
                                    {{ doc.city_ledger_name }}
                                </div>
                            </div>
                        </div>   
                    </div>
                <!-- /City Ledger -->
                </div>
            </div>
            <!-- end input -->
            <div v-if="((tax_rule && account_code.allow_tax) || (account_code.show_payment_information) || (account_code.allow_bank_fee)) && doc?.account_code" class="col-5">
                <div class="grid h-full">
                <!-- tax -->
                <div v-if="tax_rule && account_code.allow_tax" class="col-12 mt-auto">
                    <div class="flex flex-col">
                    <div class="flex justify-end text-end">
                            <label for="include-tax" class="col-6 font-medium cursor-pointer">Rate Include Tax</label> 
                            <Checkbox input-id="include-tax"  class="col-6 px-3" v-model="doc.rate_include_tax" :binary="true" trueValue="Yes"
                                falseValue="No" />
                    </div>
                    </div>
                    <!-- Tax - 1 -->
                    <div class="flex mt-2" v-if="tax_rule && tax_rule.tax_1_rate > 0">
                        <ComBoxBetwenConten inputIdFor="tax-1" is-currency="true" title-class="col-6 font-medium"
                        :title="(tax_rule.tax_1_name || '') + '-' + (tax_rule.tax_1_rate || 0) + '%'" :value="(tax_1_amount || 0)"
                            >
                            <template #prefix>
                                <div>
                                    <div class="flex items-center">
                                        <Checkbox inputId="tax-1" v-model="use_tax.use_tax_1" @input="onUseTax1Change" :binary="true" :disabled="!account_code.allow_user_to_change_tax" />
                                    </div>
                                </div>
                            </template>
                            <template #default>
                                <div>
                                    <CurrencyFormat :value="tax_1_amount"/>
                                </div>
                            </template>
                        </ComBoxBetwenConten>
                    </div> 
                    <!-- /Tax - 1 -->
                    <!-- Tax - 2 -->
                    <div class="flex mt-2" v-if="tax_rule && tax_rule.tax_2_rate > 0">
                    <ComBoxBetwenConten inputIdFor="tax-2" is-currency="true" title-class="col-6 font-medium"
                    :title="(tax_rule.tax_2_name || '') + '-' + (tax_rule.tax_2_rate || 0) + '%'" :value="(tax_2_amount || 0)"
                        >
                        <template #prefix>
                            <div>
                            <div class="flex items-center">
                                <Checkbox inputId="tax-2"  v-model="use_tax.use_tax_2" @input="onUseTax2Change" :binary="true" :disabled="!account_code.allow_user_to_change_tax"/>
                            </div>
                            </div>
                        </template>
                        <template #default>
                            <div>
                                <CurrencyFormat :value="tax_2_amount"/>
                            </div>
                        </template>
                    </ComBoxBetwenConten>
                    </div>
                    <!-- /Tax - 2 -->
                    <!-- Tax - 3 -->
                    <div class="flex mt-2" v-if="tax_rule && tax_rule.tax_3_rate > 0">
                    <ComBoxBetwenConten inputIdFor="tax-3" is-currency="true" title-class="col-6 font-medium"
                    :title="(tax_rule.tax_3_name || '') + '-' + (tax_rule.tax_3_rate || 0) + '%'" :value="(tax_3_amount || 0)"
                        >
                        <template #prefix>
                            <div>
                            <div class="flex items-center">
                                <Checkbox inputId="tax-3" v-model="use_tax.use_tax_3" @input="onUseTax3Change" :binary="true" :disabled="!account_code.allow_user_to_change_tax"/>
                            </div>
                            </div>
                        </template>
                        <template #default>
                            <div>
                                <CurrencyFormat :value="tax_3_amount"/>
                            </div>
                        </template>
                    </ComBoxBetwenConten>
                    </div>
                    <!-- /Tax - 3 -->
                    <!-- Total tax -->
                    <div v-if="tax_rule && (tax_rule.tax_1_rate + tax_rule.tax_2_rate + tax_rule.tax_3_rate > 0)"
                        class="flex justify-end mt-2">
                        <ComBoxStayInformation is-currency="true" title-class="col-6 font-medium" title="Total Tax" :value="total_tax"
                            valueClass="max-h-3rem leading-8 col-6 bg-gray-edoor-10 pr-0 text-right" />
                    </div>
                    <!-- /Total tax -->
                </div>
                <!-- /tax -->
                <!-- Bank -->
                <div v-if="account_code.show_payment_information" class="col-12">
                    <div class="grid">
                        <div class="col-12">
                            <label for="credit_card_number">Credit Card Number</label>
                            <InputText class="w-full" type="text" v-model="doc.credit_card_number" />
                        </div>
                        <div class="col-12">
                            <label for="bank_name">Bank Name</label>
                            <InputText class="w-full" type="text" v-model="doc.bank_name" />
                        </div>
                        <div class="col-6">
                            <label for="card_holder_name">Card Holder Name</label>
                            <InputText class="w-full" type="text" v-model="doc.card_holder_name" />
                        </div>
                        <div class="col-6">
                            <label for="credit_expired_date">Credit Expired Date</label>
                            <Calendar class="w-full" v-model="doc.credit_expired_date" view="month" dateFormat="mm/yy" showIcon showButtonBar />
                        </div>
                    </div>
                </div>
                <!-- /Bank -->
                <!-- Bank Fee -->
                    <div v-if="account_code.allow_bank_fee" class="col-12">
                        <div class="grid">
                            <div class="col-6">
                                <label >Bank Fee</label>
                                <InputNumber class="w-full" :input-class="'w-full'" v-model="doc.bank_fee" suffix="%" :readonly="!account_code.allow_user_to_change_bank_fee" />
                            </div>
                            <div class="col-6">
                                <label >Bank Fee Amount</label>
                                <div style="height: 36.5px;" class="w-full rounded-lg max-h-3rem leading-8 bg-gray-edoor-10 justify-end flex items-center px-3">
                                    <CurrencyFormat :value="bank_fee_amount"/>
                                </div>   
                            </div>  
                        </div>
                     </div>
                <!-- /Bank Fee -->
                </div>
            </div>
            <!-- Total Amount -->
            <div class="col-12 mb-1">
                <hr>
            </div>
            <div class="col-12">
            <div class="flex justify-end w-full">
                <div v-if="tax_rule && (tax_rule.tax_1_rate + tax_rule.tax_2_rate + tax_rule.tax_3_rate > 0) && doc?.account_code " class="col-4 p-0">
                    <div class="flex justify-end">
                        <ComBoxStayInformation is-currency="true" title-class="col-6 font-medium" title="Rate Before Tax" :value="amount"
                            valueClass="max-h-3rem h-3rem leading-8 col-6 bg-gray-edoor-10 pr-0 text-right" />
                    </div>
                </div>
                <div class="col-4 p-0">
                    <div class="flex justify-end">
                        <ComBoxStayInformation is-currency="true" title-class="col-6 font-medium" title="Total" :value="total_amount"
                            valueClass="max-h-3rem h-3rem leading-8 col-6 bg-gray-edoor-10 pr-0 text-right" />
                    </div>
                </div>
            </div>
            </div>
            <!-- /Total Amount -->    
            <!-- note -->
            <div class="col-12">
                <div class="grid justify-center px-2 mt-2">
                    <Textarea class="w-full" placeholder="Note" v-model="doc.note" autoResize rows="2" />
                </div>
            </div>
            <!-- /note -->
        </div>
    </ComDialogContent>
</template>
<script setup>

import { ref, inject, getDoc, computed, onMounted, nextTick,useToast,createUpdateDoc } from "@/plugin"
import Calendar from 'primevue/calendar';
import Checkbox from 'primevue/checkbox';
import InputNumber from 'primevue/inputnumber';
import Textarea from 'primevue/textarea';
import ComBoxStayInformation from './ComBoxStayInformation.vue';
import ComBoxBetwenConten from './ComBoxBetwenConten.vue';

const gv = inject("$gv")
const frappe = inject('$frappe');
const db = frappe.db();
const call = frappe.call()

const moment = inject("$moment")
const dialogRef = inject("dialogRef");
const isSaving = ref(false)
const account_group = ref("")
const account_code = ref({});
const city_ledger = ref({});
const balance = ref(0);
const working_day = JSON.parse(localStorage.getItem("edoor_working_day"))
const edoor_setting = JSON.parse(localStorage.getItem("edoor_setting"))
const current_user = JSON.parse(localStorage.getItem("edoor_user"))
const use_tax = ref({})
const toast = useToast()

function onUseTax1Change(value) {
    doc.value.tax_1_rate = value ? tax_rule.value.tax_1_rate : 0
}
function onUseTax2Change(value) {

    doc.value.tax_2_rate = value ? tax_rule.value.tax_2_rate : 0

}
function onUseTax3Change(value) {

    doc.value.tax_3_rate = value ? tax_rule.value.tax_3_rate : 0

}


const tax_rule = computed(() => {
    if (account_code.value?.tax_rule) {

        return JSON.parse(account_code.value.tax_rule_data)
    } else {
        return null
    }
});
const doc = ref({
    discount_type: "Percent",
    quantity: 1,

});

const min_date = computed(() => {
    if (edoor_setting?.allow_user_to_add_back_date_transaction == 0) {
        return moment(working_day?.date_working_day).toDate()
    } else {
        const permit_role = edoor_setting?.role_for_back_date_transaction
        if (current_user?.roles.includes(permit_role)) {
            return moment().subtract(100, "years").toDate()
        } else {
            return moment(working_day?.date_working_day).toDate()
        }

    }

});

const amount = computed(() => {
    if (tax_rule.value) {
        if (doc.value.rate_include_tax == "Yes") {
            return gv.getRateBeforeTax(((doc.value.input_amount || 0) * doc.value.quantity) - (discount_amount.value), tax_rule.value, doc.value.tax_1_rate, doc.value.tax_2_rate, doc.value.tax_3_rate)

        } else {
            return ((doc.value.input_amount || 0) * (doc.value.quantity || 0))
        }
    }
        return ((doc.value.input_amount || 0) * (doc.value.quantity || 0)) - discount_amount.value
})  


const discount_amount = computed(() => {
    if (doc.value.discount_type == "Percent") {
        return ((doc.value.input_amount || 0) * doc.value.quantity) * (doc.value.discount / 100 || 0)
    } else {
        return (doc.value.discount || 0)
    }

});

const tax_1_amount = computed(() => {
    if (tax_rule.value) {
        doc.value.taxable_amount_1 = amount.value * ((tax_rule.value.percentage_of_price_to_calculate_tax_1 || 100) / 100);
        if (tax_rule.value.calculate_tax_1_after_discount == 0 || doc.value.rate_include_tax == "Yes") {
            doc.value.taxable_amount_1 = doc.value.taxable_amount_1
             
        } else {
            doc.value.taxable_amount_1 = doc.value.taxable_amount_1 - discount_amount.value
             
        }
        return (doc.value.taxable_amount_1 || 0) * (doc.value.tax_1_rate / 100 || 0)
    } else {
        return 0
    }
});
const tax_2_amount = computed(() => {
    if (tax_rule.value) {
        doc.value.taxable_amount_2 = amount.value * ((tax_rule.value.percentage_of_price_to_calculate_tax_2 || 100) / 100)

        if (tax_rule.value.calculate_tax_2_after_discount == 0 ||  doc.value.rate_include_tax == "Yes") {
            doc.value.taxable_amount_2 = doc.value.taxable_amount_2
        } else { doc.value.taxable_amount_2 = doc.value.taxable_amount_2 - discount_amount.value }

        if (tax_rule.value.calculate_tax_2_after_adding_tax_1 == 0 || tax_1_amount.value == 0) {
            doc.value.taxable_amount_2 = doc.value.taxable_amount_2
        } else { doc.value.taxable_amount_2 = doc.value.taxable_amount_2 + tax_1_amount.value }

        return (doc.value.taxable_amount_2 || 0) * (doc.value.tax_2_rate / 100 || 0)
    } else {
        return 0
    }
});
const tax_3_amount = computed(() => {
    if (tax_rule.value) {
        doc.value.taxable_amount_3 = amount.value * ((tax_rule.value.percentage_of_price_to_calculate_tax_3 || 100) / 100)

        if (tax_rule.value.calculate_tax_3_after_discount == 0 || doc.value.rate_include_tax == "Yes") {
            doc.value.taxable_amount_3 = doc.value.taxable_amount_3
        } else { doc.value.taxable_amount_3 = doc.value.taxable_amount_3 - discount_amount.value }

        if (tax_rule.value.calculate_tax_3_after_adding_tax_1 == 0 || tax_1_amount.value == 0) {
            doc.value.taxable_amount_3 = doc.value.taxable_amount_3
        } else { doc.value.taxable_amount_3 = doc.value.taxable_amount_3 + tax_1_amount.value }

        if (tax_rule.value.calculate_tax_3_after_adding_tax_2 == 0 || tax_2_amount.value == 0) {
            doc.value.taxable_amount_3 = doc.value.taxable_amount_3
        } else { doc.value.taxable_amount_3 = doc.value.taxable_amount_3 + tax_2_amount.value }

        return (doc.value.taxable_amount_3 || 0) * (doc.value.tax_3_rate / 100 || 0)
    } else {
        return 0
    }
});
const bank_fee_amount = computed(() => {
    return (doc.value.input_amount || 0) * (doc.value.bank_fee / 100 || 0)
})
const total_tax = computed(() => {
    return (tax_1_amount.value || 0) + (tax_2_amount.value || 0) + (tax_3_amount.value || 0)
});
const total_amount = computed(() => {
    const discount = doc.value.rate_include_tax=='Yes'?0:(discount_amount.value || 0)
    return (amount.value || 0) - discount + (total_tax.value || 0) + (bank_fee_amount.value || 0)
});

function onSelectAccountCode(data) {
    if(data.value){
        getDoc('Account Code', data.value)
        .then((d) => {
            account_code.value = d
            doc.value.rate_include_tax = d.rate_include_tax
            doc.value.bank_fee = (d.bank_fee || 0)
            doc.value.require_city_ledger_account = d.require_city_ledger_account
            doc.value.account_name = d.account_name
            doc.value.type = d.type
            doc.value.account_code = d.name
            doc.value.show_print_preview = d.show_print_preview
            doc.value.print_format= d.print_format
            if (d.tax_rule) {
                const tax_rule = JSON.parse(account_code.value.tax_rule_data)
                if (tax_rule) {
                    doc.value.tax_1_rate = tax_rule.tax_1_rate 
                    doc.value.tax_2_rate = tax_rule.tax_2_rate 
                    doc.value.tax_3_rate = tax_rule.tax_3_rate 
                    use_tax.value.use_tax_1 = doc.value.tax_1_rate > 0
                    use_tax.value.use_tax_2 = doc.value.tax_2_rate > 0
                    use_tax.value.use_tax_3 = doc.value.tax_3_rate > 0
                }

            }
            if (d.use_folio_balance_as_default_amount == 1) {
                doc.value.input_amount = balance.value
            }
            if (d.price>0 && !doc.value.name) {
                doc.value.input_amount =d.price
            }


        })
        .catch((error) => {

        });
    }else{
        doc.value.account_name = ''
        doc.value.rate_include_tax = 'No'
        doc.value.input_amount = 0
        total_amount.value = 0

    }
}
function onSelectCityLedger(data) {
    if(data.value){
        getDoc('City Ledger', data.value)
        .then((d) => {
            city_ledger.value = d
            doc.value.city_ledger_name = d.city_ledger_name
        })
        .catch((error) => {

        });
    }else {
        doc.value.city_ledger_name = ''
    }
    

}
function onSave() {
    isSaving.value = true
    
    const data = JSON.parse(JSON.stringify(doc.value))
    if (data.posting_date) data.posting_date = moment(data.posting_date).format("yyyy-MM-DD")
    
    createUpdateDoc("Folio Transaction", { data })
            .then((doc) => {
            isSaving.value = false;
                dialogRef.value.close(doc);

            }).catch((err) => {
            
                isSaving.value = false;
            })
   

}

onMounted(() => {
    
    doc.value.folio_number = dialogRef.value.data.folio_number;

    balance.value = dialogRef.value.data.balance
    if (dialogRef.value.data.folio_transaction_number) {
        //when use edit folio transacitn
        isSaving.value = true
        call.get("edoor.api.reservation.get_folio_detail", {
            name: dialogRef.value.data.folio_transaction_number
        })
            .then((result) => {
                    doc.value = result.message.doc
                    // result.message.posting_date = moment(doc.value.posting_date).format("DD-MM-YYYY")
                    account_code.value = result.message.account_code
                    account_group.value = doc.value.account_group
                    use_tax.value = {
                        use_tax_1:doc.value.tax_1_rate > 0,
                        use_tax_3:doc.value.tax_3_rate > 0,
                        use_tax_2:doc.value.tax_2_rate > 0
                    }
                isSaving.value = false   
            }).catch(()=>{
                isSaving.value = false
            })
    } else {
        //when user want to add data 
        account_group.value = dialogRef.value.data.account_group
        doc.value.posting_date = moment(working_day.date_working_day).toDate();
    }
});

 


</script>
<style scoped>
.h-edoor-35{
    height: 36.5px !important;
}
</style>
