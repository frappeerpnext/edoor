<template>
    {{ doc }}{{ tax_rule }}
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
        </div>
    </div>
    <div v-if="account_code.allow_tax">
        <div v-if="tax_rule.tax_1_rate>0">
            {{ tax_rule.tax_1_name }} - {{ tax_rule.tax_1_rate }} %
        </div>
    </div>
    <div v-if="account_code.allow_bank_fee">
        Bank Fee
    </div>


    <Button @click="onSave"> Save</Button>
</template>
<script setup>
import { ref, inject,getDoc,computed } from "@/plugin"
import Calendar from 'primevue/calendar';
import InputNumber from 'primevue/inputnumber';
import Textarea from 'primevue/textarea';


const frappe = inject('$frappe');
const db = frappe.db();
const moment = inject("$moment")


const doc = ref({
    discount_type:"Percent"
});
const account_code = ref({})
const tax_rule = computed(()=>{
    if(account_code.value?.tax_rule){
        return JSON.parse(account_code.value.tax_rule_data)
    }else{
        return null
    }
})

function onSelectAccountCode(data) {
    getDoc('Account Code', data.value)
        .then((d) => account_code.value = d)
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

</script>