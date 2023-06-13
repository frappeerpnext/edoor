<template>
    {{ doc }}
    <Button @click="onSave"> Save</Button>
    <div class="flex mt-2 gap-2">
        <span>Ref#.</span>
        <InputText type="text" v-model="doc.reference_number" />
    </div>
    <div class="flex mt-2 gap-2">
        <span>Posting Date</span>
        <Calendar v-model="doc.posting_date" dateFormat="dd-mm-yy" showIcon showButtonBar />
    </div>
    <div class="my-2">
        <span>Amount Code</span>
        <ComAutoComplete v-model="doc.account_code" placeholder="Select Account Code" doctype="Account Code"
            class="auto__Com_Cus w-full" @onSelected="onSelectAccountCode" />
    </div>
    <div>
        <span>Rate Include Tax</span>
        <ComSelect v-model="account_code.rate_include_tax" :options="['Yes','No']" :clear="false"/>
    </div>
    <div class="flex mt-2 gap-2">
        <span>Input Amount</span>
        <InputNumber v-model="doc.input_amount" inputId="currency-us" mode="currency" currency="USD" locale="en-US" />
    </div>
    <div class="flex mt-2 gap-2">
        <span>Note</span>
        <Textarea v-model="doc.note" autoResize rows="7" cols="30" />
    </div>

        <div v-if="account_code.allow_discount">
            <span>Discount</span>
            <div class="flex mt-2 gap-2">
                <label>Discount Type</label>
                <ComSelect v-model="doc.discount_type" :options="['Percent','Amount']" :clear="false"/>
                <label>Discount</label>
                <InputNumber v-model="doc.discount" inputId="minmaxfraction" :minFractionDigits="2" :maxFractionDigits="10" />
                <label>Discount Amount: {{ discount_amount }}</label>
            </div>
        </div>
        <div v-if="account_code.allow_tax">
            <span>Tax</span>
            <div v-if="tax_rule.tax_1_rate>0">
                <div>{{ tax_rule.tax_1_name }} - {{ tax_rule.tax_1_rate }} % : {{ tax_1_amount }}</div>
                <div>{{ tax_rule.tax_2_name }} - {{ tax_rule.tax_2_rate }} % : {{ tax_2_amount }}</div>
                <div>{{ tax_rule.tax_3_name }} - {{ tax_rule.tax_3_rate }} % : {{ tax_3_amount }}</div> 
            </div>
        </div>
        <div v-if="account_code.allow_bank_fee">
            Bank Fee
        </div>
        <div>
            <span>Total : {{ total_tax }}</span>
        </div>
        <div>
            <span>Total : {{ total_amount }}</span>
        </div>

   
</template>
<script setup>
import { ref, inject,getDoc,computed,onMounted } from "@/plugin"
import Calendar from 'primevue/calendar';
import InputNumber from 'primevue/inputnumber';
import Textarea from 'primevue/textarea';


const frappe = inject('$frappe');
const db = frappe.db();
const moment = inject("$moment")
const dialogRef = inject("dialogRef");

const doc = ref({
    discount_type:"Percent"
});
const account_code = ref({
    rate_include_tax:"Yes"
});
const tax_rule = computed(()=>{
    if(account_code.value?.tax_rule){
        return JSON.parse(account_code.value.tax_rule_data)
    }else{
        return null
    }
});

const discount_amount = computed(()=>{
    if(doc.value.discount_type == "Percent"){
        return (doc.value.input_amount || 0) * (doc.value.discount/100 || 0)
    }else {
        return doc.value.discount
    }
    
});
const tax_1_amount = computed(()=>{
   return 0
    // doc.value.taxable_amount_1 = doc.value.input_amount * ((tax_rule.value.percentage_of_price_to_calculate_tax_1 || 100)/100);
    // if (tax_rule.value.calculate_tax_1_after_discount == 0 &&  account_code.value.rate_include_tax == 'Yes') {
    //     doc.value.taxable_amount_1 = doc.value.taxable_amount_1; 
    // }
    // else {doc.value.taxable_amount_1 = doc.value.taxable_amount_1 - discount_amount.value}
    // return (doc.value.taxable_amount_1 || 0) * (tax_rule.value.tax_1_rate / 100 || 0)
});
const tax_2_amount = computed(()=>{
   return 0
    // doc.value.taxable_amount_2 = doc.value.input_amount * ((tax_rule.value.percentage_of_price_to_calculate_tax_2 || 100)/100) 

    // if (tax_rule.value.calculate_tax_2_after_discount == 0 &&  account_code.value.rate_include_tax == 'Yes') {
    //     doc.value.taxable_amount_2 = doc.value.taxable_amount_2
    // }else {doc.value.taxable_amount_2 = doc.value.taxable_amount_2 - discount_amount.value} 

    // if (tax_rule.value.calculate_tax_2_after_adding_tax_1 == 0) {
    //     doc.value.taxable_amount_2 = doc.value.taxable_amount_2 
    // }else {doc.value.taxable_amount_2 = doc.value.taxable_amount_2 + tax_1_amount.value}

	// return doc.value.taxable_amount_2 * tax_rule.value.tax_2_rate / 100
});
const tax_3_amount = computed(()=>{
   return
    // doc.value.taxable_amount_3 = doc.value.input_amount * ((tax_rule.value.percentage_of_price_to_calculate_tax_3 || 100)/100)
	 
    // if (tax_rule.value.calculate_tax_3_after_discount == 0 &&  account_code.value.rate_include_tax == 'Yes') {
    //     doc.value.taxable_amount_3 = doc.value.taxable_amount_3
    // }else {doc.value.taxable_amount_3 = doc.value.taxable_amount_3 - discount_amount.value}
	  
    // if (tax_rule.value.calculate_tax_3_after_adding_tax_1 == 0) {
    //     doc.value.taxable_amount_3 = doc.value.taxable_amount_3
    // }else {doc.value.taxable_amount_3 = doc.value.taxable_amount_3 + tax_1_amount.value}
	
    // if (tax_rule.value.calculate_tax_3_after_adding_tax_2 == 0) {
    //     doc.value.taxable_amount_3 = doc.value.taxable_amount_3  
    // }else {doc.value.taxable_amount_3 = doc.value.taxable_amount_3 + tax_2_amount.value}

	// return (doc.value.taxable_amount_3 || 0) * (tax_rule.value.tax_3_rate / 100 || 0)
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
        })
        .catch((error) => {

        });

}
function onSave() {
    const data = JSON.parse(JSON.stringify(doc.value))


    if (data.posting_date) data.posting_date = moment(data.posting_date).format("yyyy-MM-DD")

    db.createDoc("Folio Transaction", { data })
        .then((doc) => {
            alert("success")
        }).catch((err) => {
            alert("error")
        })
}

onMounted(() => {



    doc.value.folio_number = dialogRef.value.data.folio_number;
 



});


</script>