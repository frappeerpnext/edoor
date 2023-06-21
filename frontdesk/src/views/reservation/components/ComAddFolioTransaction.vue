<template>
     <ComDialogContent @onOK="onSave" :loading="isSaving" hideButtonClose> 
    <div class="grid">
       {{doc}}
     
        <div class="col-12 md:col-6">
            <label for="ref">Ref#.</label>
            <InputText id="ref" class="w-full" type="text" v-model="doc.reference_number" />
        </div>
        <div class="col-12 md:col-6">
            <label for="posting_date">Posting Date</label>
            <Calendar v-model="doc.posting_date" :minDate="min_date" :maxDate="moment(working_day?.date_working_day).toDate()" class="w-full" dateFormat="dd-mm-yy" showIcon showButtonBar />
        </div>
        <div class="col-12 md:col-6">
            <label for="posting_date">Amount Code</label>
            <ComAutoComplete v-model="doc.account_code" placeholder="Select Account Code" doctype="Account Code"
            class="auto__Com_Cus w-full" @onSelected="onSelectAccountCode" :filters="{'account_group':account_group}" />

            {{ doc.account_name }}
        </div>
        <div class="col-12 md:col-6">
            <label for="input_amount">Input Amount</label>
            <InputNumber class="w-full" id="input_amount" v-model="doc.input_amount" ref="input_amount" inputId="currency-us" mode="currency" currency="USD" locale="en-US" />
        </div>
        <div class="col-12">
            <div v-if="account_code.allow_discount">
                <span class="text-lg font-semibold">Discount</span>
                <div class="grid">
                    <div class="col-6">
                        <label for="dis_type">Discount Type</label>
                        <ComSelect class="w-full" id="dis_type" v-model="doc.discount_type" :options="['Percent','Amount']" :clear="false"/>
                    </div>
                    <div class="col-6">
                        <label>Discount</label>
                        <InputNumber class="w-full" v-model="doc.discount" inputId="minmaxfraction" :minFractionDigits="2" :maxFractionDigits="10" />
                    </div>
                </div>
                <div class="flex justify-end">
                    <ComBoxStayInformation is-currency="true" title-class="col-2 " title="Discount Amount" :value="discount_amount"
                                valueClass="max-h-3rem h-3rem leading-8 col-2 bg-gray-edoor-10 pr-0 text-right"/>
                </div>
            </div>
            <!-- tax -->
            <div v-if="account_code.allow_discount">
                <span class="text-lg font-semibold">Tax</span>
                <div class="grid">
                    <div class="col-6">
                        <label>Rate Include Tax</label>
                        <ComSelect class="w-full" v-model="doc.rate_include_tax" :options="['Yes','No']" :clear="false"/>
                    </div>
                </div>
                <div  v-if="tax_rule && tax_rule.tax_1_rate>0" class="flex justify-end mt-2">
                    <ComBoxStayInformation is-currency="true" title-class="col-2 " :title="tax_rule.tax_1_name + '-' + tax_rule.tax_1_rate + '%'" :value="tax_1_amount"
                    valueClass="max-h-3rem h-3rem leading-8 col-2 bg-gray-edoor-10 pr-0 text-right"/>
                </div>
                <div  v-if="tax_rule && tax_rule.tax_2_rate>0" class="flex justify-end mt-2">
                    <ComBoxStayInformation is-currency="true" title-class="col-2 " :title="tax_rule.tax_2_name + '-' + tax_rule.tax_2_rate + '%'" :value="tax_2_amount"
                    valueClass="max-h-3rem h-3rem leading-8 col-2 bg-gray-edoor-10 pr-0 text-right"/>
                </div>
                <div  v-if="tax_rule && tax_rule.tax_3_rate>0" class="flex justify-end mt-2">
                    <ComBoxStayInformation is-currency="true" title-class="col-2 " :title="tax_rule.tax_3_name + '-' + tax_rule.tax_3_rate + '%'" :value="tax_3_amount"
                    valueClass="max-h-3rem h-3rem leading-8 col-2 bg-gray-edoor-10 pr-0 text-right"/>
                </div>
                <div  v-if="tax_rule && ( tax_rule.tax_1_rate + tax_rule.tax_2_rate + tax_rule.tax_3_rate>0)" class="flex justify-end mt-2">
                    <ComBoxStayInformation is-currency="true" title-class="col-2 " title="Total Tax" :value="total_tax"
                    valueClass="max-h-3rem h-3rem leading-8 col-2 bg-gray-edoor-10 pr-0 text-right"/>
                </div>
            </div>
            <div v-if="account_code.allow_bank_fee" class="flex justify-end mt-2">
                Bank Fee
            </div>
            <div class="flex justify-end mt-2">
            <ComBoxStayInformation is-currency="true" title-class="col-2 " title="Total" :value="total_amount"
                        valueClass="max-h-3rem h-3rem leading-8 col-2 bg-gray-edoor-10 pr-0 text-right"/>
            </div>
        </div>
        
        <div  v-if="doc.require_city_ledger_account==1" >
            <ComAutoComplete v-model="doc.city_ledger" placeholder="Select City Ledger Account" doctype="City Ledger"
            class="auto__Com_Cus w-full"    />
        </div>
        
        <div class="col-12">
            <label for="Note">Note</label>
            <Textarea class="w-full" v-model="doc.note" autoResize rows="5" />
        </div>
    </div>
    </ComDialogContent>
</template>
<script setup>

import { ref, inject,getDoc,computed,onMounted,nextTick } from "@/plugin"
import Calendar from 'primevue/calendar';
import InputNumber from 'primevue/inputnumber';
import Textarea from 'primevue/textarea';
import ComBoxStayInformation from './ComBoxStayInformation.vue';

const gv = inject("$gv")
const frappe = inject('$frappe');
const db = frappe.db();
const call = frappe.call()

const moment = inject("$moment")
const dialogRef = inject("dialogRef");
const isSaving = ref(false)
const account_group = ref("")
const account_code = ref({});
const balance = ref(0);
const working_day =JSON.parse( localStorage.getItem("edoor_working_day"))
const edoor_setting =JSON.parse( localStorage.getItem("edoor_setting"))
const current_user =JSON.parse( localStorage.getItem("edoor_user"))
 
const tax_rule = computed(()=>{
    if(account_code.value?.tax_rule){
        return JSON.parse(account_code.value.tax_rule_data)
    }else{
        return null
    }
});
const doc = ref({
    discount_type:"Percent",
    quantity:1,
    tax_1_rate:tax_rule.tax_1_rate,
     
});

const min_date = computed(()=>{
    if(edoor_setting?.allow_user_to_add_back_date_transaction==0){
        return moment(working_day?.date_working_day).toDate()
    }else{
        const permit_role = edoor_setting?.role_for_back_date_transaction
        if( current_user?.roles.includes(permit_role)){
            return moment().subtract(100,"years").toDate()
        }else{
            return  moment(working_day?.date_working_day).toDate()
        }
        
    }
 
});


const discount_amount = computed(()=>{
    if(doc.value.discount_type == "Percent"){
        return (doc.value.input_amount || 0) * (doc.value.discount/100 || 0)
    }else {
        return (doc.value.discount || 0)
    }
    
});

const tax_1_amount = computed(()=>{
    if (tax_rule.value){ 
        doc.value.taxable_amount_1 = doc.value.input_amount * ((tax_rule.value.percentage_of_price_to_calculate_tax_1 || 100)/100);
	 
        if (tax_rule.value.calculate_tax_1_after_discount == 0 &&  doc.value.rate_include_tax=="Yes") {
            doc.value.taxable_amount_1 = doc.value.taxable_amount_1
        }else {
            doc.value.taxable_amount_1 = doc.value.taxable_amount_1 - discount_amount.value
        }
    return (doc.value.taxable_amount_1 || 0) * (doc.value.tax_1_rate / 100 || 0)
}else {
    return 0
}
});
const tax_2_amount = computed(()=>{
    if(tax_rule.value){
        doc.value.taxable_amount_2 = doc.value.input_amount * ((tax_rule.value.percentage_of_price_to_calculate_tax_2 || 100)/100) 

        if (tax_rule.value.calculate_tax_2_after_discount == 0 &&  doc.value.rate_include_tax=="Yes") {
            doc.value.taxable_amount_2 = doc.value.taxable_amount_2
        }else {doc.value.taxable_amount_2 = doc.value.taxable_amount_2 - discount_amount.value} 

        if (tax_rule.value.calculate_tax_2_after_adding_tax_1 == 0) {
            doc.value.taxable_amount_2 = doc.value.taxable_amount_2 
        }else {doc.value.taxable_amount_2 = doc.value.taxable_amount_2 + tax_1_amount.value}

    return (doc.value.taxable_amount_2 || 0) * (doc.value.tax_2_rate / 100 || 0)
    }else{
        return 0
    }
});
const tax_3_amount = computed(()=>{
    if(tax_rule.value){
        doc.value.taxable_amount_3 = doc.value.input_amount * ((tax_rule.value.percentage_of_price_to_calculate_tax_3 || 100)/100)
	 
        if (tax_rule.value.calculate_tax_3_after_discount == 0 &&  doc.value.rate_include_tax=="Yes") {
            doc.value.taxable_amount_3 = doc.value.taxable_amount_3
        }else {doc.value.taxable_amount_3 = doc.value.taxable_amount_3 - discount_amount.value}
        
        if (tax_rule.value.calculate_tax_3_after_adding_tax_1 == 0) {
            doc.value.taxable_amount_3 = doc.value.taxable_amount_3
        }else {doc.value.taxable_amount_3 = doc.value.taxable_amount_3 + tax_1_amount.value}
        
        if (tax_rule.value.calculate_tax_3_after_adding_tax_2 == 0) {
            doc.value.taxable_amount_3 = doc.value.taxable_amount_3  
        }else {doc.value.taxable_amount_3 = doc.value.taxable_amount_3 + tax_2_amount.value}

	return (doc.value.taxable_amount_3 || 0) * (doc.value.tax_3_rate / 100 || 0)
    }else{
        return 0
    }
});
const bank_fee_amount = computed(()=>{
    return  (doc.value.input_amount || 0) * (account_code.value.bank_fee / 100 || 0)
})
const total_tax = computed(()=>{
    return  (tax_1_amount.value || 0 ) + (tax_2_amount.value || 0 ) + (tax_3_amount.value || 0 ) 
});
const total_amount = computed(()=>{
    return  (doc.value.input_amount || 0) - (discount_amount.value || 0) + (total_tax.value || 0) + (bank_fee_amount.value || 0)
});

function onSelectAccountCode(data) {
    getDoc('Account Code', data.value)
        .then((d) =>{ 
             account_code.value = d
             doc.value.rate_include_tax = d.rate_include_tax
             doc.value.bank_fee = (d.bank_fee || 0)
             doc.value.require_city_ledger_account =d.require_city_ledger_account
             doc.value.account_name = d.account_name
             doc.value.type = d.type
             if (d.tax_rule){
                const tax_rule =  JSON.parse(account_code.value.tax_rule_data)
                if(tax_rule){ 
                    doc.tax_1_rate = tax_rule.tax_1_rate
                    doc.tax_2_rate = tax_rule.tax_2_rate
                    doc.tax_3_rate = tax_rule.tax_3_rate
                }
                
             }
             if (d.use_folio_balance_as_default_amount==1){
                doc.value.input_amount = balance.value
             }
             

        })
        .catch((error) => {

        });

}
function onSave() {
    isSaving.value = true
    const data = JSON.parse(JSON.stringify(doc.value))
    if (data.posting_date) data.posting_date = moment(data.posting_date).format("yyyy-MM-DD")
    if(data.name){
        db.updateDoc("Folio Transaction",data.name, { data })
        .then((doc) => {
            isSaving.value = false;
            dialogRef.value.close(doc);
            
        }).catch((err) => {
            gv.showErrorMessage(err)
            isSaving.value = false;
        })
    }else{
        db.createDoc("Folio Transaction", { data })
        .then((doc) => {
            isSaving.value = false;
            dialogRef.value.close(doc);
            
        }).catch((err) => {
            gv.showErrorMessage(err)
            isSaving.value = false;
        })
    }
    
}

onMounted(() => {

    doc.value.folio_number = dialogRef.value.data.folio_number;
    account_group.value = dialogRef.value.data.account_group
    balance.value = dialogRef.value.data.balance
    if(dialogRef.value.data.folio_transaction_number){
       call.get("edoor.api.reservation.get_folio_detail",{
        name:dialogRef.value.data.folio_transaction_number
    })
       .then((result)=>{
        doc.value = result.message.doc
        account_code.value = result.message.account_code
       })
    }else{
       
        doc.value.posting_date =  moment(working_day.date_working_day).toDate();
    }


});


</script>
