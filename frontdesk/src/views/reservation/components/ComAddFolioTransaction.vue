<template>
    <ComDialogContent @onOK="onSave" :loading="isSaving" hideButtonClose>
        <div class="grid justify-between override-input-text-width myInput">
            <div class="col pb-0">
                <div class="flex gap-2">
                    <div class="col-6 pl-0" v-if="(dialog_data?.show_room || false)">
                        <label for="room">{{ $t('Room (Optional)') }}</label>
                        <ComAutoComplete :disabled="!canEdit" v-model="doc.room_id" placeholder="Select Room" doctype="Room"
                            class="auto__Com_Cus w-full" :filters="{ 'property': doc.property }" />
                    </div>
                    <div class="col-6 pl-0" v-if="doc.reservation">
                        <label for="room">{{ $t('Guest (Optional)') }}</label>
                        <ComAutoComplete v-model="doc.guest" placeholder="Select Guest" doctype="Customer"
                            class="auto__Com_Cus w-full" :filters="{ 'name': ['in', guests] }" />
                    </div>
                </div>
                <div class="grid">
                    <div class="col-6">
                        <label for="ref">{{ $t('Ref. No') }}</label>
                        <InputText id="ref" class="w-full" type="text" v-model="doc.reference_number" />
                    </div>
                    <div class="col-6">
                        <label for="posting_date">{{ $t('Posting Date') }}</label>

                        <Calendar :selectOtherMonths="true" :disabled="!canEdit" inputId="posting_date"
                            v-model="doc.posting_date" :minDate="min_date"
                            :maxDate="moment(working_day?.date_working_day).toDate()" class="w-full" dateFormat="dd-mm-yy"
                            showIcon showButtonBar selectOtherMonths panelClass="no-btn-clear" />
                    </div>
                    <div class="col-6">
                        <label for="account_code">{{ $t('Account Code') }}</label>
                        <ComAutoComplete :disabled="!canEdit" v-model="doc.account_code" 
                            placeholder="Select Account Code"
                            doctype="Account Code"
                            class="auto__Com_Cus w-full" 
                            @onSelected="onSelectAccountCode"
                            :pageLength="20"
                            :filters="accountCodeFilter" />

                    </div>
                    <div class="col-6">
                        <label for="input_amount">{{ $t('Amount') }}</label>
                        <ComInputCurrency classCss="w-full" :disabled="!canEdit" v-model="doc.input_amount"
                            id="input_amount" />
                            
                    </div>

                    <div v-if="doc.account_name" class="col-12 ">
                        <div class="bg-yellow-100 border-l-4 border-yellow-400 p-2">
                            <span class="text-500 font-italic">{{ $t('You Selected Account Code') }} </span>
                            {{ doc.account_name }}
                        </div>
                    </div>
                    <div class="col-12" v-if="account_code.show_payment_by==1">
                        <div class="col-12 -mb-2 px-0">
                            <hr>
                        </div>
                        <div class="grid">
                            <div class="col-6">
                                <label>{{ $t('Payment By') }}</label>
                                <InputText class="w-full" type="text" v-model="doc.payment_by" placeholder="Name"/>
                            </div>
                            <div class="col-6">
                                <label>{{ $t('Phone Number') }}</label>
                                <InputText  class="w-full" type="text" v-model="doc.payment_by_phone_number" placeholder="phone number"/>
                            </div>
                        </div>
                    </div>  
                    <!-- Quantity -->
                    <div v-if="account_code.allow_enter_quantity && doc?.account_code" class="col-6">
                        <label for="quantity">{{ $t('Quantity') }}</label>
                        <InputNumber class="w-full" v-model="doc.quantity" :minFractionDigits="0" :maxFractionDigits="2" />
                    </div>
                    <!-- /Quantity -->

                    <!-- Select Product -->
                    <div class="col-6" v-if="doc.required_select_product==1">
                       
                        <label >{{ $t('Product') }}</label>
                        <ComAutoComplete :filters="JSON.parse( account_code.default_product_filter || '{}')" class="auto__Com_Cus w-full"  doctype="Product" v-model="doc.product" @onSelected="onSelectProduct" />
                        
                    </div>
                    <div class="col-12">
                        <div v-if="doc.product" class="bg-yellow-100 border-l-4 border-yellow-400 p-2">
                            <span class="text-500 font-italic">{{ $t('You Selected Product Code') }} </span>
                            {{ doc.product_description }} x {{ doc.quantity }}
                        </div>
                    
                    </div>
                    <!-- /select prosduct -->
                    <!-- Discount -->
                    <div v-if="account_code.allow_discount && doc?.account_code" class="col-12">
                        <div class="grid gap-0">
                            <div class="col-12 md:col-6 lg:col-4">
                                <label for="dis_type">{{ $t('Discount Type') }}</label>
                                <div class="w-full">
                                    <ComSelect class="w-full min-w-full" id="dis_type" :disabled="!canEdit"
                                        v-model="doc.discount_type" optionLabel="label" optionValue="value" :options="discountType" :clear="false" />
                                </div>
                            </div>
                            <div class="col-12 md:col-6 lg:col-4">
                                <label for="minmaxfraction">{{ $t('Discount') }}</label>
                                <div class="w-full">
                                    <InputNumber class="w-full" inputClass="w-full" :disabled="!canEdit"
                                        v-model="doc.discount" inputId="minmaxfraction" id="discount" :minFractionDigits="2"
                                        :maxFractionDigits="10" />
                                </div>
                            </div>
                            <div class="col-12 md:col-6 lg:col-4">
                                <label for="minmaxfraction">{{ $t('Total Discount') }}</label>
                                <div class="w-full">
                                    <div
                                        class="w-full rounded-lg max-h-3rem h-edoor-35 leading-8 bg-gray-edoor-10 justify-end flex items-center px-3">
                                        <CurrencyFormat :value="discount_amount" />
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                    <!-- /Discount -->

                   
                    <div v-if="doc.target_transaction_type" class="col-12">
                        <div class="grid">
                            <div class="col-12">

                      
                                <label>{{ $t('Transfer to' + ' ' + doc.target_transaction_type) }}</label>
                               
                                <ComAutoComplete :disabled="!canEdit" v-model="doc.target_transaction_number"
                                    :placeholder="'Select ' + doc.target_transaction_type" :doctype="doc.target_transaction_type" class="auto__Com_Cus w-full"
                                    @onSelected="onSelectTargetTransactionNumber" :filters="targetTransactionNumberFilter" :suggestions="doc.selected_target_transaction_number"/>


                            </div>
 
                            <div v-if="doc.target_transaction_number" class="col-12 -mt-2">
                                <div class="bg-yellow-100 border-l-4 border-yellow-400 p-2">
                                    <span class="text-500 font-italic">{{$t('You Selected')}}</span> {{ doc.target_transaction_number }}  
                                    <!-- <span v-if="doc.selected_target_transaction_data?.description != doc.target_transaction_number">
                                        {{ doc.selected_target_transaction_data?.description }}
                                     
                                    </span> -->
 

                                </div>
                            </div>
                            
                            <div class=" p-2"  v-if="filterTargetTransactionNumberType.length>0">
                                <label>{{ $t('Filter ' + doc.target_transaction_type + ' by') }}</label>
                                 
                                    <Dropdown   class="auto__Com_Cus w-full" :placeholder="'Select Filter Option'" :options="filterTargetTransactionNumberType" optionValue="fieldname" optionLabel="label" v-model="doc.filter_target_transaction_number_by" :showClear="true" />
                
                                
                            </div>
                           


                        </div>
                    </div>
                    <!-- / System Transfer  -->

                   
          
                </div>
            </div>
            <!-- end input -->
            <div v-if="((tax_rule && account_code.allow_tax) || (account_code.show_payment_information) || (account_code.allow_bank_fee)) && doc?.account_code"
                class="col-12">
                <div class="grid h-full">
                    <!-- tax -->
                    <div v-if="tax_rule && account_code.allow_tax" class="col-12 mt-auto">
                        <div class="flex flex-col">
                            <div class="flex justify-end text-end">
                                <label for="include-tax" class="col-6 font-medium cursor-pointer">Rate Include Tax</label>
                                <Checkbox input-id="include-tax" class="col-6 px-3" :disabled="!canEdit"
                                    v-model="doc.rate_include_tax" :binary="true" trueValue="Yes" falseValue="No" />
                            </div>
                        </div>
                        <!-- Tax - 1 -->
                        <div class="flex mt-2" v-if="tax_rule && tax_rule.tax_1_rate > 0">
                            <ComBoxBetwenConten inputIdFor="tax-1" is-currency="true" title-class="col-6 font-medium"
                                :title="(tax_rule.tax_1_name || '') + '-' + (tax_rule.tax_1_rate || 0) + '%'"
                                :value="(tax_1_amount || 0)">
                                <template #prefix>
                                    <div>
                                        <div class="flex items-center">
                                            <Checkbox inputId="tax-1" v-model="use_tax.use_tax_1" @input="onUseTax1Change"
                                                :binary="true"
                                                :disabled="!account_code.allow_user_to_change_tax || !canEdit" />
                                        </div>
                                    </div>
                                </template>
                                <template #default>
                                    <div>
                                        <CurrencyFormat :value="tax_1_amount" />
                                    </div>
                                </template>
                            </ComBoxBetwenConten>
                        </div>
                        <!-- /Tax - 1 -->
                        <!-- Tax - 2 -->
                        <div class="flex mt-2" v-if="tax_rule && tax_rule.tax_2_rate > 0">
                            <ComBoxBetwenConten inputIdFor="tax-2" is-currency="true" title-class="col-6 font-medium"
                                :title="(tax_rule.tax_2_name || '') + '-' + (tax_rule.tax_2_rate || 0) + '%'"
                                :value="(tax_2_amount || 0)">
                                <template #prefix>
                                    <div>
                                        <div class="flex items-center">
                                            <Checkbox inputId="tax-2" v-model="use_tax.use_tax_2" @input="onUseTax2Change"
                                                :binary="true"
                                                :disabled="!account_code.allow_user_to_change_tax || !canEdit" />
                                        </div>
                                    </div>
                                </template>
                                <template #default>
                                    <div>
                                        <CurrencyFormat :value="tax_2_amount" />
                                    </div>
                                </template>
                            </ComBoxBetwenConten>
                        </div>
                        <!-- /Tax - 2 -->
                        <!-- Tax - 3 -->
                        <div class="flex mt-2" v-if="tax_rule && tax_rule.tax_3_rate > 0">
                            <ComBoxBetwenConten inputIdFor="tax-3" is-currency="true" title-class="col-6 font-medium"
                                :title="(tax_rule.tax_3_name || '') + '-' + (tax_rule.tax_3_rate || 0) + '%'"
                                :value="(tax_3_amount || 0)">
                                <template #prefix>
                                    <div>
                                        <div class="flex items-center">
                                            <Checkbox inputId="tax-3" v-model="use_tax.use_tax_3" @input="onUseTax3Change"
                                                :binary="true"
                                                :disabled="!account_code.allow_user_to_change_tax || !canEdit" />
                                        </div>
                                    </div>
                                </template>
                                <template #default>
                                    <div>
                                        <CurrencyFormat :value="tax_3_amount" />
                                    </div>
                                </template>
                            </ComBoxBetwenConten>
                        </div>
                        <!-- /Tax - 3 -->
                        <!-- Total tax -->
                        <div v-if="tax_rule && (tax_rule.tax_1_rate + tax_rule.tax_2_rate + tax_rule.tax_3_rate > 0)"
                            class="flex justify-end mt-2">
                            <ComBoxStayInformation is-currency="true" title-class="col-6 font-medium leading-8"
                                title="Total Tax" :value="total_tax"
                                valueClass="max-h-3rem leading-8 col-6 bg-gray-edoor-10 pr-0 text-right" />
                        </div>
                        <!-- /Total tax -->
                    </div>
                    <!-- /tax -->
                    <!-- Bank -->
                    <div v-if="account_code.show_payment_information" class="col-12">
                        <div class="grid">
                            <div class="col-6">
                                <label for="credit_card_number">{{ $t('Credit Card Number') }}</label>
                                <InputText class="w-full" type="text" v-model="doc.credit_card_number" />
                            </div>
                            <div class="col-6">
                                <label for="bank_name"> {{ $t('Bank Name') }} </label>
                                <InputText class="w-full" type="text" v-model="doc.bank_name" />
                            </div>
                            <div class="col-6">
                                <label for="card_holder_name">{{ $t('Card Holder Name') }}</label>
                                <InputText class="w-full" type="text" v-model="doc.card_holder_name" />
                            </div>
                            <div class="col-6">
                                <label for="credit_expired_date">{{ $t('Credit Expired Date') }}</label>
                              
                                <Calendar class="w-full" v-model="doc.credit_expired_date" view="month" dateFormat="mm/yy"
                                    showIcon showButtonBar  />
                            </div>
                        </div>
                    </div>
                    <!-- /Bank -->
                    <!-- Bank Fee -->
                    <div v-if="account_code.allow_bank_fee" class="col-12">
                        <div class="grid">
                            <div class="col-6">
                                <label>{{ $t('Bank Fee') }}</label>
                                <InputNumber class="w-full" :input-class="'w-full'" v-model="doc.bank_fee" suffix="%"
                                    :maxFractionDigits="2" :readonly="!account_code.allow_user_to_change_bank_fee" />
                            </div>
                            <div class="col-6">
                                <label>{{ $t('Bank Fee Amount') }}</label>
                                <div style="height: 36.5px;"
                                    class="w-full rounded-lg max-h-3rem leading-8 bg-gray-edoor-10 justify-end flex items-center px-3">
                                    <CurrencyFormat :value="bank_fee_amount" />
                                </div>
                            </div>
                        </div>
                    </div>
                    <!-- /Bank Fee -->
                </div>
            </div>
            <!-- Total Amount -->
            <div class="col-12 mb-2 -mt-2">
                <hr>
            </div>
            <div class="col-12 py-0">
                <div class="flex justify-end w-full">
                    <div class="col-3 p-0 mr-3"
                        v-if="tax_rule && (tax_rule.tax_1_rate + tax_rule.tax_2_rate + tax_rule.tax_3_rate > 0) && doc?.account_code">
                        <div class="flex justify-end">
                            <div
                                class="flex flex-column grow p-2 bg-gray-edoor-10 rounded-lg shadow-charge-total border border-gray-edoor-100">
                                <span class="text-500 uppercase text-sm text-end">{{ $t('Rate Before Tax') }}</span>
                                <span class="text-xl line-height-2 font-semibold text-end">
                                    <CurrencyFormat :value="amount" />
                                </span>
                            </div>
                        </div>
                    </div>
                    <div class="col-3 p-0">
                        <div class="flex justify-end">
                            <div
                                class="flex flex-column grow p-2 bg-green-50 rounded-lg shadow-charge-total border border-green-edoor">
                                <span class="text-500 uppercase text-sm text-end">{{ $t('Total') }}</span>
                                <span class="text-xl line-height-2 font-semibold text-end">
                                    <CurrencyFormat :value="total_amount" />
                                </span>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            <!-- /Total Amount -->
            <!-- note -->
            <div class="col-12">
                <div class="grid justify-center px-2 mt-2">
                    <Textarea class="w-full" :placeholder="$t('Note')" v-model="doc.note" autoResize rows="2" />
                </div>
            </div>
            <!-- /note -->
        </div>
    </ComDialogContent>
</template>
<script setup>

import { ref, inject, getDoc, computed, onMounted, createUpdateDoc, getDocList, getApi } from "@/plugin"
import Calendar from 'primevue/calendar';
import Checkbox from 'primevue/checkbox';
import InputNumber from 'primevue/inputnumber';
import Textarea from 'primevue/textarea';
import ComBoxStayInformation from './ComBoxStayInformation.vue';
import ComBoxBetwenConten from './ComBoxBetwenConten.vue';
import {i18n} from '@/i18n';

const { t: $t } = i18n.global;
const discountType = ref([
    { label: $t('Percent'), value: 'Percent' },
    { label: $t('Amount'), value: 'Amount' },
]);
const gv = inject("$gv")
const frappe = inject('$frappe');
const db = frappe.db();
const call = frappe.call()

const guests = ref([])

const moment = inject("$moment")
const dialogRef = inject("dialogRef");
const isSaving = ref(false)
const cityLedgerAmountSummary = ref()
const account_code = ref({});
const city_ledger = ref({});
const folio_number = ref({})
const balance = ref(0);
const working_day = JSON.parse(localStorage.getItem("edoor_working_day"))
const edoor_setting = JSON.parse(localStorage.getItem("edoor_setting"))
const current_user = JSON.parse(localStorage.getItem("edoor_user"))
const use_tax = ref({})
const extra_account_code_filter = ref({}) 
const doc = ref({}) 
const dialog_data =ref()

const accountCodeFilter = computed(()=>{
    if(extra_account_code_filter.value){
        return {...{ 'account_group': doc.value.account_group },...extra_account_code_filter.value}
    }else {
        return { 'account_group': doc.value.account_group }
    } 
})


const filterTargetTransactionNumberType = computed(()=>{
    let options = []
    if (doc.value.target_transaction_type=='Reservation Folio'){
        if(doc.value.reservation_stay){
            options.push({fieldname:"reservation_stay",label:"Reservation Stay"})
        }
        if(doc.value.reservation){
            options.push({fieldname:"reservation",label:"Reservation"})
        }
       
    }


    
    if (["Reservation Folio","Deposit Ledger","Desk Folio"].includes(doc.value.target_transaction_type)){
        if(doc.value.guest){
            options.push({fieldname:"guest",label:"Guest"})
        }
    }
    
    if (["Reservation Folio","City Ledger"].includes(doc.value.target_transaction_type)){
        if(doc.value.business_source){
            options.push({fieldname:"business_source",label:"Business Source"})
        }
    }


    return options

})

const targetTransactionNumberFilter = computed(()=>{
    let filter = {status:"Open"}
    filter.property = window.property_name
    if (doc.value.target_transaction_type == doc.value.transaction_type){
        filter.name = ["!=", doc.value.transaction_number]
    }

    if (doc.value.filter_target_transaction_number_by){
        filter[doc.value.filter_target_transaction_number_by] = doc.value[doc.value.filter_target_transaction_number_by]
    }
 

    return filter

})

const folioNumberFilter = ref()
function onUseTax1Change(value) {
    doc.value.tax_1_rate = value ? tax_rule.value.tax_1_rate : 0
} 
function onUseTax2Change(value) {

    doc.value.tax_2_rate = value ? tax_rule.value.tax_2_rate : 0

}
function onUseTax3Change(value) {

    doc.value.tax_3_rate = value ? tax_rule.value.tax_3_rate : 0

} 
const canEdit = computed(() => {
    return edoor_setting?.folio_transaction_style_credit_debit == 0 || doc.value.name == undefined;
});

const tax_rule = computed(() => {
    if (account_code.value?.tax_rule) {

        return JSON.parse(account_code.value.tax_rule_data)
    } else {
        return null
    }
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
            let priceBefore = gv.getRateBeforeTax(((doc.value.input_amount || 0) * (doc.value.quantity)) - (discount_amount.value), tax_rule.value, doc.value.tax_1_rate, doc.value.tax_2_rate, doc.value.tax_3_rate)
            let priceAfter = priceBefore + discount_amount.value
            return (priceAfter * doc.value.quantity)  

        } else {
            return ((doc.value.input_amount || 0) * (doc.value.quantity))
        }
    }
    return ((doc.value.input_amount || 0) * (doc.value.quantity)) - discount_amount.value
})


const discount_amount = computed(() => {
    if (doc.value.discount_type == "Percent") {
        return ((doc.value.input_amount || 0) * (doc.value.quantity)) * (doc.value.discount / 100 || 0)
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

        if (tax_rule.value.calculate_tax_2_after_discount == 0 || doc.value.rate_include_tax == "Yes") {
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
    const discount = doc.value.rate_include_tax == 'Yes' ? 0 : (discount_amount.value || 0)
    return (amount.value || 0) - discount + (total_tax.value || 0) + (bank_fee_amount.value || 0)
});

function onSelectAccountCode(data) {

    if (data.value) {
        getDoc('Account Code', data.value)
            .then((d) => {
                account_code.value = d
                doc.value.rate_include_tax = d.rate_include_tax
                doc.value.bank_fee = (d.bank_fee || 0)
                doc.value.account_name = d.account_name
                doc.value.type = d.type
                doc.value.account_code = d.name
                doc.value.show_print_preview = d.show_print_preview
                doc.value.print_format = d.print_format
                doc.value.discount_type = "Percent"
                doc.value.discount = 0
                doc.value.target_account_type = d.target_account_type
                doc.value.target_account_code= d.target_account_code
                doc.value.target_transaction_type = d.target_document
                doc.value.required_select_product= d.required_select_product
            
               


                doc.value.quantity = 1
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

                if (account_code.value.use_folio_balance_as_default_amount == 1) {
                    doc.value.input_amount = Math.abs(balance.value || 0)
                }
                if (d.price > 0 && !doc.value.name) {
                    doc.value.input_amount = d.price
                }

                if (d.target_document && d.target_document=='City Ledger'){
                    getSuguestCityLedger()
                }else {
                    doc.value.target_transaction_number=""
                }

                const input = document.getElementById("input_amount").querySelector('input')
                input.focus()
                input.select()

            })
            .catch((error) => {

            });
    } else {
        doc.value.account_name = ''
        doc.value.rate_include_tax = 'No'
        doc.value.input_amount = 0
        total_amount.value = 0
        doc.value.city_ledger = ''
        doc.value.city_ledger_name = ''
        doc.value.folio_number = ''
        doc.value.target_transaction_number = ""
        doc.value.target_transaction_type = ""
        doc.value.required_select_product= 0
        doc.value.product=  ""


    }
}
 


function onSelectProduct(data){
    doc.value.product_description = data.description || ''
    if (data?.value){
        getDoc("Product", data.value).then(r=>{
          
            doc.value.input_amount = r.price || 0
        })
    }
    
}
function onSelectTargetTransactionNumber(data){
     
        doc.value.selected_target_transaction_data=data
  
  
}

function onSelectCityLedger(data) {
    if (data.value) {
        getDoc('City Ledger', data.value)
            .then((d) => {
                city_ledger.value = d
                doc.value.city_ledger_name = d.city_ledger_name

            })
    } else {
        doc.value.city_ledger_name = ''
    }


}
function onSelectFolioNumber(data) {
    doc.value.selected_folio_number_description = data.description
}

function onFolioFilterTypeChange(d){
    doc.value.target_transaction_number = ""
    doc.value.target_transaction_number = ""
}
 


function onSave() {
    
    const data = JSON.parse(JSON.stringify(doc.value))
    if (data.posting_date) data.posting_date = moment(data.posting_date).format("yyyy-MM-DD")
    if(!gv.cashier_shift?.name){
        isSaving.value = false;
        gv.toast('error', 'Please Open Cashier Shift.')
        return
        
    }
    isSaving.value = true;
    createUpdateDoc("Folio Transaction", data)
        .then((doc) => {
            isSaving.value = false
            dialogRef.value.close(doc)
            window.postMessage({action:"ReservationList"},"*")
            window.postMessage({action:"GuestLedger"},"*")
            window.postMessage({action:"ReservationStayList"},"*")
            window.postMessage({action:"ReservationStayDetail"},"*")
            window.postMessage({action:"ReservationDetail"},"*")
            window.postMessage({action:"FolioTransactionDetail"},"*")
            window.postMessage({action:"CityLedgerAccount"},"*")
            window.postMessage({action:"ComCityLedgerDetail"},"*") 
            window.postMessage({action:"GuestLedgerTransaction"},"*")
            window.postMessage({action:"Reports"},"*")
            window.postMessage({action:"FolioTransactionList"},"*")
            window.postMessage({action:"ComPayableLedgerDetail"},"*")
            window.postMessage({action:"PayableLedger"},"*")
            window.postMessage({action:"DeskFolio"},"*") 
            window.postMessage({action:"ComDeskFolioDetail"},"*")
            window.postMessage({action:"DepositLedger"},"*")
            window.postMessage({action:"ComDepositLedgerDetail"},"*")
            window.postMessage({action:"load_folio_transaction"},"*")

        }).catch((err) => {
            isSaving.value = false;
        })
}

function getSuguestCityLedger(){
    if(dialogRef.value.data.business_source){
            call.get('frappe.desk.search.search_link', {doctype:"City Ledger",txt:dialogRef.value.data.business_source, filters: [["property", "=", window.property.name]]}).then(r=>{
 
                if (r.message.length > 0) {
                    doc.value.target_transaction_number = r.message[0].value
                    doc.value.selected_target_transaction_data= r.message[0]
                    doc.value.selected_target_transaction_number = r.message
                    
                }else {
                    doc.value.selected_target_transaction_number = null
                }
            })
 
        }

}
onMounted(() => { 
    if(window.isMobile){
        let elem = document.querySelectorAll(".p-dialog");
        if (elem){
            elem = elem[elem.length-1]
            elem?.classList.add("p-dialog-maximized"); // adds the maximized class
        }
    }
    balance.value = dialogRef.value.data.balance
    let reservation = ""
    dialog_data.value = dialogRef.value.data
    if (dialogRef.value.data.folio_transaction_number) {
        //when use edit folio transacitn
        isSaving.value = true
        reservation = dialogRef.value.data.reservation
        call.get("edoor.api.reservation.get_folio_detail", {
            name: dialogRef.value.data.folio_transaction_number
        })
            .then((result) => {
                doc.value = result.message.doc
                account_code.value = result.message.account_code

                use_tax.value = {
                    use_tax_1: doc.value.tax_1_rate > 0,
                    use_tax_3: doc.value.tax_3_rate > 0,
                    use_tax_2: doc.value.tax_2_rate > 0
                }
                doc.value.posting_date = moment(doc.value.posting_date).toDate();

                isSaving.value = false
                folioNumberFilter.value = { 'property': window.property_name, status: 'Open', 'name': ['!=', doc.value.transaction_number] }
            }).catch(() => {
                isSaving.value = false
            })
 
    } else {
        //when user add new folio transaction
        reservation = dialogRef.value.data.new_doc.reservation
        doc.value = dialogRef.value.data.new_doc     
        extra_account_code_filter.value = dialogRef.value.data.account_code_filter

        doc.value.posting_date = moment(working_day.date_working_day).toDate();
        folioNumberFilter.value = { 'property': window.property_name, status: 'Open', 'name': ['!=', doc.value.transaction_number] }
        
    }
    //get guest by reservation
    if (reservation) {
        getApi("reservation.get_guest_by_reservation", { reservation: reservation }).then(result => {
            guests.value = result.message
        })
    }
}); 

</script>
<style scoped>.h-edoor-35 {
    height: 36.5px !important;
}</style>
