<template>
    <ComDialogContent @onOK="onSave" :loading="isSaving" hideButtonClose>
       <div class="grid">
       <div class="col grid justify-between override-input-text-width myInput">
            <div class="col pb-0">
                <div class="grid">
                    <div class="col-12 " v-if="(dialog_data?.show_source_reservation_stay || false)">
                        <label for="source_reservation_stay">{{ $t('Reservation Stay') }}</label>
                        <ComAutoComplete :disabled="!canEdit" v-model="doc.source_reservation_stay" placeholder="Reservation Stay associated with this Transaction" doctype="Reservation Stay"
                            class="auto__Com_Cus w-full" :filters="{ 'property': doc.property,'reservation':doc.reservation,'reservation_status':'In-house' }" />
                    </div>
                    <div class="col-6 " v-if="(dialog_data?.show_room || false)">
                        <label for="room">{{ $t('Room (Optional)') }}</label>
                        <ComAutoComplete :disabled="!canEdit" v-model="doc.room_id" placeholder="Select Room" doctype="Room"
                            class="auto__Com_Cus w-full" :filters="{ 'property': doc.property }" />
                    </div>
                    <div class="col-6 " v-if="doc.reservation">
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
                            :filters="accountCodeFilter"
                            
                            />

                    </div>
                    <div class="col-6">
                        <label for="input_amount">{{ $t('Amount') }}</label>
                        
                        <ComInputCurrency   classCss="w-full" :disabled="!canEdit || doc.required_select_product==1" v-model="doc.input_amount"
                            id="input_amount" @update:modelValue="onRateCalculation" />
                            
                    </div>

                    <div v-if="doc.account_name" class="col-12 ">
                        <div class="bg-yellow-100 border-l-4 border-yellow-400 p-2">
                            <span class="text-500 font-italic">{{ $t('You Selected Account Code') }} </span>
                           {{ doc.account_code }} - {{ doc.account_name }}
                        </div>
                    </div>
                                        <!-- Bank Fee -->
                                        <div v-if="doc.account_name && account_code.allow_bank_fee" class="col-12">
                        <div class="grid">
                            <div class="col-6">
                                <label>{{ $t('Bank Fee') }}</label>
                                <InputNumber @update:modelValue="onRateCalculation" class="w-full" :input-class="'w-full'" v-model="doc.bank_fee" suffix="%"
                                    :maxFractionDigits="2" :readonly="!account_code.allow_user_to_change_bank_fee" />
                            </div>
                            <div class="col-6">
                                <label>{{ $t('Bank Fee Amount') }}</label>
                                <div style="height: 36.5px;"
                                    class="w-full rounded-lg max-h-3rem leading-8 bg-gray-edoor-10 justify-end flex items-center px-3">
                                    <CurrencyFormat :value="data?.bank_fee_amount" />
                                </div>
                            </div>
                        </div>
                    </div>
                    <!-- /Bank Fee -->
                    <!-- Bank -->
                    <div v-if="doc.account_name  && account_code.show_payment_information" class="col-12">
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
                    <div class="col-12" v-if="doc.account_name && account_code.show_payment_by==1">
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


                    <!-- Pax -->
                    <div v-if="account_code.allow_enter_pax && doc?.account_code"  class="col-12 grid pt-0">
                    <div class="col-6 pr-1 ">
                            <label>{{$t('Adults')}}</label>
                            <InputNumber @update:modelValue="onRateCalculation" v-model="doc.adult" inputId="stacked-buttons" showButtons :min="1" :max="100"
                                class="child-adults-txt w-full"  />
                            </div>
                            <div class="col-6 pr-0 pl-3">
                            <label>{{$t('Children')}}</label>
                            <InputNumber v-model="doc.child" @update:modelValue="onRateCalculation" inputId="stacked-buttons" showButtons :min="0" :max="100"
                                class="child-adults-txt w-full"  />
                            </div>
                    </div>
                    <!-- Pax -->
                    <!-- Quantity -->
                    <div v-if="account_code.allow_enter_quantity && doc?.account_code && !doc.required_select_product==1" class="col-6">
                        <label for="quantity">{{ $t('Quantity') }}</label>
                        <InputNumber class="w-full" @update:modelValue="onRateCalculation" v-model="doc.quantity" :minFractionDigits="0" :maxFractionDigits="2" />
                    </div>
                    <!-- /Quantity -->

                    <!-- Select Product -->
         <!--          <div class="col-6" v-if="doc.required_select_product==1">
                       
                        <label >{{ $t('Product') }}</label>
                        <ComAutoComplete :filters="JSON.parse( account_code.default_product_filter || '{}')" class="auto__Com_Cus w-full"  doctype="Product" v-model="doc.product" @onSelected="onSelectProduct" />
                        

    </div>--> 
    <div  v-if="doc.required_select_product==1" class="col-12 " >
    <div v-for="(item, index) in doc.items" :key="index" class="w-full grid">
        <div class="col">
        <label v-if="index == 0">Product</label>
        <ComAutoComplete :filters="JSON.parse( account_code.default_product_filter || '{}')" class="auto__Com_Cus w-full"  doctype="Product" v-model="item.product_code" @onSelected="onSelectProduct($event ,index)" />        
        </div>
        <div class="col">
            <label v-if="index == 0">Product Name</label>
    <InputText class="w-full" disabled  type="text" v-model="item.product_name" placeholder="Name"/>        
        </div >
        <div class="col">
            <label v-if="index == 0">QTY</label>
    <InputNumber class="w-full" @update:modelValue="calculateTotalAmounts(index)" v-model="item.quantity" :minFractionDigits="0" :maxFractionDigits="2" />  
        </div>
    <div class="col">
        <label v-if="index == 0">Price</label>
     <ComInputCurrency @update:modelValue="calculateTotalAmounts(index)" classCss="w-full" :disabled="!canEdit" v-model="item.price" />    
    </div> 
    <div class="col">
        <label v-if="index == 0">Total Amount</label>
     <ComInputCurrency  classCss="w-full" disabled v-model="item.total_amount" />    
    </div> 
      <div class="col-fixed w-4rem" >
      <Button class="tr-h__custom text-3xl h-12" icon="pi pi-trash" v-if="index !== 0" @click="removeItem(index)">
      </Button></div>
      
    </div>
      <Button @click="addItem" class="px-4 mt-2 conten-btn">Add Item</Button>
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
                                        v-model="doc.discount_type" @update:modelValue="onRateCalculation" optionLabel="label" optionValue="value" :options="discountType" :clear="false" />
                                </div>
                            </div>
                            <div class="col-12 md:col-6 lg:col-4">
                                <label for="minmaxfraction">{{ $t('Discount') }}</label>
                                <div class="w-full">
                                    <InputNumber class="w-full" @update:modelValue="onRateCalculation" inputClass="w-full" :disabled="!canEdit"
                                        v-model="doc.discount" inputId="minmaxfraction" id="discount" :minFractionDigits="2"
                                        :maxFractionDigits="10" />
                                </div>
                            </div>
                            <div class="col-12 md:col-6 lg:col-4">
                                <label for="minmaxfraction">{{ $t('Total Discount') }}</label>
                                <div class="w-full">
                                    <div

                                        class="w-full rounded-lg max-h-3rem h-edoor-35 leading-8 bg-gray-edoor-10 justify-end flex items-center px-3">
                                    
                                        <CurrencyFormat :value="data?.discount_amount" />
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
                                    <CurrencyFormat :value="data?.total_amount - data?.total_tax" />
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
                                    <CurrencyFormat :value="data?.total_amount" />
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
        <div v-if="tax_rule && account_code.allow_tax && doc?.account_code && !doc.required_select_product==1" class="col-4">
            <div class="card">
        <Accordion :activeIndex="0">
            <AccordionTab header="Room Rate Breakdown">
                <div class="grid p-2">
                    <div class="col-12 pb-0">
                <div class="grid justify-end ">
                    <div class="col-12">
                        <table>
                    <tbody>
                        <ComStayInfoNoBox label="Base Rate"
                            :value="data?.base_transaction_data?.rate" isCurrency="true" valueClass="text-end" />
                            <ComStayInfoNoBox v-if="data?.base_transaction_data?.discount_amount" label="Discount" :value="data?.base_transaction_data?.discount_amount" isCurrency="true" valueClass="text-end" />    
                            <ComStayInfoNoBox label="Rate Include Tax" valueClass="text-end">
                                <div class="flex gap-2">
                             <Checkbox   @change="onRateCalculation"  :disabled="!canEdit"
                             v-model="doc.rate_include_tax" :binary="true" trueValue="Yes" falseValue="No" /> 
                                </div>    
                            </ComStayInfoNoBox>
                            <ComStayInfoNoBox v-if="tax_rule && tax_rule.tax_1_rate > 0" :label="($t(tax_rule.tax_1_name ?? '') || '') + ' ' + (tax_rule.tax_1_rate || 0) + '%'" valueClass="text-end">
                                <div class="flex gap-2"> 
                                    <CurrencyFormat :value="data?.base_transaction_data?.tax_1_amount || 0 " />
                                 <Checkbox v-model="use_tax.use_tax_1" @input="onUseTax1Change"
                                                :binary="true"
                                                :disabled="!account_code.allow_user_to_change_tax || !canEdit" />
                                </div>
                            </ComStayInfoNoBox>
                            <ComStayInfoNoBox v-if="tax_rule && tax_rule.tax_2_rate > 0" :label="($t(tax_rule.tax_2_name ?? '') || '') + ' ' + (tax_rule.tax_2_rate || 0) + '%'" valueClass="text-end">
                                <div class="flex gap-2"> 
                                    <CurrencyFormat :value="data?.base_transaction_data?.tax_2_amount || 0 " />
                                <Checkbox input-id="tax-2" @input="onUseTax2Change" v-model="use_tax.use_tax_2"
                                                            :binary="true" />
                                </div>
                            </ComStayInfoNoBox>
                            <ComStayInfoNoBox v-if="tax_rule && tax_rule.tax_3_rate > 0" :label="($t(tax_rule.tax_3_name ?? '') || '') + ' ' + (tax_rule.tax_3_rate || 0) + '%'" valueClass="text-end">
                                <div class="flex gap-2"> 
                                    <CurrencyFormat :value="data?.base_transaction_data?.tax_3_amount || 0 " />
                                <Checkbox input-id="tax-3" @input="onUseTax3Change" v-model="use_tax.use_tax_3"
                                                            :binary="true" />
                                </div>
                            </ComStayInfoNoBox>
                         
                             <ComStayInfoNoBox v-if="tax_rule && (tax_rule.tax_1_rate + tax_rule.tax_2_rate + tax_rule.tax_3_rate > 0) && doc?.account_code" 
                                label="Total Tax" 
                                :value="data?.base_transaction_data?.total_tax" isCurrency="true" valueClass="text-end" />  
                                <ComStayInfoNoBox   
                                label="Total Rate" 
                                :value="data?.base_transaction_data?.total_amount" isCurrency="true" valueClass="text-end" />   
                    </tbody>
                </table>
                   
                        
                    </div>
                </div>
            </div>
                </div>
            </AccordionTab>
            <AccordionTab v-if="account_code.is_package && data?.package_charge_data " >
               <template #header>
Package Charge Breakdown
               </template> 
                <div class="col-12">
  <div class="grid p-y px-2">
    <div class="col-12" v-for="item in data?.package_charge_data" :key="item.account_name" >
        <Fieldset  :key="item.account_name" v-if="item.quantity > 0" >
            <template #legend>
                <div class="flex align-items-center pl-2">
                    <span class="font-bold"> {{ item.account_name }} x {{ item.quantity }} </span>
                </div>
            </template>
            <div class="grid">
                <table class="w-full">
                    <tbody>
                        <ComStayInfoNoBox label="Base Rate"
                            :value="item.rate" isCurrency="true" valueClass="text-end" />
                            <ComStayInfoNoBox v-if="item.discount_amount > 0" label="Discount" :value="item.discount_amount" isCurrency="true" valueClass="text-end" />    
                          <ComStayInfoNoBox label="Rate Include Tax" valueClass="text-end">
                                <div class="flex gap-2"> 
                             <Checkbox  v-model="item.rate_include_tax" disabled :binary="true"
                                    trueValue="Yes" falseValue="No"  /> 
                                </div>    
                              
                            </ComStayInfoNoBox>
                              <ComStayInfoNoBox v-if="item.tax_1_rate > 0" :label="($t(item.tax_1_name ?? '') || '') + ' ' + (item.tax_1_rate || 0) + '%'" valueClass="text-end">
                                <div class="flex gap-2"> 
                                    <CurrencyFormat :value="item.tax_1_amount || 0 " />
                                <Checkbox v-model="isCheckedTrue" disabled :binary="true"
                                    />
                                </div>
                            </ComStayInfoNoBox>
                           <ComStayInfoNoBox v-if="item.tax_2_rate > 0" :label="($t(item.tax_2_name ?? '') || '') + ' ' + (item.tax_2_rate || 0) + '%'" valueClass="text-end">
                                <div class="flex gap-2"> 
                                    <CurrencyFormat :value="item.tax_2_amount || 0 " />
                                    <Checkbox v-model="isCheckedTrue" disabled :binary="true"
                                    />
                                </div>
                            </ComStayInfoNoBox>
                              <ComStayInfoNoBox v-if="item.tax_3_rate > 0" :label="($t(item.tax_3_name ?? '') || '') + ' ' + (item.tax_3_rate || 0) + '%'" valueClass="text-end">
                                <div class="flex gap-2"> 
                                    <CurrencyFormat :value="item.tax_3_amount || 0 " />
                                    <Checkbox v-model="isCheckedTrue" disabled :binary="true"
                                   />
                                </div>
                            </ComStayInfoNoBox>
                          <ComStayInfoNoBox  v-if="item.tax_1_rate > 0 || item.tax_2_rate > 0 || item.tax_3_rate > 0" 
                                label="Total Tax" 
                                :value="item.total_tax" isCurrency="true" valueClass="text-end" />  
                                 <ComStayInfoNoBox   
                                label="Total Rate" 
                                :value="item.total_amount" isCurrency="true" valueClass="text-end" />        
                    </tbody>
                </table>
            </div> 
        </Fieldset>
    </div>
                </div>
                </div>
            </AccordionTab>
        </Accordion>
    </div>
        </div>
         </div>  
    </ComDialogContent>
</template>
<script setup>

import { ref, inject, getDoc, computed, onMounted, createUpdateDoc, getDocList, getApi,postApi,nextTick  } from "@/plugin"
import Calendar from 'primevue/calendar';
import Checkbox from 'primevue/checkbox';
import InputNumber from 'primevue/inputnumber';
import Textarea from 'primevue/textarea';
import ComBoxStayInformation from './ComBoxStayInformation.vue';
import ComBoxBetwenConten from './ComBoxBetwenConten.vue';
import {i18n} from '@/i18n';
const isCheckedTrue = ref(true);
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
const doc = ref({});
const dialog_data =ref()
const data = ref()

const addItem = () => {
    doc.value.items.push({
    product_code: '',
    product_name:'',
    quantity: 1,
    price: 0,
    total_amount:0
  });
};
function removeItem(index) {
    doc.value.items.splice(index, 1);
    doc.value.input_amount = doc.value.items.reduce((sum, item) => sum + item.total_amount, 0)
    onRateCalculation()
}
function calculateTotalAmounts(index) {
    setTimeout(() => {
    doc.value.items[index].total_amount = (doc.value.items[index].quantity ==0?1:doc.value.items[index].quantity) * doc.value.items[index].price;
    doc.value.input_amount = doc.value.items.reduce((sum, item) => sum + item.total_amount, 0)
    onRateCalculation()
  }, 50);

}
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
function onUseTax1Change() {
    doc.value.tax_1_rate = use_tax.value.use_tax_1 ?  0 : tax_rule.value.tax_1_rate
    onRateCalculation()
} 

function onUseTax2Change() {

    doc.value.tax_2_rate = use_tax.value.use_tax_2 ?  0 : tax_rule.value.tax_2_rate
    onRateCalculation()
}
function onUseTax3Change() {

    doc.value.tax_3_rate = use_tax.value.use_tax_3 ?  0 : tax_rule.value.tax_3_rate
    onRateCalculation()

} 
const canEdit = computed(() => {
    return true; // edoor_setting?.folio_transaction_style_credit_debit == 0 || doc.value.name == undefined;
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



 
 
 
 
function onSelectAccountCode(data) {

    if (data.value) {
        getDoc('Account Code', data.value)
            .then((d) => {
                account_code.value = d
                doc.value.tax_rule = d.tax_rule
                doc.value.rate_include_tax = d.rate_include_tax
                doc.value.bank_fee = (d.bank_fee || 0)
                doc.value.bank_fee_account = d.bank_fee_account
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
                if(d.allow_enter_pax){
                    doc.value.child = 0
                    doc.value.adult = 1
                }
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
                if(doc.value.required_select_product){
              doc.value.items = [
      {
        product_code: '',
        product_name:'',
        quantity: 1,
        price: 0,
        total_amount:0
      }
    ];
        }  
            })
            .catch((error) => {

            });
    } else {

        doc.value.account_name = ''
        doc.value.rate_include_tax = 'No'
        doc.value.input_amount = 0
        
        doc.value.city_ledger = ''
        doc.value.city_ledger_name = ''
        doc.value.folio_number = ''
        doc.value.target_transaction_number = ""
        doc.value.target_transaction_type = ""
        doc.value.required_select_product= 0
        doc.value.product=  ""
        doc.value.items = []

    }
}
 


function onSelectProduct(data,index){
    if (data?.value){
        getDoc("Product", data.value).then(r=>{  
            if(r?.product_name_en){
         doc.value.items[index].product_name = r?.product_name_en || ''       
            }
            if (r.product_price){   
                let price = r.product_price.find(x=>x.business_branch == window.property_name && x.price_rule == window.setting.pos_profile.price_rule) 
        
                if (price){ 
                    console.log(doc.value.items[index].price)
                    doc.value.items[index].price = price.price
                    
                }else {
              
                        price = r.product_price.find(x=>x.price_rule == window.setting.pos_profile.price_rule)
                        if(price){
                            doc.value.items[index].price = price.price
                        }else {
                            doc.value.items[index].price = r.price || 0
                        }
                }
            }else {
                doc.value.items[index].price = r.price || 0
            }
            calculateTotalAmounts(index) 
           
        })
    }else{
        doc.value.items[index].price = 0
        doc.value.items[index].product_name = ''
        doc.value.items[index].total_amount = 0
        doc.value.input_amount = doc.value.items.reduce((sum, item) => sum + item.total_amount, 0)
         calculateTotalAmounts(index) 
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

async function onRateCalculation(newValue){
    await nextTick();
   
    if (doc.value.account_code && doc.value.input_amount){
        postApi("add_folio_transaction.get_folio_transaction_calculation",
        {
            folio_transaction_data:doc.value
        },
        "",
        false
).then(result=>{
        data.value = result.message
        
    })
    }
}



function onSave(){
    const data = JSON.parse(JSON.stringify(doc.value))
    data.input_amount = data.input_amount || 0
    // will change this later


    if (data.posting_date) data.posting_date = moment(data.posting_date).format("yyyy-MM-DD")
    if (data.credit_expired_date) data.credit_expired_date = moment(data.credit_expired_date).format("yyyy-MM-DD")
    
    if(!gv.cashier_shift?.name){
        isSaving.value = false;
        gv.toast('error', 'Please Open Cashier Shift.')
        return
        
    }
    isSaving.value = true;
    postApi("add_folio_transaction.create_folio_transaction", {
        data:data
    })
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
                onRateCalculation()
            }).catch(() => {
                isSaving.value = false
            })
 
    } else {
        //when user add new folio transaction'
        reservation = dialogRef.value.data.new_doc.reservation
        doc.value = dialogRef.value.data.new_doc
      
        doc.value.is_base_transaction = 1

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
<style scoped>
.h-edoor-35 {
    height: 36.5px;
}
::v-deep .top-label-style{
    display: block !important;
}
::v-deep .p-fieldset .p-fieldset-legend{
    background-color: white;
}
</style>
