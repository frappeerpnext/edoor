<template>
    <ComDialogContent @onOK="onSave" v-model:visible="visible" modal header="Edit Rate" :loading="isSaving" hideButtonClose>
       {{ use_tax }}
        Stay Number: {{ stay?.name }} <br>
        Room: {{ stay?.rooms }} <br>
        Room Type: {{ stay?.room_types }} <br>
        Guest code: {{ stay?.guest }} <br>
        Guest name: {{ stay?.guest_name }} <br>
        Business Source: {{ stay?.Business_source }} <br>
        phone: {{ stay?.guest_phone_number}} <br>
        email: {{ stay?.guest?.email }} <br>
        Pax: {{ stay?.adult }}/{{ stay?.child }}<br>
    
        <hr />

        <label>Rate</label>
        <InputNumber class="w-full" v-model="doc.input_rate" />

        <div>
            <label>Rate Type</label>
            <ComSelect v-model="doc.rate_type" doctype="Rate Type" :clear="false" />
        </div>
        <div>
            <label>Discount Type</label>
            <ComSelect v-model="doc.discount_type" :options="['Percent', 'Amount']" :clear="false" />
        </div>
        <div>
            <label>Discount</label>
            <InputNumber class="w-full" v-model="doc.discount" />
        </div>
        <div>
            <CurrencyFormat :value="discount_amount" />
        </div>
        <div>
            <label>Tax Rule</label>
            <ComSelect v-model="doc.tax_rule" doctype="Tax Rule" :clear="false" />
        </div>
        <div>
            <label>Rate Incldue Tax</label>
            <Checkbox v-model="doc.rate_include_tax" :binary="true" trueValue="Yes" falseValue="No" />
        </div>
        <div>
            <ComBoxStayInformation is-currency="true" title-class="col-6 font-medium" title="Total Befor Tax" :value="rate"
                valueClass="leading-8 col-6 bg-gray-edoor-10 pr-0 text-right flex justify-space-between" />
        </div>
        <div class="flex mt-2" v-if="doc">
            <ComBoxBetwenConten is-currency="true" title-class="col-6 font-medium"
                :title="(tax_rule.tax_1_name || '') + '-' + (tax_rule.tax_1_rate || 0) + '%'" :value="(tax_1_amount || 0)"
                valueClass="leading-8 col-6 bg-gray-edoor-10 pr-0 text-right flex justify-space-between">
                <template #prefix>
                    <div>
                        <div class="flex items-center">
                            <Checkbox v-model="use_tax.use_tax_1" @input="onUseTax1Change" :binary="true" />
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
        <div class="flex mt-2" v-if="doc">
            <ComBoxBetwenConten is-currency="true" title-class="col-6 font-medium"
                :title="(tax_rule.tax_2_name || '') + '-' + (tax_rule.tax_2_rate || 0) + '%'" :value="(tax_2_amount || 0)"
                valueClass="leading-8 col-6 bg-gray-edoor-10 pr-0 text-right flex justify-space-between">
                <template #prefix>
                    <div>
                        <div class="flex items-center">
                            <Checkbox @input="onUseTax2Change" v-model="use_tax.use_tax_2" :binary="true" />
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
        <!-- /Tax - 2 -->s
        <!-- Tax - 3 -->
        <div class="flex mt-2" v-if="doc">
            <ComBoxBetwenConten is-currency="true" title-class="col-6 font-medium"
                :title="(tax_rule.tax_3_name || '') + '-' + (tax_rule.tax_3_rate || 0) + '%'" :value="(tax_3_amount || 0)"
                valueClass="leading-8 col-6 bg-gray-edoor-10 pr-0 text-right flex justify-space-between">
                <template #prefix>
                    <div>
                        <div class="flex items-center">
                            <Checkbox @input="onUseTax3Change" v-model="use_tax.use_tax_3" :binary="true" />
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

        <div>
            <ComBoxStayInformation is-currency="true" title-class="col-6 font-medium" title="Total Tax" :value="total_tax"
                valueClass="leading-8 col-6 bg-gray-edoor-10 pr-0 text-right flex justify-space-between" />
        </div>
        <div>
            <ComBoxStayInformation is-currency="true" title-class="col-6 font-medium" title="Total" :value="total_amount"
                valueClass="leading-8 col-6 bg-gray-edoor-10 pr-0 text-right flex justify-space-between" />
        </div>
        <div>
            <Textarea class="w-full" v-model="doc.note" />
        </div>
        <hr />
        {{ doc }}

    </ComDialogContent>
</template>
<script setup>

import { ref, inject, computed, onMounted, useToast } from "@/plugin"
import Checkbox from 'primevue/checkbox';
import InputNumber from 'primevue/inputnumber';
import Textarea from 'primevue/textarea';
import ComBoxStayInformation from './ComBoxStayInformation.vue';
import ComBoxBetwenConten from './ComBoxBetwenConten.vue';

const gv = inject("$gv")
const visible = ref(false)
const frappe = inject('$frappe');
const call = frappe.call();

const dialogRef = inject("dialogRef");
const isSaving = ref(false);
const selectedRoomRates = ref([])
const use_tax = ref({})
const toast = useToast()
const stay = ref({})
const tax_rule = computed(() => {
    if (doc.value?.tax_rule_data) {
        return JSON.parse(doc.value?.tax_rule_data)
    }
    return []
})
function onUseTax1Change(value) {

    doc.value.tax_1_rate = value ? tax_rule.value.tax_1_rate : 0


}
function onUseTax2Change(value) {

    doc.value.tax_2_rate = value ? tax_rule.value.tax_2_rate : 0

}
function onUseTax3Change(value) {

    doc.value.tax_3_rate = value ? tax_rule.value.tax_3_rate : 0

}

const doc = ref({
    discount_type: 'Percent',
});

const discount_amount = computed(() => {
    if (doc.value.discount_type == "Percent") {
        return (doc.value.input_rate || 0) * (doc.value.discount / 100 || 0)
    } else {
        return (doc.value.discount || 0)
    }

});
const rate = computed(() => {
    if (tax_rule.value) {
        if (doc.value.rate_include_tax == "Yes") {
            return gv.getRateBeforeTax((doc.value.input_rate || 0) - (discount_amount.value), tax_rule.value, doc.value.tax_1_rate, doc.value.tax_2_rate, doc.value.tax_3_rate)

        } else {
            return (doc.value.input_rate || 0)
        }
    }
    return (doc.value.input_rate || 0) - discount_amount.value
})


const tax_1_amount = computed(() => {
    if (tax_rule.value) {
        doc.value.taxable_amount_1 = rate.value * ((tax_rule.value.percentage_of_price_to_calculate_tax_1 || 100) / 100);
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
        doc.value.taxable_amount_2 = rate.value * ((tax_rule.value.percentage_of_price_to_calculate_tax_2 || 100) / 100)

        if (tax_rule.value.calculate_tax_2_after_discount == 0 || doc.value.rate_include_tax == "Yes") {
            doc.value.taxable_amount_2 = doc.value.taxable_amount_2
        } else { doc.value.taxable_amount_2 = doc.value.taxable_amount_2 - discount_amount.value }

        if (tax_rule.value.calculate_tax_2_after_adding_tax_1 == 0) {
            doc.value.taxable_amount_2 = doc.value.taxable_amount_2
        } else { doc.value.taxable_amount_2 = doc.value.taxable_amount_2 + tax_1_amount.value }

        return (doc.value.taxable_amount_2 || 0) * (doc.value.tax_2_rate / 100 || 0)
    } else {
        return 0
    }
});
const tax_3_amount = computed(() => {
    if (tax_rule.value) {
        doc.value.taxable_amount_3 = rate.value * ((tax_rule.value.percentage_of_price_to_calculate_tax_3 || 100) / 100)

        if (tax_rule.value.calculate_tax_3_after_discount == 0 || doc.value.rate_include_tax == "Yes") {
            doc.value.taxable_amount_3 = doc.value.taxable_amount_3
        } else { doc.value.taxable_amount_3 = doc.value.taxable_amount_3 - discount_amount.value }

        if (tax_rule.value.calculate_tax_3_after_adding_tax_1 == 0) {
            doc.value.taxable_amount_3 = doc.value.taxable_amount_3
        } else { doc.value.taxable_amount_3 = doc.value.taxable_amount_3 + tax_1_amount.value }

        if (tax_rule.value.calculate_tax_3_after_adding_tax_2 == 0) {
            doc.value.taxable_amount_3 = doc.value.taxable_amount_3
        } else { doc.value.taxable_amount_3 = doc.value.taxable_amount_3 + tax_2_amount.value }

        return (doc.value.taxable_amount_3 || 0) * (doc.value.tax_3_rate / 100 || 0)
    } else {
        return 0
    }
});

const total_tax = computed(() => {
    return (tax_1_amount.value || 0) + (tax_2_amount.value || 0) + (tax_3_amount.value || 0)
});
const total_amount = computed(() => {
    const discount = doc.value.rate_include_tax == 'Yes' ? 0 : (discount_amount.value || 0)
    return (rate.value || 0) - discount + (total_tax.value || 0)
});


function onSave() {
    isSaving.value = true;
    call
        .post('edoor.api.reservation.update_room_rate', {
            room_rate_names: selectedRoomRates.value.map(d => d["name"]),
            data: doc.value,
        })
        .then((doc) => {
            toast.add({ severity: 'success', summary: 'Edit Room Rate', detail: "Update Success", life: 3000 })
            isSaving.value = false;
             
            dialogRef.value.close(doc.message);
        })
        .catch((error) => {
            isSaving.value = false;
            throw new Error(error.exception || error.message)
        });

}
onMounted(() => {
    stay.value = dialogRef.value.data.reservation_stay
    if (dialogRef.value.data.selected_room_rate) {
        doc.value = JSON.parse(JSON.stringify(dialogRef.value.data.selected_room_rate) ) 
    } else if (dialogRef.value.data.selected_room_rates?.length > 0) {
        selectedRoomRates.value = dialogRef.value.data.selected_room_rates
        doc.value =JSON.parse(JSON.stringify( dialogRef.value.data.selected_room_rates[0]))
    }
    use_tax.value = {
        use_tax_1:doc.value.tax_1_rate > 0,
        use_tax_3:doc.value.tax_3_rate > 0,
        use_tax_2:doc.value.tax_2_rate > 0
    }

});



</script>
