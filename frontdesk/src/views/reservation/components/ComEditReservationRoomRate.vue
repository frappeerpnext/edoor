<template>
    <ComDialogContent @onOK="onSave" v-model:visible="visible" modal header="Edit Rate" :loading="isSaving" hideButtonClose>
       <div class="grid justify-between">
        <div class="col-6">
        <table>
            <tbody>
                <ComStayInfoNoBox  label="Res Stay. No" :value="stay?.name" />
                <ComStayInfoNoBox  label="Business Source" :value="stay?.business_source" />
                <ComStayInfoNoBox  label="Room" :value="stay?.room_type_alias + '/' + stay?.rooms" />
                <ComStayInfoNoBox  label="Date" :value="moment(stay?.arrival_date).format('DD-MM-yyyy')"/>
            </tbody>
        </table> 
        </div>
        <div class="col-6">
            <table>
                <tbody>
                <ComStayInfoNoBox  label="Guest" :value="stay?.guest_name +' ('+ stay?.guest+')' "/> 
                <ComStayInfoNoBox  label="Pax" :value="stay?.adult + '/' + stay?.child" />
                <ComStayInfoNoBox  label="Phone Number" :value="stay?.guest_phone_number" /> 
                </tbody>
            </table>
        </div>
    </div>
    <hr class="my-1">
    <div class="grid">  
        <div class="col-12 mt-2 -mb-3 p-0">
            <div class="grid">
                <div class="col-6">
                    <div class="flex">
                    <label for="manual_rate"  class="col-6 font-medium cursor-pointer">Use Manualy Update Rate</label>
                    <div class="inline col-6 text-left px-3">
                            <Checkbox input-id="manual_rate" class="" v-model="doc.is_manual_rate" :trueValue="1" :falseValue="0" :binary="true" @input="onUseManualRate"/>
                    </div>
                    </div>
                </div>
            </div>
        </div>
        <div class="col">
            <div class="grid">
                <div class="col-6">
                    <div>
                        <label>Rate Type</label>
                        <ComSelect class="w-full" v-model="doc.rate_type" doctype="Rate Type" @onSelected="onSelectRateType" :clear="false"/>
                    </div>
                </div> 
                <div class="col-6">
                    <label>Room Rate</label>                
                        <ComInputCurrency classCss="w-full" v-model="doc.input_rate" :disabled="doc.is_manual_rate==0"/>
                </div>
                <div class="col-4">
                        <label>Discount Type</label>
                        <ComSelect class="w-full min-w-full" v-model="doc.discount_type" :options="['Percent', 'Amount']" :clear="false" />
                </div>
                <div class="col-4">
                        <label>Discount</label>
                        <InputNumber class="w-full" :input-class="'w-full'" v-model="doc.discount" :minFractionDigits="2" :maxFractionDigits="10"/>
                </div>
                <div class="col-4 text-right">
                        <label >Amount Discount</label>
                        <div class="w-full rounded-lg max-h-3rem h-edoor-35 leading-8 bg-gray-edoor-10 justify-end flex items-center px-3">
                        <CurrencyFormat  :value="discount_amount" />
                        </div>
                </div>

            <div class="col-12 text-right" v-if="tax_rule.tax_1_rate > 0 && tax_rule.tax_2_rate > 0 && tax_rule.tax_3_rate > 0">
                <div class="grid justify-end">
                    <div class="col-4">
                        <label>Rate Befor Tax</label>
                        <div class="w-full rounded-lg max-h-3rem h-edoor-35 leading-8 bg-gray-edoor-10 justify-end flex items-center px-3">
                        <CurrencyFormat  :value="rate" />
                    </div>
                    </div>
                </div>
            </div>
            <div class="col-12">
                <Textarea placeholder="Note" class="w-full" v-model="doc.note" />
            </div>
            
            <div class="col-12" v-if="showCheckUpdateFutureStayRoomRate">
                <Checkbox class="" v-model="updateFutureRoomRate"   :binary="true" /> 
                Update room rate to the future stay room rate ({{ futureRoomRates?.length-1 }} Room Night(s))
            </div>

            </div>
        </div>
        <div class="col-5">
            <div class="grid justify-end ">
                <div class="col-12">
            <div class="flex justify-end text-end" v-if="tax_rule.tax_1_rate > 0 && tax_rule.tax_2_rate > 0 && tax_rule.tax_3_rate > 0">
                <label for="rate_tax"  class="col-6 font-medium cursor-pointer">Rate Incldue Tax</label>
                <div class="inline col-6 text-left px-3">
                <Checkbox input-id="rate_tax" class="" v-model="doc.rate_include_tax" :binary="true" trueValue="Yes" falseValue="No" />
                </div>
            </div>   
            <div class="flex mt-2" v-if="tax_rule && tax_rule.tax_1_rate > 0">
                <ComBoxBetwenConten inputIdFor="tax-1" is-currency="true" title-class="col-6 font-medium"
                    :title="(tax_rule.tax_1_name || '') + ' ' + (tax_rule.tax_1_rate || 0) + '%'" :value="(tax_1_amount || 0)">
                    <template #prefix>
                        <div>
                            <div class="flex items-center">
                                <Checkbox input-id="tax-1" v-model="use_tax.use_tax_1" @input="onUseTax1Change" :binary="true" />
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
                    :title="(tax_rule.tax_2_name || '') + ' ' + (tax_rule.tax_2_rate || 0) + '%'" :value="(tax_2_amount || 0)"
                   >
                    <template #prefix>
                        <div>
                            <div class="flex items-center">
                                <Checkbox input-id="tax-2" @input="onUseTax2Change" v-model="use_tax.use_tax_2" :binary="true" />
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
                    :title="(tax_rule.tax_3_name || '') + ' ' + (tax_rule.tax_3_rate || 0) + '%'" :value="(tax_3_amount || 0)"
                    valueClass="">
                    <template #prefix>
                        <div>
                            <div class="flex items-center">
                                <Checkbox input-id="tax-3" @input="onUseTax3Change" v-model="use_tax.use_tax_3" :binary="true" />
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
                <div class="flex mt-2" v-if="tax_rule.tax_1_rate > 0 && tax_rule.tax_2_rate > 0 && tax_rule.tax_3_rate > 0">
                    <ComBoxStayInformation is-currency="true" title-class="col-6 m-auto font-medium" title="Total Tax" :value="total_tax"
                        valueClass="leading-8 max-h-3rem col-6 bg-gray-edoor-10 text-right" />
                </div>
                <div class="flex mt-2">
                    <ComBoxStayInformation is-currency="true" title-class="col-6 m-auto font-medium" title="Total" :value="total_amount"
                        valueClass="leading-8 max-h-3rem col-6 bg-gray-edoor-10 text-right" />
                </div>
                 </div>
            </div>
        </div>
       
        <hr />
      
    </div> 

    </ComDialogContent>
</template>
<script setup>
import { ref, inject, computed, onMounted, useToast, getDoc ,postApi} from "@/plugin"
import Checkbox from 'primevue/checkbox';
import InputNumber from 'primevue/inputnumber';
import Textarea from 'primevue/textarea';
import ComBoxStayInformation from './ComBoxStayInformation.vue';
import ComBoxBetwenConten from './ComBoxBetwenConten.vue';
import ComReservationStayPanel from '@/views/reservation/components/ComReservationStayPanel.vue';
 
const socket = inject("$socket")
const gv = inject("$gv")
const visible = ref(false)
 
const dialogRef = inject("dialogRef");
const moment = inject("$moment")
const isSaving = ref(false);
const selectedRoomRates = ref([])
const use_tax = ref({})
const toast = useToast()
const stay = ref({})
const rate_plan = ref({})
const room_types = ref([])
const showCheckUpdateFutureStayRoomRate = ref(false)
const updateFutureRoomRate = ref(false)
const futureRoomRates = ref([])
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
        }else{
            
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


function onSelectRateType(selected){
    if(doc.value.is_manual_rate == 0 && selected.value){
        postApi('reservation.get_room_rate',{
                property: doc.value.property,
                rate_type: selected.value,
                room_type: doc.value.room_type_id, 
                business_source: doc.value.business_source, 
                date: doc.value.date
            })
            .then((result) => {
               
                doc.value.input_rate = result.message
            })
     }    
    
  
}
function onUseManualRate(){
    if(doc.value.is_manual_rate == 0){
        postApi('reservation.get_room_rate',{
                property: doc.value.property,
                rate_type: doc.value.rate_type,
                room_type: doc.value.room_type_id, 
                business_source: doc.value.business_source, 
                date: doc.value.date
            },"", false)
            .then((result) => {
                doc.value.input_rate = result.message
            })
    }    
    
  
}

function onSave() {
  
    //prepare room rate name send to api
    let room_rate_names = []
    let reservation_stay_names = []
    
    if (futureRoomRates.value && futureRoomRates.value.length>0) 
    {
 
        if(updateFutureRoomRate.value==true){
            room_rate_names =  futureRoomRates.value.map(d => d["name"])
            reservation_stay_names = Array.from(new Set( futureRoomRates.value.map(d => d["reservation_stay"])))
        }
        
    }else {
        room_rate_names =  selectedRoomRates.value.map(d => d["name"])
        reservation_stay_names = Array.from(new Set( selectedRoomRates.value.map(d => d["reservation_stay"])))
    }

  
    isSaving.value = true;
    postApi('reservation.update_room_rate', {
            room_rate_names: room_rate_names,
            data: doc.value,
            reservation_stays: reservation_stay_names
        },"Edit room rate successfully")
        .then((doc) => {
            
            isSaving.value = false;
            
            socket.emit("RefreshNightAuditStep", JSON.parse(localStorage.getItem("edoor_property")).name);

            dialogRef.value.close(doc.message);
        })
        .catch((error) => {
            isSaving.value = false;
            
        });

}
onMounted(() => {
    stay.value = dialogRef.value.data.reservation_stay
    
    
    showCheckUpdateFutureStayRoomRate.value = dialogRef.value.data.show_check_update_future_stay_room_rate
     
    if (dialogRef.value.data.selected_room_rate) {
        doc.value = JSON.parse(JSON.stringify(dialogRef.value.data.selected_room_rate)) 
        //this condition below is true only if user edit rate from run night audit
   
     
        futureRoomRates.value = dialogRef.value.data.future_room_rates;

        
        
    } else if (dialogRef.value.data.selected_room_rates?.length > 0) {
        selectedRoomRates.value = dialogRef.value.data.selected_room_rates
        doc.value = JSON.parse(JSON.stringify(dialogRef.value.data.selected_room_rates[0]))
    
    }

    use_tax.value = {
        use_tax_1:doc.value.tax_1_rate > 0,
        use_tax_3:doc.value.tax_3_rate > 0,
        use_tax_2:doc.value.tax_2_rate > 0
    }

});



</script>
<style scoped>
.h-edoor-35{
    height: 36.5px;
}
</style>
